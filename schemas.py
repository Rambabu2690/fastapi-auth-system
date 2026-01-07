from pydantic import BaseModel, EmailStr

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
