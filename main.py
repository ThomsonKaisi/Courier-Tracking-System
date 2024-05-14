from fastapi import FastAPI, HTTPException
from models import Base, User,Parcel
from passlib.hash import bcrypt
from settings import *

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.post("/register_user/")
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
@app.post('register_station')
async def register_station(parcels_departed):
    pass

@app.post("/register_parcel")
async def register_parcel(name: str, description: str, status: str, sender_id:int, receiver_id:int, source_id:int,destination_id:int ):
    db = SessionLocal()
    new_parcel = Parcel(name=name, description =description, status=status, sender_id=sender_id, receiver_id=receiver_id, source_id=source_id,destination_id=destination_id)
    
    db.add(new_parcel)
    db.commit()
    db.refresh()
    return {"message":"Parcel registered successfully"}


    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



