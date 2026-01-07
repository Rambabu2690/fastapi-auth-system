import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import SignupSchema, LoginSchema, ResetPasswordSchema, ForgotPasswordSchema, UpdateUserSchema
from database import SessionLocal
from models import User
from auth import hash_password, verify_password, create_token
from email_utils import send_email
from sqlalchemy import or_
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from auth import get_current_user

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
def signup(user: SignupSchema, db: Session = Depends(get_db)):

    # Duplicate checks
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hash password
    hashed = hash_password(user.password)

    # Create user
    new_user = User(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hashed
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)   # ✅ important

    # ✅ SEND WELCOME EMAIL AFTER COMMIT
    send_email(
        user.email,
        "Welcome to the Platform",
        f"Hi {user.first_name},\n\nWelcome to our platform 🎉\nYour account has been created successfully."
    )

    return {"message": "Signup successful"}



# ================= LOGIN =================
@router.post("/login")
def login(credentials: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(user.email)
    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ================= FORGOT PASSWORD =================
from datetime import datetime, timedelta
import random

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = str(random.randint(100000, 999999))
    user.otp = otp
    user.otp_expiry = datetime.utcnow() + timedelta(minutes=5)

    db.commit()
    db.refresh(user)

    send_email(
        data.email,
        "OTP Verification",
        f"Your OTP is {otp}. It expires in 5 minutes."
    )

    return {"message": "OTP sent successfully"}



# ================= RESET PASSWORD =================
@router.post("/reset-password")
def reset_password(data: ResetPasswordSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.otp != data.otp or datetime.utcnow() > user.otp_expiry:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user.password = hash_password(data.new_password)
    user.otp = None
    user.otp_expiry = None

    db.commit()
    db.refresh(user)

    return {"message": "Password updated successfully"}


# ================= LIST USERS (PAGINATION) =================
@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    return db.query(User).all()


# ================= UPDATE USER =================
@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    data: UpdateUserSchema,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Username uniqueness check
    if data.username:
        existing_user = (
            db.query(User)
            .filter(
                User.username == data.username,
                User.id != user_id
            )
            .first()
        )
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )

    updated = False

    for field in ["username", "first_name", "last_name"]:
        value = getattr(data, field)
        if value is not None and getattr(user, field) != value:
            setattr(user, field, value)
            updated = True

    if not updated:
        return {"message": "No changes detected"}

    db.commit()
    db.refresh(user)

    return {"message": "User updated successfully"}

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)  # JWT protected
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
