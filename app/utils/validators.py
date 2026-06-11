import re


def validate_phone(phone: str) -> bool:
    """校验中国大陆手机号"""
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
