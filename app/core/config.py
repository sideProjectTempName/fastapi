from typing import List
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn
from dotenv import load_dotenv
import os
from pathlib import Path
from typing import Optional

# .env 파일 로드
load_dotenv()

class Settings(BaseSettings):
    # API 설정
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Travel AI API"
    DESCRIPTION: str = "여행 추천 AI API"
    VERSION: str = "1.0.0"
    
    # CORS 설정
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # 데이터베이스 설정
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_NAME: str = os.getenv("DB_NAME", "travelai_db")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DIR: str = "logs"
    LOG_FILE: str = "app.log"
    LOG_FILE_PATH: Optional[Path] = None
    
    # 일정 관련 설정
    MAX_RESTAURANTS_PER_DAY: int = 2  # 하루 최대 음식점 수
    MIN_SPOTS_PER_DAY: int = 3  # 하루 최소 관광지 수
    MAX_SPOTS_PER_DAY: int = 8
    MAX_TRAVEL_DAYS: int = 7
    RESTAURANT_RATIO: float = 0.3  # 하루 일정 중 음식점 비율
    MAX_DISTANCE: float = 50.0  # 최대 이동 거리 (km)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 로그 디렉토리 생성
        log_dir = Path(self.LOG_DIR)
        log_dir.mkdir(exist_ok=True)
        
        # 로그 파일 경로 설정
        self.LOG_FILE_PATH = log_dir / self.LOG_FILE

settings = Settings() 