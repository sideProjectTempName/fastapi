from fastapi import APIRouter, HTTPException
from app.api.v1.schemas.recommendations import (
    TravelRecommendationRequest,
    TravelSchedule,
    CategoryHierarchy
)
from app.services.recommender import TourAPIRecommender

router = APIRouter()
recommender = TourAPIRecommender()

@router.post("/", response_model=TravelSchedule)
async def get_travel_recommendations(request: TravelRecommendationRequest):
    """
    여행 일정 추천 API
    
    Args:
        request: 여행 추천 요청 데이터
        
    Returns:
        TravelSchedule: 일자별 추천 여행지 및 숙박시설
    """
    try:
        return recommender.get_travel_recommendations(
            area_code=request.area_code,
            sigungu_code=request.sigungu_code,
            category_codes=request.category_codes,
            days=request.days,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories/{category_code}", response_model=list[CategoryHierarchy])
async def get_category_hierarchy(category_code: str):
    """
    카테고리 계층 구조 조회 API
    
    Args:
        category_code: 카테고리 코드
        
    Returns:
        List[CategoryHierarchy]: 카테고리 계층 구조
    """
    try:
        return recommender.get_category_hierarchy(category_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 