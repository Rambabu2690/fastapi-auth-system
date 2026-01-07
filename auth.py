from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer


# ================= JWT CONFIG =================
SECRET_KEY = "f9a2c8e1b4d7a6c3e5f098a1d4c7b2e9a6f3d8c1b4e7a9"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ================= OAUTH2 CONFIG =================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ================= PASSWORD CONFIG =================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# ================= PASSWORD FUNCTIONS =================
def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        password = password[:72]
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    if len(password.encode("utf-8")) > 72:
        password = password[:72]
    return pwd_context.verify(password, hashed)


# ================= JWT TOKEN CREATION =================
def create_token(email: str) -> str:
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ================= JWT TOKEN VERIFICATION =================
def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return email

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
