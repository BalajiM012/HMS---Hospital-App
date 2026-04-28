from flask_mail import Message
from flask import current_app
from app import mail

def send_email(to, subject, body):
    msg = Message(subject,
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[to])
    msg.body = body
    mail.send(msg)
