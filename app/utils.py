from flask_mail import Message
from firebase_admin import messaging
from . import mail

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender="noreply@stonks.com"
    )
    mail.send(msg)


def send_push_notification(tokens, title, body):
    if not isinstance(tokens, list):
        tokens = [tokens]

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        tokens=tokens,
    )
    response = messaging.send_multicast(message)
    print('Successfully sent message:', response.success_count)
