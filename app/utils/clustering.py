from typing import List, Dict
import numpy as np
from sklearn.cluster import KMeans
from app.api.v1.schemas.recommendations import TravelSpot
from app.utils.distance import haversine
from app.core.config import settings

def optimize_schedule(spots: List[TravelSpot], days: int) -> Dict[str, List[TravelSpot]]:
    """
    여행지를 클러스터링하여 일자별 일정을 최적화합니다.
    
    Args:
        spots: 여행지 목록
        days: 여행 일수
        
    Returns:
        Dict[str, List[TravelSpot]]: 일자별 여행지 목록
    """
    if not spots:
        return {}
        
    # 관광지와 식당 분리
    tourist_spots = [spot for spot in spots if spot.type != "restaurant"]
    restaurants = [spot for spot in spots if spot.type == "restaurant"]
    
    # 위도, 경도 데이터 준비 (관광지 기준으로 클러스터링)
    X = np.array([[spot.latitude, spot.longitude] for spot in tourist_spots])
    
    # K-means 클러스터링 수행
    kmeans = KMeans(n_clusters=days, random_state=42)
    clusters = kmeans.fit_predict(X)
    centroids = kmeans.cluster_centers_  # 클러스터 중심 좌표
    
    # 클러스터별 여행지 그룹화
    schedule = {f"day_{day}": [] for day in range(1, days + 1)}
    cluster_spots = {day: [] for day in range(days)}
    for i, spot in enumerate(tourist_spots):
        cluster_spots[clusters[i]].append(spot)
    
    # 식당을 클러스터 중심과 매칭
    for restaurant in restaurants:
        closest_cluster = min(
            range(days),
            key=lambda cluster_idx: haversine(
                centroids[cluster_idx][0], centroids[cluster_idx][1],
                restaurant.latitude, restaurant.longitude
            )
        )
        cluster_spots[closest_cluster].append(restaurant)
    
    # 클러스터별 일정 생성
    for day in range(1, days + 1):
        day_spots = cluster_spots[day - 1]
        
        # 관광지와 식당 분리
        day_tourist_spots = [spot for spot in day_spots if spot.type != "restaurant"]
        day_restaurants = [spot for spot in day_spots if spot.type == "restaurant"]
        
        # 관광지 개수 제한 (3~5개)
        max_spots_per_day = 5
        min_spots_per_day = 3
        spots_count = min(max_spots_per_day, max(min_spots_per_day, len(day_tourist_spots)))
        day_tourist_spots = day_tourist_spots[:spots_count]
        
        # 식당 개수 제한 (최대 2개)
        max_restaurants_per_day = 2
        day_restaurants = day_restaurants[:max_restaurants_per_day]
        
        # 관광지와 식당 순서 최적화
        optimized_tourist_spots = optimize_cluster_order(day_tourist_spots)
        optimized_restaurants = optimize_cluster_order(day_restaurants)
        
        # 관광지와 식당 번갈아 배치
        day_schedule = []
        while optimized_tourist_spots or optimized_restaurants:
            if optimized_tourist_spots:
                day_schedule.append(optimized_tourist_spots.pop(0))
            if optimized_restaurants:
                day_schedule.append(optimized_restaurants.pop(0))
        
        schedule[f"day_{day}"] = day_schedule
        
    return schedule

def optimize_cluster_order(spots: List[TravelSpot]) -> List[TravelSpot]:
    """
    클러스터 내 여행지들의 방문 순서를 최적화합니다.
    
    Args:
        spots: 여행지 목록
        
    Returns:
        List[TravelSpot]: 최적화된 순서의 여행지 목록
    """
    if not spots:
        return []
        
    # 시작점 선택 (첫 번째 여행지)
    current = spots[0]
    remaining = spots[1:]
    optimized = [current]
    
    # 가장 가까운 여행지부터 방문
    while remaining:
        next_spot = min(
            remaining,
            key=lambda x: haversine(
                current.latitude, current.longitude,
                x.latitude, x.longitude
            )
        )
        optimized.append(next_spot)
        remaining.remove(next_spot)
        current = next_spot
        
    return optimized