
from controller import *

#User Routes

@app.post("/register_user/")
async def register_user(name: str, email: str, password: str,phone:str, bio: str = None):
    register_user(name=name,email=email,password=password,phone=phone,bio=bio)

@app.post('/register_station/')
async def register_station(name:str,location:str):
    register_station(name=name,location=location)


@app.post("/notification/")
async def get_notification(token:str):
    get_notification(token=token)

#tracking received parcels  
@app.post("/track_received/")
async def track_parcel(token:str):
   track_parcel(token=token)

#tracking sent parcels
@app.post("/track_sent/")
async def track_sent(token:str):
    track_sent(token=token)

#basic account Information
@app.post("/account_info/")
async def account_info(token:str):
    account_info(token=token)
    

#Adding or updating address
@app.post("/update_address/")
async def update_address(token:str,district:str,box_number:str,area:str,description:str):
    update_address(token=token,district=district,box_number=box_number,area=area,description=description)    

# Admin Routes

@app.post("/register_parcel/")
async def register_parcel(name: str, description: str, status: str, sender_id:int, receiver_id:int, source_id:int,destination_id:int,token:str):
    register_parcel(name=name,description=description,status=status,sender_id=sender_id,receiver_id=receiver_id,destination_id=destination_id,token=token) 

# creating group
@app.post('/create_group/')
async def create_group(name:str,description:str,token:str):
    create_group(name=name,description=description,token=token)

#General Routes
@app.post('/login/')
async def login(email:str,password:str,):
    login(email=email,password=password)
    
@app.post("/logout/")
async def logout(token:str):
    logout(token=token)

#Changing password

@app.post("/update_password/")
async def update_password(email:str,new_password:str):
    update_password(email=email,new_password=new_password)
    
@app.post("/otp_verification/")
async def verifying_otp(otp:int):
    verifying_otp(otp=otp)

            

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



