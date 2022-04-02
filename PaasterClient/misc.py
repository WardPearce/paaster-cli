def end_slash(value: str) -> str:
    if not value.endswith("/"):
        value += "/"
    return value
