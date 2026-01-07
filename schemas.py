from pydantic import BaseModel, EmailStr
from pydantic import BaseModel
from typing import Optional

class SignupSchema(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class ResetPasswordSchema(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
class ForgotPasswordSchema(BaseModel):   
    email: EmailStr

class UpdateUserSchema(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None