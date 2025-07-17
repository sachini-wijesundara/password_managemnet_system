import pyotp
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app import schemas, models, encryption
from app.database import get_db

router = APIRouter()

# ✅ Registration - save user + TOTP secret
@router.post("/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = encryption.hash_password(user.password)
    totp_secret = pyotp.random_base32()  # 🔥 Generate secret for Google Authenticator

    new_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        otp_secret=totp_secret
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    print(f"✅ Save this secret for {user.email}: {totp_secret}")  # 🔥 Give this to lecturer manually

    return {
        "success": True,
        "message": "Registered successfully. Setup Google Authenticator with your secret.",
        "totp_secret": totp_secret  # 🔥 Show so user can add it manually in app
    }

# ✅ Login Step 1: Verify password
@router.post("/login")
def login_user(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not encryption.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"success": True, "message": "Password verified. Enter your 6-digit code."}

# ✅ Login Step 2: Verify 6-digit TOTP
@router.post("/verify-otp")
def verify_otp(data: schemas.OTPVerify, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == data.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    totp = pyotp.TOTP(db_user.otp_secret)
    if totp.verify(data.otp):  # ✅ Checks the 6-digit TOTP
        print(f"✅ TOTP verified for {data.email}")
        return {"success": True, "message": "Login successful"}
    raise HTTPException(status_code=400, detail="Invalid 6-digit code")
