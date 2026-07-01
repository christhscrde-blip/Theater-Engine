from dataclasses import replace

import pytest

from src.document_model import build_document_model_from_texts
from src.formatting_plan import FormattingPlanError, build_formatting_plan
from src.models import TextSpanType
from src.style_engine import StyleEngine
from src.style_loader import load_style_sheet_from_text

STYLE = """
name: plan-test
defaults:
  font_family: Test Serif
  font_size: 11
  bold: false
  italic: false
  underline: false
  text_color: "#111111"
  highlight_color: null
  alignment: left
  left_indent: 0
  right_indent: 0
  first_line_indent: 0
  spacing_before: 0
  spacing_after: 0
  line_spacing: 1.0
styles:
  speaker:
    bold: true
    text_color: "#222222"
  replique:
    text_color: "#000000"
  inline_stage:
    italic: true
    text_color: "#777777"
"""


def make_engine() -> StyleEngine:
    return StyleEngine(load_style_sheet_from_text(STYLE))


def test_formatting_plan_preserves_document_visible_text_and_hash():
    texts = ["Franz.", "Aber ist Euch wohl? (nimmt den Brief)"]
    model = build_document_model_from_texts(texts, source_file="memory")

    plan = build_formatting_plan(model, make_engine())

    assert plan.source_file == "memory"
    assert plan.style_name == "plan-test"
    assert plan.paragraph_count == model.paragraph_count
    assert plan.visible_text == model.visible_text
    assert plan.visible_text_sha256 == model.visible_text_sha256
    assert plan.has_integrity


def test_formatting_plan_assigns_styles_per_span_type():
    model = build_document_model_from_texts(["Franz. Hallo (leise)"])

    plan = build_formatting_plan(model, make_engine())
    runs = plan.paragraphs[0].runs

    assert [run.span_type for run in runs] == [
        TextSpanType.SPEAKER,
        TextSpanType.REPLIQUE,
        TextSpanType.INLINE_STAGE,
    ]
    assert runs[0].style.bold is True
    assert runs[1].style.text_color == "#000000"
    assert runs[2].style.italic is True


def test_formatting_plan_falls_back_to_default_style_for_unconfigured_span_type():
    model = build_document_model_from_texts(["Ein unklarer Absatz ohne Kontext"])

    plan = build_formatting_plan(model, make_engine())
    run = plan.paragraphs[0].runs[0]

    assert run.span_type == TextSpanType.PLAIN
    assert run.style.text_color == "#111111"
    assert plan.paragraphs[0].needs_manual_review
    assert plan.manual_review_paragraphs == (plan.paragraphs[0],)


def test_formatting_plan_rejects_invalid_document_model_hash():
    model = build_document_model_from_texts(["Franz."])
    broken_model = replace(model, visible_text_sha256="0" * 64)

    with pytest.raises(FormattingPlanError, match="DocumentModel integrity"):
        build_formatting_plan(broken_model, make_engine())
