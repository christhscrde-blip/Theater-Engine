from pathlib import Path

from docx import Document

from src.pipeline import format_docx
from src.report import FormattingReport
from src.verifier import assert_visible_text_unchanged, visible_text_hash


def make_docx(path: Path, paragraphs: list[str]) -> None:
    doc = Document()
    for paragraph in paragraphs:
        doc.add_paragraph(paragraph)
    doc.save(path)


def test_format_docx_renders_output_without_changing_visible_text(tmp_path: Path):
    input_docx = tmp_path / "input.docx"
    output_docx = tmp_path / "output.docx"
    make_docx(input_docx, ["FIGUR A. Hallo (leise)"])
    before_hash = visible_text_hash(input_docx)

    report = format_docx(input_docx, output_docx, Path("styles/theater.yaml"))

    assert isinstance(report, FormattingReport)
    assert report.source_file == input_docx
    assert report.output_file == output_docx
    assert report.runtime_seconds >= 0
    assert report.paragraph_count == 1
    assert report.classified_paragraph_count == 1
    assert report.manual_review_count == 0
    assert report.validation_warning_count == 0
    assert report.validation_error_count == 0
    assert report.visible_text_integrity is True
    assert output_docx.exists()
    assert visible_text_hash(output_docx) == before_hash
    assert report.output_hash == before_hash
    assert_visible_text_unchanged(input_docx, output_docx)
