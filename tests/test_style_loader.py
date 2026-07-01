from pathlib import Path

import pytest

from src.models import TextSpanType
from src.style_engine import StyleEngine, load_style_engine
from src.style_loader import (
    StyleLoaderError,
    load_style_sheet,
    load_style_sheet_from_text,
)
from src.style_models import TextAlignment

VALID_STYLE = """
name: test-style
defaults:
  font_family: Test Serif
  font_size: 11
  bold: false
  italic: false
  underline: false
  text_color: "#112233"
  highlight_color: null
  alignment: left
  left_indent: 0
  right_indent: 0
  first_line_indent: 0
  spacing_before: 0
  spacing_after: 6
  line_spacing: 1.15
styles:
  speaker:
    italic: true
    text_color: "#445566"
  inline_stage:
    italic: true
"""


def test_valid_style_loading_merges_defaults():
    sheet = load_style_sheet_from_text(VALID_STYLE)

    speaker = sheet.style_for(TextSpanType.SPEAKER)
    assert sheet.name == "test-style"
    assert speaker.font_family == "Test Serif"
    assert speaker.font_size == 11.0
    assert speaker.italic is True
    assert speaker.text_color == "#445566"
    assert speaker.alignment == TextAlignment.LEFT


def test_style_loader_rejects_invalid_yaml():
    with pytest.raises(StyleLoaderError, match="Invalid YAML"):
        load_style_sheet_from_text("name: [broken")


def test_style_loader_rejects_missing_required_default_fields():
    with pytest.raises(StyleLoaderError, match="missing required fields: line_spacing"):
        load_style_sheet_from_text("""
name: incomplete
defaults:
  font_family: Test Serif
  font_size: 11
  bold: false
  italic: false
  underline: false
  text_color: "#112233"
  highlight_color: null
  alignment: left
  left_indent: 0
  right_indent: 0
  first_line_indent: 0
  spacing_before: 0
  spacing_after: 6
styles: {}
""")


def test_style_loader_rejects_invalid_color_values():
    with pytest.raises(StyleLoaderError, match="text_color"):
        load_style_sheet_from_text(VALID_STYLE.replace("#112233", "blue"))


def test_style_loader_rejects_invalid_alignment_values():
    with pytest.raises(StyleLoaderError, match="alignment"):
        load_style_sheet_from_text(
            VALID_STYLE.replace("alignment: left", "alignment: diagonal")
        )


def test_style_loader_rejects_unknown_span_type():
    with pytest.raises(StyleLoaderError, match="invalid span type"):
        load_style_sheet_from_text(VALID_STYLE.replace("speaker:", "unknown_span:"))


def test_style_sheet_falls_back_to_defaults_for_missing_span_type():
    sheet = load_style_sheet_from_text(VALID_STYLE)

    plain = sheet.style_for(TextSpanType.PLAIN)
    assert plain.font_family == "Test Serif"
    assert plain.text_color == "#112233"
    assert plain.italic is False


def test_style_engine_lookup_uses_configured_span_style():
    sheet = load_style_sheet_from_text(VALID_STYLE)
    engine = StyleEngine(sheet)

    style = engine.get_style(TextSpanType.INLINE_STAGE)

    assert style.italic is True
    assert style.text_color == "#112233"


def test_load_style_engine_from_file(tmp_path: Path):
    style_path = tmp_path / "style.yaml"
    style_path.write_text(VALID_STYLE, encoding="utf-8")

    engine = load_style_engine(style_path)

    assert engine.get_style(TextSpanType.SPEAKER).text_color == "#445566"


def test_repository_style_files_load():
    for style_path in Path("styles").glob("*.yaml"):
        sheet = load_style_sheet(style_path)
        assert sheet.name == style_path.stem
        assert sheet.style_for(TextSpanType.REPLIQUE).font_family
