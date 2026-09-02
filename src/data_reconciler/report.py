from __future__ import annotations

import csv
import html
import json
from dataclasses import asdict
from pathlib import Path

from .reconcile import ReconciliationResult


def write_outputs(result: ReconciliationResult, output_dir: str | Path) -> None:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    with (destination / "reconciliation.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["incoming_row", "master_row", "status", "score", "reasons", "name", "email", "phone", "company"],
        )
        writer.writeheader()
        for row in result.rows:
            writer.writerow(
                {
                    "incoming_row": row.incoming_row,
                    "master_row": row.master_row or "",
                    "status": row.status,
                    "score": f"{row.score:.4f}",
                    "reasons": "; ".join(row.reasons),
                    **{key: row.incoming.get(key, "") for key in ("name", "email", "phone", "company")},
                }
            )
    (destination / "audit.json").write_text(
        json.dumps([asdict(row) for row in result.rows], indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (destination / "report.html").write_text(_html_report(result), encoding="utf-8")


def _html_report(result: ReconciliationResult) -> str:
    rows = []
    for item in result.rows:
        values = [
            item.incoming_row,
            item.master_row or "—",
            item.incoming.get("name", ""),
            item.incoming.get("email", ""),
            item.status,
            f"{item.score:.0%}",
            "; ".join(item.reasons),
        ]
        cells = "".join(f"<td>{html.escape(str(value))}</td>" for value in values)
        rows.append(f'<tr class="{item.status}">{cells}</tr>')
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Reconciliation report</title>
<style>body{{font:15px system-ui;margin:0;background:#f3f6fb;color:#182338}}main{{max-width:1200px;margin:40px auto;padding:0 24px}}h1{{font-size:38px}}.cards{{display:flex;gap:16px;margin:24px 0}}.card{{background:white;padding:20px 28px;border-radius:14px;box-shadow:0 8px 24px #20304a12}}.card b{{display:block;font-size:30px}}table{{width:100%;border-collapse:collapse;background:white;border-radius:14px;overflow:hidden;box-shadow:0 8px 24px #20304a12}}th,td{{padding:13px;text-align:left;border-bottom:1px solid #e8edf5}}th{{background:#13233c;color:white}}.matched td:nth-child(5){{color:#087b4d;font-weight:700}}.ambiguous td:nth-child(5){{color:#a76600;font-weight:700}}.unmatched td:nth-child(5){{color:#bd2945;font-weight:700}}</style></head>
<body><main><h1>Data reconciliation report</h1><p>Explainable record matching with a complete audit trail.</p><div class="cards"><div class="card"><b>{len(result.rows)}</b>Incoming</div><div class="card"><b>{result.matched}</b>Matched</div><div class="card"><b>{result.ambiguous}</b>Review</div><div class="card"><b>{result.unmatched}</b>Unmatched</div></div><table><thead><tr><th>Incoming row</th><th>Master row</th><th>Name</th><th>Email</th><th>Status</th><th>Score</th><th>Evidence</th></tr></thead><tbody>{''.join(rows)}</tbody></table></main></body></html>"""

