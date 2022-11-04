from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from mealswap.settings import SECURITY_PASSWORD_SALT, SECRET_KEY


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=SECURITY_PASSWORD_SALT)


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(
            token,
            salt=SECURITY_PASSWORD_SALT,
            max_age=expiration
        )
    except SignatureExpired or BadSignature:
        return False
    return email
