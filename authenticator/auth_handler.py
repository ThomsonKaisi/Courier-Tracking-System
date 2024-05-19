import random
import string
from datetime import datetime, timedelta
from settings import *
from models import Base,Auth, User,Group
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


