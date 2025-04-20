from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from datetime import datetime
from sqlalchemy.orm import Session
from web_panel.db import get_db
from web_panel.models import Complaint
import os

router = APIRouter()
templates = Jinja2Templates(directory="web_panel/templates")

JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = "HS256"

# Главная
@router.get("/", response_class=HTMLResponse)
async def root_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

# Список жалоб с фильтрами
@router.get("/html", response_class=HTMLResponse)
async def complaints_html(
    request: Request,
    token: str,
    full_name: str = "",
    date_from: str = "",
    date_to: str = "",
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        exp = payload.get("exp")

        if user_id is None or exp is None or datetime.utcnow().timestamp() > exp:
            return HTMLResponse(content="⛔️ Токен недействителен или просрочен", status_code=401)

    except JWTError:
        return HTMLResponse(content="⛔️ Ошибка авторизации", status_code=401)

    query = db.query(Complaint)

    if full_name:
        query = query.filter(Complaint.full_name.ilike(f"%{full_name}%"))
    if date_from:
        query = query.filter(Complaint.created_at >= datetime.strptime(date_from, "%Y-%m-%d"))
    if date_to:
        query = query.filter(Complaint.created_at <= datetime.strptime(date_to, "%Y-%m-%d"))

    complaints = query.order_by(Complaint.created_at.desc()).all()

    return templates.TemplateResponse("complaints.html", {
        "request": request,
        "complaints": complaints,
        "token": token,
        "full_name": full_name,
        "date_from": date_from,
        "date_to": date_to
    })

