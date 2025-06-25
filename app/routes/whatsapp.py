import os, requests, json, logging
from flask import Blueprint, request, abort, jsonify

whatsapp_bp = Blueprint("whatsapp", __name__, url_prefix="/whatsapp")

VERIFY_TOKEN = os.getenv("WA_VERIFY_TOKEN", "acms_verify_token")
ACCESS_TOKEN = os.getenv("WA_ACCESS_TOKEN")          # leave empty → feature disabled
PHONE_ID     = os.getenv("WA_PHONE_ID")              # numeric string

def send_whatsapp(to:str, text:str):
    if not ACCESS_TOKEN:
        logging.warning("WhatsApp disabled – no ACCESS_TOKEN")
        return
    url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}",
               "Content-Type": "application/json"}
    payload = {"messaging_product":"whatsapp",
               "to": to, "type":"text", "text":{"body": text}}
    requests.post(url, headers=headers, json=payload, timeout=10)

@whatsapp_bp.route("/webhook", methods=["GET","POST"])
def webhook():
    # -- Verification (GET) --
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        return "Invalid verify token", 403
    # -- Incoming messages (POST) --
    data = request.get_json()
    try:
        entry = data["entry"][0]["changes"][0]["value"]["messages"][0]
        sender = entry["from"]
        text   = entry["text"]["body"]
        # Simple echo or feed to the chatbot
        from app.utils.chatbot import get_response
        reply = get_response(text)
        send_whatsapp(sender, reply)
    except Exception as e:
        logging.exception("WA webhook error")
    return "OK", 200