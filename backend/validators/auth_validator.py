import re

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PASSWORD_MIN_LENGTH = 10
PASSWORD_COMPLEXITY_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).+$')


def validate_email(email):
    if not email or not isinstance(email, str) or not EMAIL_REGEX.match(email):
        raise ValueError('A valid email address is required')
    return email.strip().lower()


def validate_password(password):
    if not password or not isinstance(password, str) or len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(f'Password must be at least {PASSWORD_MIN_LENGTH} characters long')
    if not PASSWORD_COMPLEXITY_REGEX.match(password):
        raise ValueError('Password must include upper and lower case letters, a number, and a symbol')
    return password


def validate_signup_payload(email, password):
    return {
        'email': validate_email(email),
        'password': validate_password(password),
    }


def validate_login_payload(email, password):
    if not email or not password:
        raise ValueError('Email and password are required')
    return {
        'email': validate_email(email),
        'password': password,
    }
