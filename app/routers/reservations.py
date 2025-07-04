from fastapi import APIRouter, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas
from ..database import get_db
from fastapi.templating import Jinja2Templates
from datetime import datetime
from fastapi.responses import RedirectResponse

router = APIRouter(
prefix="/reservations",
    tags=["reservations"]
)

templates = Jinja2Templates(directory="app/templates")

@router.get("/new")
async def new_reservation(
    request: Request,
    facility_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    새로운 예약을 생성하는 페이지를 렌더링하는 엔드포인트
    특정 시설에 대한 예약인 경우 해당 시설 정보를, 그렇지 않은 경우 모든 시설 목록을 제공합니다
    """
    facility = None
    facilities = None
    
    if facility_id is not None:
        facility = db.query(models.Facility).filter(models.Facility.id == facility_id).first()
        if not facility:
            raise HTTPException(status_code=404, detail="Facility not found")
    else:
        facilities = db.query(models.Facility).all()

    return templates.TemplateResponse(
        "reservations/new.html",
        {"request": request, "facility": facility, "facilities": facilities}
    )

@router.get("/{reservation_id}/edit")
async def edit_reservation(
    request: Request,
    reservation_id: int,
    db: Session = Depends(get_db)
):
    """
    기존 예약을 수정하는 페이지를 렌더링하는 엔드포인트
    예약이 존재하지 않는 경우 404 에러를 반환합니다
    """
    reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    return templates.TemplateResponse(
        "reservations/edit.html",
        {"request": request, "reservation": reservation}
    )

@router.get("/")
def get_reservations(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    모든 예약 목록을 조회하는 엔드포인트
    페이지네이션을 지원하며, 예약 목록 페이지를 렌더링합니다
    """
    reservations = db.query(models.Reservation).offset(skip).limit(limit).all()
    return templates.TemplateResponse(
        "reservations/list.html",
        {"request": request, "reservations": reservations}
    )

@router.post("/new")
async def create_reservation(
    request: Request,
    reservation: schemas.ReservationCreate,  # JSON body로 받음
    db: Session = Depends(get_db)
):
    # 시간 중복 체크
    existing = db.query(models.Reservation).filter(
        models.Reservation.facility_id == reservation.facility_id,
        models.Reservation.start_time <= reservation.end_time,
        models.Reservation.end_time >= reservation.start_time
    ).first()
    if existing:
        return templates.TemplateResponse(
            "reservations/new.html",
            {"request": request, "error": "이미 해당 시간에 예약이 있습니다.", "facility": None, "facilities": db.query(models.Facility).all()}
        )
    new_reservation = models.Reservation(
        facility_id=reservation.facility_id,
        user_name=reservation.user_name,
        user_phone=reservation.user_phone,
        start_time=reservation.start_time,
        end_time=reservation.end_time,
        purpose=reservation.purpose,
        capacity=reservation.capacity
    )
    db.add(new_reservation)
    db.commit()
    return RedirectResponse("/reservations", status_code=303)

@router.get("/{reservation_id}", response_model=schemas.Reservation)
def get_reservation(reservation_id: int, db: Session = Depends(get_db)):
    """
    특정 ID의 예약 정보를 조회하는 엔드포인트
    예약이 존재하지 않는 경우 404 에러를 반환합니다
    """
    reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return reservation

@router.put("/{reservation_id}", response_model=schemas.Reservation)
def update_reservation(
    reservation_id: int,
    reservation: schemas.ReservationUpdate,
    db: Session = Depends(get_db)
):
    """
    특정 ID의 예약 정보를 업데이트하는 엔드포인트
    예약이 존재하지 않는 경우 404 에러를 반환합니다
    """
    db_reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
    if db_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    for key, value in reservation.dict(exclude_unset=True).items():
        setattr(db_reservation, key, value)
    
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

@router.delete("/{reservation_id}")
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    """
    특정 ID의 예약을 삭제하는 엔드포인트
    예약이 존재하지 않는 경우 404 에러를 반환합니다
    """
    reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    db.delete(reservation)
    db.commit()
    return {"message": "Reservation deleted successfully"} 