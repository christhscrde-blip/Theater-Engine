from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from .classifier import build_report, classify_docx
from .pipeline import format_docx
from .report import FormattingReport, write_analysis_report, write_classification_csv
from .validation import InvalidFormattingPlan


def analyse_command(args: argparse.Namespace) -> int:
    docx_path = Path(args.docx)
    paragraphs = classify_docx(docx_path)
    report = build_report(docx_path, paragraphs)

    out_dir = Path(args.out)
    report_path = write_analysis_report(report, out_dir)
    csv_path = write_classification_csv(paragraphs, out_dir)

    print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    print(f"Analysebericht: {report_path}")
    print(f"Absatzklassifikation: {csv_path}")
    return 0


def format_command(args: argparse.Namespace) -> int:
    try:
        report = format_docx(args.input_docx, args.output_docx, args.style)
    except InvalidFormattingPlan as error:
        print(f"Validation error: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        if _is_integrity_error(error):
            print(f"Integrity error: {error}", file=sys.stderr)
            return 1
        print(f"Unexpected runtime error: {error}", file=sys.stderr)
        return 2
    except Exception as error:  # noqa: BLE001 - CLI must convert unexpected errors to exit code 2.
        print(f"Unexpected runtime error: {error}", file=sys.stderr)
        return 2

    print(_format_report(report))
    if not report.visible_text_integrity or report.validation_error_count > 0:
        return 1
    return 0


def _is_integrity_error(error: ValueError) -> bool:
    return "sichtbare Text wurde verändert" in str(error)


def _format_report(report: FormattingReport) -> str:
    lines = [
        "Formatting report",
        f"Source file: {report.source_file}",
        f"Output file: {report.output_file}",
        f"Runtime seconds: {report.runtime_seconds:.3f}",
        f"Paragraph count: {report.paragraph_count}",
        f"Manual review count: {report.manual_review_count}",
        f"Validation warning count: {report.validation_warning_count}",
        f"Validation error count: {report.validation_error_count}",
        f"Visible text integrity: {_format_bool(report.visible_text_integrity)}",
        f"Output hash: {report.output_hash}",
    ]
    return "\n".join(lines)


def _format_bool(value: bool) -> str:
    return "ok" if value else "failed"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="theater-formatierung")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyse = subparsers.add_parser("analyse", help="DOCX analysieren und Berichte schreiben")
    analyse.add_argument("docx", help="Pfad zur DOCX-Datei")
    analyse.add_argument("--out", default="reports", help="Ausgabeordner für Berichte")
    analyse.set_defaults(func=analyse_command)

    formatter = subparsers.add_parser("format", help="DOCX formatieren")
    formatter.add_argument("input_docx", help="Pfad zur Eingabe-DOCX-Datei")
    formatter.add_argument("output_docx", help="Pfad zur Ausgabe-DOCX-Datei")
    formatter.add_argument("--style", default=None, help="Optionaler Pfad zur Style-YAML-Datei")
    formatter.set_defaults(func=format_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
