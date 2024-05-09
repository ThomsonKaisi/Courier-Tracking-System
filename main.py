from fastapi import FastAPI, HTTPException
from models import Base, User
from passlib.hash import bcrypt
from settings import *

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.post("/register/")
async def register_user(name: str, email: str, password: str, bio: str = None):
    # Check if the email already exists
    db = SessionLocal()
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password
    hashed_password = bcrypt.hash(password)
    new_user = User(name=name, email=email, password=hashed_password, bio=bio)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



