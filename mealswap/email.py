from mealswap.extensions import mail
from mealswap.controllers.user.token import generate_confirmation_token
from flask import url_for, render_template
from flask_mail import Message
from mealswap.settings import MAIL_DEFAULT_SENDER


def send_confirmation_msg(email: str, name: str) -> None:
    """
    Sends email with confirmation token to unlock the account.

    :param str email: user's email
    :param str name: user's name
    :return: None
    """
    token = generate_confirmation_token(email)
    confirm_url = url_for('user.confirm_email', token=token, _external=True)
    html = render_template('mail/activate.html', confirm_url=confirm_url, name=name)
    subject = "Please confirm your email for Mealswap"

    msg = Message(subject=subject,
                  sender=MAIL_DEFAULT_SENDER,
                  recipients=[email],
                  html=html)
    mail.send(msg)

    return None
