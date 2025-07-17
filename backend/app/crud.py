from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, encryption
from app.models import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def add_password(data: schemas.PasswordCreate, db: Session = Depends(get_db)):
    encrypted_pw = encryption.encrypt_password(data.password)
    new_pw = models.Password(site=data.site, username=data.username, encrypted_password=encrypted_pw, user_id=1)
    db.add(new_pw)
    db.commit()
    return {"success": True, "message": "Password saved"}

@router.get("/")
def get_passwords(db: Session = Depends(get_db)):
    passwords = db.query(models.Password).all()
    return [
        {"site": p.site, "username": p.username, "password": encryption.decrypt_password(p.encrypted_password)}
        for p in passwords
    ]
