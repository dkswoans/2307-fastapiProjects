from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db
from fastapi.templating import Jinja2Templates

# 시설 관련 라우터 생성
# prefix: 모든 라우트의 기본 경로
# tags: API 문서화를 위한 태그
router = APIRouter(
    prefix="/facilities",
    tags=["facilities"]
)

# Jinja2 템플릿 엔진 설정
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_model=List[schemas.Facility])
def get_facilities(
    request: Request,
    skip: int = 0,  # 건너뛸 레코드 수
    limit: int = 100,  # 반환할 최대 레코드 수
    db: Session = Depends(get_db)
):
    """
    모든 시설 목록을 조회하는 엔드포인트
    페이지네이션을 지원하며, 시설 목록 페이지를 렌더링합니다
    """
    # 데이터베이스에서 시설 목록 조회
    facilities = db.query(models.Facility).offset(skip).limit(limit).all()
    # 시설 목록 페이지 템플릿 렌더링
    return templates.TemplateResponse(
        "facilities/list.html",
        {"request": request, "facilities": facilities}
    )

@router.post("/", response_model=schemas.Facility)
def create_facility(facility: schemas.FacilityCreate, db: Session = Depends(get_db)):
    """
    새로운 시설을 생성하는 엔드포인트
    요청 데이터를 검증하고 데이터베이스에 저장합니다
    """
    # 요청 데이터로 새로운 시설 객체 생성
    db_facility = models.Facility(**facility.dict())
    # 데이터베이스에 저장
    db.add(db_facility)
    db.commit()
    db.refresh(db_facility)
    return db_facility

@router.get("/{facility_id}", response_model=schemas.Facility)
def get_facility(facility_id: int, db: Session = Depends(get_db)):
    """
    특정 ID의 시설 정보를 조회하는 엔드포인트
    시설이 존재하지 않는 경우 404 에러를 반환합니다
    """
    # ID로 시설 조회
    facility = db.query(models.Facility).filter(models.Facility.id == facility_id).first()
    if facility is None:
        raise HTTPException(status_code=404, detail="Facility not found")
    return facility

@router.put("/{facility_id}", response_model=schemas.Facility)
def update_facility(
    facility_id: int,
    facility: schemas.FacilityUpdate,
    db: Session = Depends(get_db)
):
    """
    특정 ID의 시설 정보를 업데이트하는 엔드포인트
    시설이 존재하지 않는 경우 404 에러를 반환합니다
    """
    # ID로 시설 조회
    db_facility = db.query(models.Facility).filter(models.Facility.id == facility_id).first()
    if db_facility is None:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    # 요청 데이터로 시설 정보 업데이트
    for key, value in facility.dict(exclude_unset=True).items():
        setattr(db_facility, key, value)
    
    # 변경사항 저장
    db.commit()
    db.refresh(db_facility)
    return db_facility

@router.delete("/{facility_id}")
def delete_facility(facility_id: int, db: Session = Depends(get_db)):
    """
    특정 ID의 시설을 삭제하는 엔드포인트
    시설이 존재하지 않는 경우 404 에러를 반환합니다
    """
    # ID로 시설 조회
    facility = db.query(models.Facility).filter(models.Facility.id == facility_id).first()
    if facility is None:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    # 시설 삭제
    db.delete(facility)
    db.commit()
    return {"message": "Facility deleted successfully"} 

@router.get("/new")
def new_facility_form(request: Request):
    """
    시설 등록 페이지를 렌더링합니다
    """
    return templates.TemplateResponse("facilities/new.html", {"request": request})