from settings import *

app.post('/getuserinfo/')
def get_user_info(email:str):
    db =SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if user:
        return {"name":user.name,"address":user.address,"bio":user.bio,"group":user.group,"phone":user.phone}
    else:
        raise HTTPException(status_code=400, detail="User does not exist")
app.post('/suspenduser/')
def suspend_user(email:str,reason:str):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.status = False
        send_SMS(recipient_number=user.phone,message=f"Your Account has been suspended by Admin. Reason: {reason}. Please contact the admin.")
        return {"message":f"user {user.name}, suspended successfully"}
    raise HTTPException(status_code=400, detail="User does not exist")
app.post('/activateaccount/')
def activate_account(email:str):
    db = SessionLocal()
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.status = True
        send_SMS(recipient_number=user.phone,message=f"Your Account has been activated !!")
        return{"message":"Account Activated"}
    raise HTTPException(status_code=400, detail="User does not exist")

    

    
    

