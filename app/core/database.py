import psycopg2
from psycopg2.extras import RealDictCursor
from app.core.config import settings

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        raise Exception(f"데이터베이스 연결 실패: {str(e)}")

def get_db_cursor():
    """데이터베이스 커서를 생성합니다."""
    conn = get_db_connection()
    try:
        return conn.cursor()
    except Exception as e:
        conn.close()
        raise Exception(f"커서 생성 실패: {str(e)}") 