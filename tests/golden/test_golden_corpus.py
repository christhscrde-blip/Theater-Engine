from __future__ import annotations

from pathlib import Path

import pytest

from src.pipeline import format_docx
from src.verifier import assert_visible_text_unchanged, visible_text_hash

from .corpus import GOLDEN_DOCUMENTS, GoldenDocument, build_regression_summary


REQUIRED_COVERAGE = {
    "modern layout",
    "classic layout",
    "OCR spacing issues",
    "Roman numerals",
    "long stage directions",
    "multiple speakers",
    "inline stage directions",
    "empty pages",
    "page breaks",
    "unusual indentation",
}


@pytest.mark.parametrize(
    "golden_document",
    GOLDEN_DOCUMENTS,
    ids=[document.name for document in GOLDEN_DOCUMENTS],
)
def test_golden_document_formats_without_text_changes(
    tmp_path: Path, golden_document: GoldenDocument
):
    input_docx = tmp_path / f"{golden_document.name}.docx"
    output_docx = tmp_path / f"{golden_document.name}.formatted.docx"
    golden_document.write_docx(input_docx)
    before_hash = visible_text_hash(input_docx)

    report = format_docx(input_docx, output_docx)

    assert output_docx.exists()
    assert report.visible_text_integrity is True
    assert report.validation_error_count == 0
    assert visible_text_hash(output_docx) == before_hash
    assert_visible_text_unchanged(input_docx, output_docx)


def test_golden_corpus_covers_required_layout_variants():
    covered = {
        item
        for golden_document in GOLDEN_DOCUMENTS
        for item in golden_document.coverage
    }

    assert len(GOLDEN_DOCUMENTS) >= 10
    assert REQUIRED_COVERAGE <= covered


def test_golden_corpus_produces_regression_summary(tmp_path: Path):
    results = []
    for golden_document in GOLDEN_DOCUMENTS:
        input_docx = tmp_path / f"{golden_document.name}.docx"
        output_docx = tmp_path / f"{golden_document.name}.formatted.docx"
        golden_document.write_docx(input_docx)

        report = format_docx(input_docx, output_docx)

        assert output_docx.exists()
        assert report.visible_text_integrity is True
        assert report.validation_error_count == 0
        assert_visible_text_unchanged(input_docx, output_docx)
        results.append((golden_document, report))

    summary = build_regression_summary(results)

    assert "Golden regression summary" in summary
    assert f"documents: {len(GOLDEN_DOCUMENTS)}" in summary
    for golden_document in GOLDEN_DOCUMENTS:
        assert golden_document.name in summary
