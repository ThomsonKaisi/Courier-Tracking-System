import random
import string
from datetime import datetime, timedelta
from settings import *
from models import Base,Auth, User,Group
Base.metadata.create_all(bind=engine)

def generate_random_ascii_word(length=10):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

SEED = hash(generate_random_ascii_word())


def sign_token(user_id:str):
    token = hash(user_id+SEED)
    expire = datetime.now() + timedelta(hours=1)
    db = SessionLocal()
    new_auth = Auth(email =user_id,token=token,expire=expire,seed=SEED)
    db.add(new_auth)
    db.commit()
    db.refresh(new_auth)  
    return {"token":token}


def verification(user_id:str,token:str):
    db = SessionLocal()
    auth_instance = db.query(Auth).filter(Auth.email == user_id).first()
    if auth_instance:
        generated = hash(user_id+auth_instance.seed)
        expire = auth_instance.expire
        if token == generated and datetime.now <expire:
            return True
        else:
            return False
        
def group_verification(user_id:str):
    db =SessionLocal()
    user_instance = db.query(User).filter(User.email == user_id).first()
    group_instance = db.query(Group).filter(Group.id == user_instance.group_id).first()
    return group_instance.name

