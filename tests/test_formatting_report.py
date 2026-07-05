from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from src.report import FormattingReport


def test_formatting_report_is_immutable():
    report = FormattingReport(
        source_file=Path("input.docx"),
        output_file=Path("output.docx"),
        runtime_seconds=0.1,
        paragraph_count=1,
        classified_paragraph_count=1,
        manual_review_count=0,
        validation_warning_count=0,
        validation_error_count=0,
        visible_text_integrity=True,
        output_hash="abc123",
    )

    with pytest.raises(FrozenInstanceError):
        report.output_hash = "changed"
