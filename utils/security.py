from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password is too long (max 72 bytes)")
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password is too long (max 72 bytes)")
    return pwd_context.verify(password, hashed_password)



