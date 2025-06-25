# app/routes/chatbot.py

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from app.utils.chatbot import get_response

chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/chatbot")

@chatbot_bp.route("/")
@login_required
def chat():
    return render_template("chatbot.html")

@chatbot_bp.route("/ask", methods=["POST"])
@login_required
def ask():
    user_msg  = request.json.get("message", "")
    reply     = get_response(user_msg)
    return jsonify({"reply": reply})
