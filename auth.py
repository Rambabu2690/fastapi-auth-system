from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

# ================= JWT CONFIG =================
SECRET_KEY = "f9a2c8e1b4d7a6c3e5f098a1d4c7b2e9a6f3d8c1b4e7a9"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

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

# ================= JWT TOKEN FUNCTION =================
def create_token(email: str) -> str:
    payload = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
