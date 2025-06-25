from flask import Blueprint, request, jsonify
from app.utils.sms import send_sms

sms_test_bp = Blueprint('sms_test', __name__)

@sms_test_bp.route('/sms/test', methods=['GET'])
def test_sms():
    # Replace with your test recipient
    recipient = "+263783779971"
    message = "Hello from ACMS via Africa's Talking!"
    result = send_sms(recipient, message)
    return jsonify(result)
