import random
import string
from datetime import datetime, timedelta
from settings import *
from models import Base,Auth, User,Group, OTP
from sqlalchemy import delete
from fastapi import HTTPException
from passlib.hash import bcrypt
import hashlib
Base.metadata.create_all(bind=engine)

def generate_random_ascii_word(length=10):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

SEED = hash(generate_random_ascii_word())


def sign_token(user_id: str):
    value = str(user_id) + str(SEED)
    token = hashlib.sha256(value.encode()).hexdigest()
    expire = datetime.now() + timedelta(hours=1)
    db = SessionLocal()
    
    # Check if token already exists
    existing_auth = db.query(Auth).filter(Auth.email == user_id).first()
    if existing_auth:
        # Update existing token
        existing_auth.token = token
        existing_auth.expire = expire
        existing_auth.seed = SEED
        db.commit()
        return token
    else:
        # Create new token
        new_auth = Auth(email=user_id, token=token, expire=expire, seed=SEED)
        db.add(new_auth)
        db.commit()
        db.refresh(new_auth)
        return token

#verifying if the token is valid and uptodate


def verification(token: str):
    db = SessionLocal()
    auth_instance = db.query(Auth).filter(Auth.token == token).first()
    if auth_instance:
        expected = auth_instance.email + auth_instance.seed
        generated = hashlib.sha256(expected.encode()).hexdigest()
        stored_hash = auth_instance.token
        
        if generated == stored_hash:
            if datetime.now() < auth_instance.expire:
                return True
            else:
                # Delete expired entry
                db.delete(auth_instance)
                db.commit()
                return False
        else:
            raise HTTPException(status_code=400, detail="Bad Token!")
    else:
        return False

def group_verification(user_id:str):
    db =SessionLocal()
    user_instance = db.query(User).filter(User.email == user_id).first()
    group_instance = db.query(Group).filter(Group.id == user_instance.group_id).first()
    return {"name":group_instance.name,"id":group_instance.id}

def user_id(token:str):
    db =SessionLocal()
    auth_instance = db.query(Auth).filter(Auth.token == token).first()
    user_email = auth_instance.email
    user_instance = db.query(User).filter(User.email ==user_email).first()
    return user_instance.id

def otp_generator(email:str,password:str):
    otp_pin =random.randint(10000, 99999)
    db =SessionLocal()
    otp_instance = db.query(OTP).filter(OTP.email==email).first()
    if otp_instance:
        otp_instance.email = email
        otp_instance.expire = datetime.now() + timedelta(minutes=10)
        otp_instance.otp_token = otp_pin
        otp_instance.password =password
        db.commit()
        return otp_pin
    else:
        new_otp = OTP(email=email,expire=(datetime.now() + timedelta(minutes=10)),otp_token=otp_pin,password=password)
        db.add(new_otp)
        db.commit()
        db.refresh(new_otp)
        return otp_pin

def otp_verification(otp_pin:int):
    db = SessionLocal()
    otp_instance = db.query(OTP).filter(OTP.otp_token==otp_pin).first()
    if otp_instance:
        if datetime.now() < otp_instance.expire:
            return True
        else:
            return False
    else:
        return False
    
def user_email(token:str):
    db =SessionLocal()
    auth_instance = db.query(Auth).filter(Auth.token == token).first()
    return auth_instance.email
#Transfering  password from otp table to user table
def password_transfer(email:str):
    db =SessionLocal()
    user_instance = db.query(User).filter(User.email==email).first()
    otp_instance = db.query(OTP).filter(OTP.email==email).first()
    user_instance.password =otp_instance.password
    db.commit()

