from __future__ import annotations

from pathlib import Path

from docx import Document

from src import cli
from src.verifier import assert_visible_text_unchanged, visible_text_hash


def make_docx(path: Path, paragraphs: list[str]) -> None:
    doc = Document()
    for paragraph in paragraphs:
        doc.add_paragraph(paragraph)
    doc.save(path)


def test_format_command_writes_output_and_prints_report(tmp_path: Path, capsys):
    input_docx = tmp_path / "input.docx"
    output_docx = tmp_path / "output.docx"
    make_docx(input_docx, ["FIGUR A.", "Hallo."])
    before_hash = visible_text_hash(input_docx)

    exit_code = cli.main(["format", str(input_docx), str(output_docx)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert output_docx.exists()
    assert "Formatting report" in captured.out
    assert f"Source file: {input_docx}" in captured.out
    assert f"Output file: {output_docx}" in captured.out
    assert "Runtime seconds:" in captured.out
    assert "Paragraph count: 2" in captured.out
    assert "Manual review count: 0" in captured.out
    assert "Validation warning count: 0" in captured.out
    assert "Validation error count: 0" in captured.out
    assert "Visible text integrity: ok" in captured.out
    assert f"Output hash: {before_hash}" in captured.out
    assert visible_text_hash(output_docx) == before_hash
    assert_visible_text_unchanged(input_docx, output_docx)


def test_format_command_accepts_optional_style_path(tmp_path: Path, capsys):
    input_docx = tmp_path / "input.docx"
    output_docx = tmp_path / "output.docx"
    make_docx(input_docx, ["FIGUR A. Hallo (leise)"])
    before_hash = visible_text_hash(input_docx)

    exit_code = cli.main(
        [
            "format",
            str(input_docx),
            str(output_docx),
            "--style",
            "styles/theater.yaml",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Formatting report" in captured.out
    assert visible_text_hash(output_docx) == before_hash
    assert_visible_text_unchanged(input_docx, output_docx)


def test_format_command_returns_runtime_error_for_missing_input(tmp_path: Path, capsys):
    missing_docx = tmp_path / "missing.docx"
    output_docx = tmp_path / "output.docx"

    exit_code = cli.main(["format", str(missing_docx), str(output_docx)])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Unexpected runtime error:" in captured.err
    assert not output_docx.exists()
