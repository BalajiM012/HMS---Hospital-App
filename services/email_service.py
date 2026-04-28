from flask_mail import Message
from app import mail

def send_email(to, subject, body):
    msg = Message(
        subject=subject,
        recipients=[to]
    )
    msg.body = body
    mail.send(msg)
