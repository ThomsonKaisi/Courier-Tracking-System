from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, Request
from models import Base, User,Parcel,Group,Auth, Notification, Address, OTP
from passlib.hash import bcrypt
from settings import *
from authenticator.auth_handler import sign_token, verification, user_id, user_email, password_transfer,otp_generator,otp_verification
from sqlalchemy import delete
from messages import PASSWORD, REGISTER
from SMS_notifications import send_SMS

app = FastAPI()

Base.metadata.create_all(bind=engine)


#User Routes

@app.post("/register_user/")
async def register_user(name: str, email: str, password: str,phone:str, bio: str = None):
    # Check if the email already exists
    db = SessionLocal()
    existing_user = db.query(User).filter(User.email == email).first()
    existing_phone = db.query(User).filter(User.phone == phone).first()
    if existing_user or existing_phone:
        raise HTTPException(status_code=400, detail="Email already registered or Phone Number Already Registered")

    # Hash the password
    
    hashed_password = bcrypt.hash(password)
    otp = otp_generator(email,hashed_password)
    message = f"{REGISTER} OTP:{otp}"
    send_SMS(phone,message)
    new_user = User(name=name, email=email, bio=bio,phone=phone)
    group = db.query(Group).filter(Group.id == 1).first()
    new_user.group =group
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"OTP has been sent to {phone}"}

@app.post('/register_station/')
async def register_station(parcels_departed):
    pass


@app.post("/notification/")
async def get_notification(token:str):
    
    if verification(token):
        user_id = user_id(token)
        db = SessionLocal()
        notifications = db.query(Notification).filter(Notification.receiver_id == user_id).all()
        if notifications:
            return {"notifications":[notifications.message for notification in notifications ]}
        else:
            return {"notifications":[]}
    else:
        raise HTTPException(status_code=400, detail="un aunthenticated user!")
  #tracking received parcels  
@app.post("/track_received/")
async def track_parcel(token:str):
    
    if verification(token):
        id = user_id(token)
        db = SessionLocal()
        parcel_instance = db.query(Parcel).filter(Parcel.receiver_id ==id).all()
        if parcel_instance:
            return {"parcels":[parcel_instance.name for parcel in parcel_instance]}
        else:
            return {"parcels":[]}
    else:
        raise HTTPException(status_code=400, detail="un aunthenticated user!")
#tracking sent parcels
@app.post("/track_sent/")
async def track_sent(token:str):
    if verification(token):
        id=user_id(token)
        db = SessionLocal()
        parcel_instance = db.query(Parcel).filter(Parcel.sender_id ==id).all()
        if parcel_instance:
            return {"parcels":[parcel_instance.name for parcel in parcel_instance],}
        else:
            return {"parcels":[]}
    else:
        raise HTTPException(status_code=400, detail="un aunthenticated user!")

#basic account Information

@app.post("/account_info/")
async def account_info(token:str):
    if verification(token):
         id = user_id(token)
         db =SessionLocal()
         User_instance = db.query(User).filter(User.id == id).first()
         return {"user":[User_instance.name,User_instance.email,User_instance.bio]}
    else:
        raise HTTPException(status_code=400, detail="un aunthenticated user!")
    

#Adding or updating address
@app.post("/update_address/")
async def update_address(token:str,district:str,box_number:str,area:str,description:str):
    if verification(token):
        id = user_id(token)
        db =SessionLocal()
         # Check if address already exists
        address_instance = db.query(Address).filter(Address.user_id == id).first()
        if address_instance:
            # Update existing address
            address_instance.area=area
            address_instance.box_number=box_number
            address_instance.district =district
            address_instance.description=description
            db.commit()
            return {"message":"Address Updated Successfully"}
        else:
            # Create new Address
            new_address= Address(area=area,description=description,box_number=box_number,district=district,user_id=id)
            db.add(new_address)
            db.commit()
            db.refresh(new_address)
            return {"message":"Address Added Successfully"}
    else:
        raise HTTPException(status_code=400, detail=" unaunthenticated user!")    

# Admin Routes

@app.post("/register_parcel/")
async def register_parcel(name: str, description: str, status: str, sender_id:int, receiver_id:int, source_id:int,destination_id:int,token:str):
    db = SessionLocal()
    new_parcel = Parcel(name=name, description =description, status=status, sender_id=sender_id, receiver_id=receiver_id, source_id=source_id,destination_id=destination_id)
    
    db.add(new_parcel)
    db.commit()
    db.refresh()
    return {"message":"Parcel registered successfully"} 

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

#General Routes

@app.post('/login/')
async def login(email:str,password:str,):
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
    
@app.post("/logout/")
async def logout(token:str):
    if verification(token):
        delete_query = delete(Auth).where(Auth.token == token)
        db = SessionLocal()
        db.execute(delete_query)
        db.commit()
        return {'message':'logout successful'}
    else:
        raise HTTPException(status_code=400, detail="Can not logout unauthenticated user!")

#Changing password

@app.post("/update_password/")
async def update_password(email:str,new_password:str):
    db =SessionLocal()
    user_instance = db.query(User).filter(User.email==email).first()
    if user_instance:
         hashed_password = bcrypt.hash(new_password)
         otp =otp_generator(email,hashed_password)
         phone = str(user_instance.phone)
         message = f"{PASSWORD} OTP:{otp}."
         send_SMS(phone,message)
         return {"message":"An OTP has been sent to Your Mobile"}
    else:
        raise HTTPException(status_code=400, detail="Email or user does not exist!")
    
@app.post("/otp_verification/")
async def verifying_otp(otp:int):
    if otp_verification(otp):
        db = SessionLocal()
        otp_instance = db.query(OTP).filter(OTP.otp_token==otp).first()
        password_transfer(otp_instance.email)
        return {"message":"Password Changed Successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP")

            



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



