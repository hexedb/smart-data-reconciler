from __future__ import annotations

import csv
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .matcher import compare
from .normalize import email, phone


@dataclass(frozen=True, slots=True)
class Candidate:
    incoming_row: int
    master_row: int | None
    score: float
    status: str
    reasons: tuple[str, ...]
    incoming: dict[str, str]
    master: dict[str, str] | None


@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    rows: tuple[Candidate, ...]

    @property
    def matched(self) -> int:
        return sum(row.status == "matched" for row in self.rows)

    @property
    def ambiguous(self) -> int:
        return sum(row.status == "ambiguous" for row in self.rows)

    @property
    def unmatched(self) -> int:
        return sum(row.status == "unmatched" for row in self.rows)


def read_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path} has no header row")
        required = {"name", "email", "phone", "company"}
        missing = required - {name.strip().casefold() for name in reader.fieldnames}
        if missing:
            raise ValueError(f"{path} is missing columns: {', '.join(sorted(missing))}")
        return [
            {str(key).strip().casefold(): (value or "").strip() for key, value in row.items()}
            for row in reader
        ]


def reconcile(
    master: Iterable[dict[str, str]],
    incoming: Iterable[dict[str, str]],
    *,
    match_threshold: float = 0.78,
    ambiguity_margin: float = 0.06,
) -> ReconciliationResult:
    master_rows = list(master)
    email_index: dict[str, set[int]] = {}
    phone_index: dict[str, set[int]] = {}
    for index, row in enumerate(master_rows):
        if value := email(row.get("email")):
            email_index.setdefault(value, set()).add(index)
        if value := phone(row.get("phone")):
            phone_index.setdefault(value, set()).add(index)

    output: list[Candidate] = []
    for incoming_index, row in enumerate(incoming, start=2):
        candidate_ids = set()
        if value := email(row.get("email")):
            candidate_ids.update(email_index.get(value, set()))
        if value := phone(row.get("phone")):
            candidate_ids.update(phone_index.get(value, set()))
        if not candidate_ids:
            candidate_ids = set(range(len(master_rows)))
        ranked = sorted(
            ((compare(row, master_rows[index]), index) for index in candidate_ids),
            key=lambda item: item[0].score,
            reverse=True,
        )
        best_score, best_index = ranked[0] if ranked else (None, None)
        if best_score is None or best_score.score < match_threshold:
            output.append(Candidate(incoming_index, None, best_score.score if best_score else 0, "unmatched", best_score.reasons if best_score else ("master is empty",), row, None))
            continue
        second_score = ranked[1][0].score if len(ranked) > 1 else 0.0
        status = "ambiguous" if best_score.score - second_score < ambiguity_margin else "matched"
        output.append(
            Candidate(
                incoming_index,
                best_index + 2,
                best_score.score,
                status,
                best_score.reasons,
                row,
                master_rows[best_index],
            )
        )
    return ReconciliationResult(tuple(output))
