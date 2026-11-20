import re

def normalize_phone(raw: str) -> str | None:
    value: str = re.sub(r"[\s\-()]", "", raw.strip())
    if re.fullmatch(r"\+?\d{9,15}", value):
        return value
    return None