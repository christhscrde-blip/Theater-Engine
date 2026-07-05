from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .models import AnalysisReport, ClassifiedParagraph


@dataclass(frozen=True)
class FormattingReport:
    source_file: Path
    output_file: Path
    runtime_seconds: float
    paragraph_count: int
    classified_paragraph_count: int
    manual_review_count: int
    validation_warning_count: int
    validation_error_count: int
    visible_text_integrity: bool
    output_hash: str


def ensure_dir(path: str | Path) -> Path:
    target = Path(path)
    target.mkdir(parents=True, exist_ok=True)
    return target


def write_analysis_report(report: AnalysisReport, out_dir: str | Path) -> Path:
    out = ensure_dir(out_dir) / "analysis_report.json"
    out.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def write_classification_csv(paragraphs: list[ClassifiedParagraph], out_dir: str | Path) -> Path:
    out = ensure_dir(out_dir) / "paragraph_classification.csv"
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "index",
                "type",
                "speaker",
                "text_preview",
                "difficult_words",
                "flags",
                "note",
            ],
        )
        writer.writeheader()
        for item in paragraphs:
            writer.writerow(
                {
                    "index": item.index,
                    "type": item.type.value,
                    "speaker": item.speaker,
                    "text_preview": item.text.strip()[:220],
                    "difficult_words": "; ".join(item.difficult_words),
                    "flags": "; ".join(item.flags),
                    "note": item.note,
                }
            )
    return out
