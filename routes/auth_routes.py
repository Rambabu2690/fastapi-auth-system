import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User
from auth import hash_password, verify_password, create_token
from email_utils import send_email

router = APIRouter()


@router.get("/test")
def test():
    return {"msg": "ok"}

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= SIGNUP =================
@router.post("/signup")
def signup(user: dict, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user["email"]).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(user["password"])

    new_user = User(
        username=user["username"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        email=user["email"],
        password=hashed
    )

    db.add(new_user)
    db.commit()

    send_email(
        user["email"],
        "Welcome!",
        "Welcome to our platform 🎉"
    )

    return {"message": "Signup successful"}


# ================= LOGIN =================
@router.post("/login")
def login(credentials: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials["email"]).first()

    if not user or not verify_password(credentials["password"], user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(user.email)
    return {"access_token": token}


# ================= FORGOT PASSWORD =================
@router.post("/forgot-password")
def forgot_password(data: dict, db: Session = Depends(get_db)):
    email = data.get("email")

    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = str(random.randint(100000, 999999))
    user.otp = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)

    db.commit()

    send_email(
        email,
        "OTP Verification",
        f"Your OTP is {otp}. It expires in 5 minutes."
    )

    return {"message": "OTP sent"}


# ================= RESET PASSWORD =================
@router.post("/reset-password")
def reset_password(data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data["email"]).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.otp != data["otp"] or datetime.utcnow() > user.otp_expiry:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user.password = hash_password(data["new_password"])
    user.otp = None
    user.otp_expiry = None

    db.commit()
    return {"message": "Password updated successfully"}


# ================= LIST USERS (PAGINATION) =================
@router.get("/users")
def list_users(page: int = 1, limit: int = 10, db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    users = db.query(User).offset(offset).limit(limit).all()
    return users


# ================= UPDATE USER =================
@router.put("/users/{user_id}")
def update_user(user_id: int, data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    allowed_fields = ["username", "first_name", "last_name"]
    updated = False

    # Username uniqueness check
    if "username" in data:
        existing_user = (
            db.query(User)
            .filter(User.username == data["username"], User.id != user_id)
            .first()
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

    for field in allowed_fields:
        if field in data and getattr(user, field) != data[field]:
            setattr(user, field, data[field])
            updated = True

    if not updated:
        return {"message": "No changes detected"}

    db.commit()
    return {"message": "User updated successfully"}
