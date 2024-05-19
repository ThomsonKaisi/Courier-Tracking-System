import requests
from config import SMS_TOKEN,SMS_URL

def send_SMS(recipient_number:str,message:str):
    payload = {"to": recipient_number, "message": message}
    headers = {
    "Authorization": f"{SMS_TOKEN}",
    "Content-Type": "application/json"
    }
    try:
        with requests.Session() as session:
            response = session.post(SMS_URL, json=payload, headers=headers, verify=False)
            return True
    except Exception as e:
        return False
