from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class TravelStyle(str, Enum):
    HEALING = "healing"
    CULTURE = "culture"
    NATURE = "nature"
    FOOD = "food"
    SHOPPING = "shopping"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            return cls(value.lower())
        return None

class TravelSpot(BaseModel):
    destination_id: str
    name: str
    addr1: str
    addr2: Optional[str] = None
    latitude: float
    longitude: float
    content_id: Optional[str] = None
    category_code: str
    category_name: str
    type: str

class Accommodation(BaseModel):
    destination_id: str
    name: str
    addr1: str
    addr2: Optional[str] = None
    latitude: float
    longitude: float
    content_id: Optional[str] = None

class DailySchedule(BaseModel):
    spots: List[TravelSpot]
    accommodation: Optional[Accommodation] = None

class TravelSchedule(BaseModel):
    schedule: dict[str, DailySchedule]
    message: str
    area_code: str

class CategoryHierarchy(BaseModel):
    category_code: str
    category_name: str
    parent_code: Optional[str] = None
    level: int

class TravelRecommendationRequest(BaseModel):
    area_code: str = Field(..., description="지역 코드 (예: 32)")
    sigungu_code: Optional[str] = Field(None, description="시군구 코드 (예: 강남구-1, 전체-None)gi")
    category_codes: List[str] = Field(..., description="카테고리 코드 목록 (예: ['A01', 'A05'])")
    days: int = Field(..., ge=1, le=7, description="여행 일수 (1-7일)")
    