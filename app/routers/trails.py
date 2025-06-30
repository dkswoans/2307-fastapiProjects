from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter(prefix="/trails", tags=["trails"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def list_trails(request: Request, db: Session = Depends(get_db)):
    trails = db.query(models.Trail).all()
    return templates.TemplateResponse("trails/list.html", {"request": request, "trails": trails})

@router.get("/{trail_id}")
def trail_detail(trail_id: int, request: Request, db: Session = Depends(get_db)):
    trail = db.query(models.Trail).filter(models.Trail.id == trail_id).first()
    return templates.TemplateResponse("trails/detail.html", {"request": request, "trail": trail}) 