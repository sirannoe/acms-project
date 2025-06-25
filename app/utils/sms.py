# app/utils/sms.py
import africastalking
import os
from dotenv import load_dotenv

load_dotenv()

africastalking.initialize(
    username=os.getenv("AT_USERNAME"),
    api_key=os.getenv("AT_API_KEY")
)

sms = africastalking.SMS

def send_sms(recipient, message):
    try:
        response = sms.send(message, [recipient])
        return response
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None
