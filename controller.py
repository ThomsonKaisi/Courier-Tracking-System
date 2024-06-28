from settings import *
#User registration

def register_user(name: str, email: str, password: str,phone:str, bio: str = None):
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

#Station registration

def register_station(name:str,location:str):
    db = SessionLocal()
    existing_station = db.query(Station).filter(Station.name == name).first()
    if existing_station:
        raise HTTPException(status_code=400, detail="station already registered!")
    new_station = Station(name=name,location=location)
    db.add(new_station)
    db.commit()
    db.refresh()
    return {"message":"station registered successfully!"}

# Get Notification
def get_notification(token:str):
    
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

# Track parcel Received 
def track_parcel(token:str):
    
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

# Track Sent
def track_sent(token:str):
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

def account_info(token:str):
    if verification(token):
         id = user_id(token)
         db =SessionLocal()
         User_instance = db.query(User).filter(User.id == id).first()
         return {"user":[User_instance.name,User_instance.email,User_instance.bio]}
    else:
        raise HTTPException(status_code=400, detail="un aunthenticated user!")

#Adding or updating address
def update_address(token:str,district:str,box_number:str,area:str,description:str):
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
def register_parcel(name: str, description: str, status: str, sender_id:int, receiver_id:int, source_id:int,destination_id:int,token:str):
    db = SessionLocal()
    new_parcel = Parcel(name=name, description =description, status=status, sender_id=sender_id, receiver_id=receiver_id, source_id=source_id,destination_id=destination_id)
    
    db.add(new_parcel)
    db.commit()
    db.refresh()
    return {"message":"Parcel registered successfully"}

# Creating group
def create_group(name:str,description:str,token:str):
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

def logout(token:str):
    if verification(token):
        delete_query = delete(Auth).where(Auth.token == token)
        db = SessionLocal()
        db.execute(delete_query)
        db.commit()
        return {'message':'logout successful'}
    else:
        raise HTTPException(status_code=400, detail="Can not logout unauthenticated user!")
    
# Changing password   
def update_password(email:str,new_password:str):
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
    
#verifying OTP    
def verifying_otp(otp:int):
    if otp_verification(otp):
        db = SessionLocal()
        otp_instance = db.query(OTP).filter(OTP.otp_token==otp).first()
        password_transfer(otp_instance.email)
        return {"message":"Password Changed Successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    






    

    
