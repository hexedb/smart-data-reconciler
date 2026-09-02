from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from difflib import SequenceMatcher

from .normalize import company, email, phone, text


@dataclass(frozen=True, slots=True)
class MatchScore:
    score: float
    reasons: tuple[str, ...]


def compare(left: Mapping[str, str], right: Mapping[str, str]) -> MatchScore:
    reasons: list[str] = []
    weighted: list[tuple[float, float]] = []

    left_email, right_email = email(left.get("email")), email(right.get("email"))
    if left_email and right_email:
        exact = float(left_email == right_email)
        weighted.append((exact, 0.42))
        if exact:
            reasons.append("exact email")

    left_phone, right_phone = phone(left.get("phone")), phone(right.get("phone"))
    if left_phone and right_phone:
        exact = float(left_phone == right_phone)
        weighted.append((exact, 0.33))
        if exact:
            reasons.append("exact phone")

    left_name, right_name = text(left.get("name")), text(right.get("name"))
    if left_name and right_name:
        similarity = SequenceMatcher(None, left_name, right_name).ratio()
        weighted.append((similarity, 0.18))
        if similarity >= 0.86:
            reasons.append(f"similar name {similarity:.0%}")

    left_company, right_company = company(left.get("company")), company(right.get("company"))
    if left_company and right_company:
        similarity = SequenceMatcher(None, left_company, right_company).ratio()
        weighted.append((similarity, 0.07))
        if similarity >= 0.86:
            reasons.append(f"similar company {similarity:.0%}")

    if not weighted:
        return MatchScore(0.0, ("no comparable fields",))
    total_weight = sum(weight for _, weight in weighted)
    score = sum(value * weight for value, weight in weighted) / total_weight
    return MatchScore(round(score, 4), tuple(reasons) or ("weak field agreement",))
