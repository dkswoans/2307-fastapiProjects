# FastAPI 및 관련 모듈 임포트
from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from .database import engine, get_db
from . import models
from .routers import trails, records, users, reservations
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(title="도시 산책로 추천 및 기록 서비스")

# 애플리케이션 시작 시 데이터베이스 테이블 자동 생성
models.Base.metadata.create_all(bind=engine)

# Jinja2 템플릿 엔진 설정
# HTML 템플릿 파일은 app/templates 디렉토리에 위치
templates = Jinja2Templates(directory="app/templates")

# 정적 파일(CSS, JavaScript, 이미지 등) 설정
# 정적 파일은 app/static 디렉토리에 위치
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 기능별 라우터 등록
app.include_router(trails.router)
app.include_router(records.router)
app.include_router(users.router)
app.include_router(reservations.router)

@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    trails = db.query(models.Trail).all()
    return templates.TemplateResponse("index.html", {"request": request, "trails": trails})

@app.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    # 예시: 전체 산책로 수, 전체 산책 기록 수, 전체 사용자 수
    trail_count = db.query(models.Trail).count()
    record_count = db.query(models.WalkRecord).count() if hasattr(models, 'WalkRecord') else 0
    user_count = db.query(models.User).count()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "trail_count": trail_count,
        "record_count": record_count,
        "user_count": user_count    
    })

@app.on_event("startup")
def startup_event():
    db = next(get_db())
    # 기본 사용자 생성 (id=1)
    if not db.query(models.User).filter_by(id=1).first():
        user = models.User(id=1, username="testuser", password="testpass")
        db.add(user)
        db.commit()
    # 기본 산책로 데이터
    if not db.query(models.Trail).first():
        default_trails = [
            models.Trail(
                name="한강공원 산책로",
                type=models.TrailType.RIVER,
                location="서울특별시 영등포구",
                distance_km=5.2,
                description="한강을 따라 걷는 대표적인 산책로.",
                image_url="https://images.unsplash.com/photo-1506744038136-46273834b3fb"
            ),
            models.Trail(
                name="서울숲 산책로",
                type=models.TrailType.PARK,
                location="서울특별시 성동구",
                distance_km=3.1,
                description="도심 속 자연을 느낄 수 있는 산책로.",
                image_url="https://images.unsplash.com/photo-1465101046530-73398c7f28ca"
            ),
            models.Trail(
                name="북한산 둘레길",
                type=models.TrailType.FOREST,
                location="서울특별시 은평구",
                distance_km=7.8,
                description="산림욕과 함께 걷기 좋은 숲길.",
                image_url="https://images.unsplash.com/photo-1500534314209-a25ddb2bd429"
            )
        ]
        db.add_all(default_trails)
        db.commit()
        db.close()