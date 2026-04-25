import os
import jwt
from datetime import datetime, timedelta
from config.settings import Settings


def create_access_token(payload):
    now = datetime.utcnow()
    token_payload = {
        'exp': now + timedelta(minutes=Settings.ACCESS_TOKEN_EXPIRES_MINUTES),
        'iat': now,
        'nbf': now,
        **payload,
    }
    return jwt.encode(token_payload, Settings.JWT_SECRET_KEY, algorithm=Settings.JWT_ALGORITHM)


def decode_access_token(token):
    try:
        return jwt.decode(token, Settings.JWT_SECRET_KEY, algorithms=[Settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError('Token has expired')
    except jwt.InvalidTokenError:
        raise ValueError('Invalid token')
