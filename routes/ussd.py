from flask import Blueprint, request

ussd_bp = Blueprint("ussd", __name__)

@ussd_bp.route("/ussd", methods=["POST"])
def ussd():
    return "END USSD Connected Successfully"