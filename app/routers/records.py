from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter(prefix="/records", tags=["records"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def list_records(request: Request, db: Session = Depends(get_db)):
    # 임시: user_id=1로 고정
    records = db.query(models.WalkRecord).filter(models.WalkRecord.user_id == 1).all()
    return templates.TemplateResponse("records/list.html", {"request": request, "records": records})

@router.get("/new")
def new_record_form(request: Request, db: Session = Depends(get_db)):
    trails = db.query(models.Trail).all()
    return templates.TemplateResponse("records/new.html", {"request": request, "trails": trails})

@router.post("/new")
def create_record(request: Request, trail_id: int = Form(...), memo: str = Form(""), db: Session = Depends(get_db)):
    # 임시: user_id=1로 고정
    record = models.WalkRecord(user_id=1, trail_id=trail_id, memo=memo)
    db.add(record)
    db.commit()
    return RedirectResponse("/records/", status_code=303) 