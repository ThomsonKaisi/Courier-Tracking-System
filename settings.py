from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:fibonacci@127.0.0.1/courier_tracking_system"  
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, Request
from models import Base, User,Parcel,Group,Auth, Notification, Address, OTP, Station
from passlib.hash import bcrypt
from authenticator.auth_handler import sign_token, verification, user_id, user_email, password_transfer,otp_generator,otp_verification
from sqlalchemy import delete
from messages import PASSWORD, REGISTER
from SMS_notifications import send_SMS

app = FastAPI()

Base.metadata.create_all(bind=engine)

