#!/usr/bin/env python3
import argparse
from pathlib import Path

from humility_engine import analyze_document, render_markdown


def main() -> int:
    parser = argparse.ArgumentParser(description="Review a Markdown draft for uncertainty laundering and proofwashing.")
    parser.add_argument("input", nargs="?", default="examples/input.md", help="Markdown/text draft to review.")
    parser.add_argument("--evidence", default="examples/evidence.md", help="Optional evidence notes file.")
    parser.add_argument("--output", default="examples/output.md", help="Markdown output path.")
    parser.add_argument(
        "--review-only",
        "--no-rewrite",
        action="store_true",
        help="Write only the claim review table and boundary note. Recommended for full Markdown documents.",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    evidence_path = Path(args.evidence)
    output_path = Path(args.output)

    draft_text = input_path.read_text(encoding="utf-8")
    evidence_text = evidence_path.read_text(encoding="utf-8") if evidence_path.exists() else ""
    review = analyze_document(draft_text, evidence_text)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(review, review_only=args.review_only), encoding="utf-8")
    print(f"Wrote {output_path}")
    print(f"Reviewed {len(review['claims'])} claim(s)")
    if args.review_only:
        print("Review-only mode: revised draft section suppressed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
