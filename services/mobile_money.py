import os

def send_money(phone, amount):

    print(
        f"SENDING KES {amount} TO {phone}"
    )

    return True, {
        "status": "Success",
        "reference": "PAYROLL123"
    }