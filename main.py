from fastapi import FastAPI
from database import Base, engine
from routes.auth_routes import router as auth_router


app = FastAPI()
@app.get("/")
def root():
    return {"message": "FastAPI is running"}

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])

