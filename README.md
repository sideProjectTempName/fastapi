# Tripplai
Tripplai 여행지 추천 서비스 전용 api

## 시작하기

1. 가상 환경 생성<br/>

프로젝트 루트 디렉토리에서 가상 환경을 생성합니다.
```cmd
python -m venv venv
```
2. 가상환경 활성화<br/>

windows:
```cmd
venv\Scripts\activate
```
macOS/Linux:
```cmd
source venv/bin/activate
```
3. 필요한 패키지 설치
```cmd
pip install -r requirements.txt
```
4. .env 파일 생성<br/>
루트 폴더에 ```".env"``` 파일을 생성하고 다음 설정을 해줍니다.
```python
# 데이터베이스 설정
DB_HOST=localhost
DB_PORT=5432
DB_USER=<username>
DB_PASSWORD=<password>
DB_NAME=<db_name>

# 로깅 설정
LOG_LEVEL=INFO
LOG_DIR=logs
LOG_FILE=app.log 
```
5. 실행
```cmd
uvicorn app.main:app --reload
```

