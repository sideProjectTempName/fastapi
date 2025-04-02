from typing import List, Dict, Optional
import logging
from app.utils.distance import haversine
from app.utils.clustering import optimize_schedule
from app.core.database import get_db_cursor
from app.core.config import settings
from app.api.v1.schemas.recommendations import TravelSpot, Accommodation, TravelStyle
from app.db.queries import get_tourist_spots_query, get_accommodations_query

logger = logging.getLogger(__name__)

class TourAPIRecommender:
    def get_travel_recommendations(
        self,
        area_code: str,
        sigungu_code: Optional[str],
        category_codes: List[str],
        days: int
    ) -> Dict:
        """
        여행 일정 추천 API
        
        Args:
            area_code: 지역 코드 (예: 32-강원도)
            sigungu_code: 시군구 코드 (예: 1-강릉시)
            category_codes: 카테고리 코드 목록 (예: ['A01', 'A05', 'A02'])
            days: 여행 일수
            
        Returns:
            Dict: 일자별 추천 여행지 및 숙박시설
        """
        cursor = get_db_cursor()
        
        try:
            # 1. 관광지와 음식점 데이터 가져오기
            # 시군구 코드가 None이면 전체 지역을 대상으로 함
            include_sigungu = sigungu_code is not None
            if not category_codes or len(category_codes) < 2:
                raise ValueError("카테고리 코드를 두 개 이상 지정해주세요.")
                
            # 카테고리 코드 패턴 생성
            category_patterns = [f"{code}%" for code in category_codes]
            logger.info(f"Category patterns: {category_patterns}") 
            
            # 데이터 가져오기
            tourist_spots_query = get_tourist_spots_query(category_patterns,include_sigungu)
            query_params = [area_code]
            if include_sigungu:
                query_params.append(sigungu_code)
            query_params += category_patterns
            logger.info(f"Query: {tourist_spots_query}")
            logger.info(f"Query parameters: {query_params}") 
            cursor.execute(tourist_spots_query, query_params)
            spots = cursor.fetchall()
            
            logger.info(f"Query returned {len(spots)} spots.")
            if not spots:
                logger.error("No data returned from the query.")
                raise ValueError("해당 지역에서 추천할 여행지를 찾을 수 없습니다.")
            else:
                logger.info(f"Query returned {len(spots)} spots.")

            # 2. 데이터 전처리
            restaurants = []
            tourist_spots = []
            
            for spot in spots:
                try:
                    spot_data = TravelSpot(
                        destination_id=str(spot["destination_id"]),
                        name=spot["name"],
                        addr1=spot["addr1"] or "",
                        addr2=spot["addr2"],
                        latitude=float(spot["latitude"]),
                        longitude=float(spot["longitude"]),
                        content_id=str(spot["content_id"]),
                        category_code=str(spot["category_code"]),
                        category_name=spot["category_name"],
                        type=spot["type"]
                    )
                    
                    if spot_data.type == "restaurant":
                        restaurants.append(spot_data)
                    else:
                        tourist_spots.append(spot_data)
                        
                except (ValueError, TypeError) as e:
                    logger.error(f"Error processing spot: {spot}, Error: {str(e)}")
                    continue

            # 3. 클러스터링 기반 일정 최적화
            try:
                max_restaurants_per_day = settings.MAX_RESTAURANTS_PER_DAY
                
                schedule = optimize_schedule(tourist_spots + restaurants, days) or {}
                
            except Exception as e:
                logger.error(f"일정 최적화 중 오류 발생: {str(e)}")
                schedule = {}
                spots_per_day = len(tourist_spots) // days if days > 0 else 0
                selected_restaurants = restaurants[:max_restaurants_per_day * days]  # Select a subset of restaurants
                for day in range(1, days + 1):
                    day_spots = []
                    start_idx = (day - 1) * spots_per_day
                    end_idx = start_idx + spots_per_day if day < days else len(tourist_spots)
                    day_spots.extend(tourist_spots[start_idx:end_idx])
                    
                    start_idx = (day - 1) * max_restaurants_per_day
                    end_idx = start_idx + max_restaurants_per_day
                    day_spots.extend(selected_restaurants[start_idx:end_idx])
                    
                    schedule[f"day_{day}"] = day_spots

            # 4. 숙소 추천
            accommodations = {}
            for day in range(1, days):
                day_spots = schedule.get(f"day_{day}", [])
                if not day_spots:
                    continue

                center_lat = sum(spot.latitude for spot in day_spots) / len(day_spots)
                center_lon = sum(spot.longitude for spot in day_spots) / len(day_spots)

                accommodation_query = get_accommodations_query()
                cursor.execute(accommodation_query, [area_code, sigungu_code])
                accommodation_results = cursor.fetchall()
                
                if accommodation_results:
                    day_accommodations = []
                    for acc in accommodation_results:
                        try:
                            accommodation = Accommodation(
                                destination_id=str(acc["destination_id"]),
                                name=acc["name"],
                                addr1=acc["addr1"] or "",
                                addr2=acc["addr2"],
                                content_id=str(acc["content_id"]),
                                latitude=float(acc["latitude"]),
                                longitude=float(acc["longitude"])
                            )
                            day_accommodations.append(accommodation)
                        except (ValueError, TypeError) as e:
                            logger.error(f"Error processing accommodation: {acc}, Error: {str(e)}")
                            continue
                    
                    if day_accommodations:
                        selected_accommodation = min(
                            day_accommodations,
                            key=lambda acc: haversine(
                                center_lat,
                                center_lon,
                                float(acc.latitude),
                                float(acc.longitude)
                            )
                        )
                        accommodations[f"day_{day}"] = selected_accommodation

            # 5. 최종 일정 구성
            final_schedule = {}
            for day in range(1, days + 1):
                day_key = f"day_{day}"
                final_schedule[day_key] = {
                    "spots": schedule.get(day_key, []),
                    "accommodation": accommodations.get(day_key)
                }

            return {
                "schedule": final_schedule,
                "message": "여행 일정이 성공적으로 생성되었습니다.",
                "area_code": area_code
            }

        except Exception as e:
            logger.error(f"여행 추천 중 오류 발생: {str(e)}", exc_info=True)
            raise
        finally:
            cursor.close()

    def get_category_hierarchy(self, category_code: str) -> List[Dict]:
        """
        카테고리 계층 구조를 조회합니다.
        
        Args:
            category_code: 카테고리 코드
            
        Returns:
            List[Dict]: 카테고리 정보 목록
        """
        cursor = get_db_cursor()
        
        try:
            query = """
                WITH RECURSIVE category_tree AS (
                    -- Base case: 시작 카테고리
                    SELECT 
                        c.category_id,
                        c.category_code,
                        c.name,
                        c.parent_id,
                        NULL::VARCHAR AS parent_code,
                        1 AS level
                    FROM category c
                    WHERE c.category_code = %s
                    
                    UNION ALL
                    
                    -- Recursive case: 하위 카테고리
                    SELECT 
                        c.category_id,
                        c.category_code,
                        c.name,
                        c.parent_id,
                        p.category_code AS parent_code,  -- 부모 카테고리의 category_code 조회
                        ct.level + 1
                    FROM category c
                    INNER JOIN category_tree ct ON c.parent_id = ct.category_id
                    LEFT JOIN category p ON c.parent_id = p.category_id  -- 부모 카테고리 조회
                )
                SELECT 
                    category_code,
                    name,
                    parent_code,
                    level
                FROM category_tree
                ORDER BY level;
            """
            
            cursor.execute(query, (category_code,))
            categories = cursor.fetchall()
            
            return [{
                "category_code": cat["category_code"],
                "category_name": cat["name"],
                "parent_code": cat["parent_code"] if cat["parent_code"] else None,
                "level": cat["level"],  # level 필드 추가
            } for cat in categories]
            
        except Exception as e:
            logger.error(f"카테고리 조회 중 오류 발생: {str(e)}")
            return []
            
        finally:
            cursor.close()