from __future__ import annotations

import re
import unicodedata


def text(value: str | None) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    without_marks = "".join(char for char in normalized if not unicodedata.combining(char))
    compact = re.sub(r"[^a-z0-9]+", " ", without_marks.casefold())
    return " ".join(compact.split())


def email(value: str | None) -> str:
    candidate = (value or "").strip().casefold()
    if candidate.count("@") != 1:
        return ""
    local, domain = candidate.split("@")
    domain = domain.removeprefix("www.")
    return f"{local}@{domain}" if local and "." in domain else ""


def phone(value: str | None) -> str:
    digits = re.sub(r"\D", "", value or "")
    if len(digits) < 7:
        return ""
    if len(digits) == 10:
        return "1" + digits
    if digits.startswith("00"):
        return digits[2:]
    return digits


def company(value: str | None) -> str:
    words = text(value).split()
    legal_suffixes = {"llc", "ltd", "limited", "inc", "corp", "corporation", "gmbh", "plc"}
    return " ".join(word for word in words if word not in legal_suffixes)

