from flask_mail import Message
from flask import url_for, current_app
from extensions import mail

def send_setup_email(user, raw_token):
    setup_url = url_for(
        "auth.setup_account",
        token=raw_token,
        _external=True
    )

    msg = Message(
        subject="Set your password",
        recipients=[user.email],
        body=f"""
Hello {user.username},

Your account has been created.

Click the link below to set your password (valid for 24 hours):

{setup_url}

If you didn’t request this, ignore this email.
"""
    )

    mail.send(msg)
