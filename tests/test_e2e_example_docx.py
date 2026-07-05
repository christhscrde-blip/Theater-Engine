from pathlib import Path

from docx import Document

from src.pipeline import format_docx
from src.verifier import assert_visible_text_unchanged, visible_text_hash


def _write_mini_theater_scene(path: Path) -> None:
    doc = Document()
    for text in _mini_theater_scene_paragraphs():
        doc.add_paragraph(text)
    doc.save(path)


def _mini_theater_scene_paragraphs() -> list[str]:
    return [
        "Erster Akt",
        "1. Szene",
        "Großer Saal im Stadttheater.",
        "FIGUR A.",
        "Aber ist Euch auch wohl, Vater?",
        "FIGUR B (leise).",
        "Nachrichten von meiner Schwester?",
        "Seite 1",
    ]


def test_format_docx_keeps_visible_text_for_generated_mini_scene(tmp_path: Path):
    input_docx = tmp_path / "mini_scene.docx"
    output_docx = tmp_path / "mini_scene_formatted.docx"
    _write_mini_theater_scene(input_docx)
    before_hash = visible_text_hash(input_docx)

    report = format_docx(input_docx, output_docx)

    assert report.output_file == output_docx
    assert output_docx.exists()
    assert report.visible_text_integrity is True
    assert visible_text_hash(output_docx) == before_hash
    assert_visible_text_unchanged(input_docx, output_docx)
