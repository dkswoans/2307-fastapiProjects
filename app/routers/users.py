from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter(prefix="/users", tags=["users"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/mypage")
def mypage(request: Request, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == 1).first()
    records = db.query(models.WalkRecord).filter(models.WalkRecord.user_id == 1).all()
    reviews = db.query(models.TrailReview).filter(models.TrailReview.user_id == 1).all()
    return templates.TemplateResponse("users/mypage.html", {"request": request, "user": user, "records": records, "reviews": reviews}) 