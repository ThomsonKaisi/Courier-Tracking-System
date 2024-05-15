from fastapi import FastAPI, HTTPException
from models import Base, User,Parcel,Group,Auth
from passlib.hash import bcrypt
from settings import *
from authenticator.auth_handler import sign_token, verification
from sqlalchemy import delete

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
    group = db.query(Group).filter(Group.id == 1).first()
    new_user.group =group
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}
@app.post('/register_station/')
async def register_station(parcels_departed):
    pass

@app.post('/login/')
async def login(email:str,password:str):
    db = SessionLocal()
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        if bcrypt.verify(password, existing_user.password):
            token =sign_token(email)
            return {'message':'login successful','token':token}
        else:
            raise HTTPException(status_code=400, detail="Incorrect username or password")
    else:
        raise HTTPException(status_code=400, detail="The account does not exist")
    
@app.post('/logout/')
async def logout(token:str):
    if verification(token):
        delete_query = delete(Auth).where(Auth.token == token)
        db = SessionLocal()
        db.execute(delete_query)
        db.commit()
        return {'message':'logout successful'}
    else:
        raise HTTPException(status_code=400, detail="Can not logout unauthenticated user!")
            

@app.post('/create_group/')
async def create_group(name:str,description:str,token:str):
    db = SessionLocal()
    existing_group = db.query(Group).filter(Group.name == name).first()
    if existing_group:
        raise HTTPException(status_code=400, detail="Group Already registered")
    
    new_group = Group(name=name,description=description)
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return {'message':'Group registered successfully'}

    
    

@app.post("/register_parcel/")
async def register_parcel(name: str, description: str, status: str, sender_id:int, receiver_id:int, source_id:int,destination_id:int,token:str):
    db = SessionLocal()
    new_parcel = Parcel(name=name, description =description, status=status, sender_id=sender_id, receiver_id=receiver_id, source_id=source_id,destination_id=destination_id)
    
    db.add(new_parcel)
    db.commit()
    db.refresh()
    return {"message":"Parcel registered successfully"}


    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



