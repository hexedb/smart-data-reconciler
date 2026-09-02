from __future__ import annotations

import argparse

from .reconcile import read_csv, reconcile
from .report import write_outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reconcile an incoming CSV against a master CSV")
    parser.add_argument("master", help="canonical/master CSV")
    parser.add_argument("incoming", help="incoming CSV to match")
    parser.add_argument("--output", default="output", help="output directory")
    parser.add_argument("--threshold", type=float, default=0.78, help="automatic match threshold")
    parser.add_argument("--ambiguity-margin", type=float, default=0.06, help="minimum lead over second candidate")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = reconcile(
        read_csv(args.master),
        read_csv(args.incoming),
        match_threshold=args.threshold,
        ambiguity_margin=args.ambiguity_margin,
    )
    write_outputs(result, args.output)
    print(
        f"Processed {len(result.rows)} rows: {result.matched} matched, "
        f"{result.ambiguous} need review, {result.unmatched} unmatched."
    )
    print(f"Reports written to {args.output}")


if __name__ == "__main__":
    main()

