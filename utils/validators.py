import re

def validate_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    pattern = r"^\+?[0-9\s\-]{7,15}$"
    return bool(re.match(pattern, phone))

def validate_float(value: str) -> bool:
    try:
        f = float(value)
        return f >= 0
    except ValueError:
        return False
