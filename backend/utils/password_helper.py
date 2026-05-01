import bcrypt


def hash_password(raw_password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')


def check_password(raw_password: str, password_hash: str) -> bool:
    if not raw_password or not password_hash:
        return False
    return bcrypt.checkpw(raw_password.encode('utf-8'), password_hash.encode('utf-8'))
