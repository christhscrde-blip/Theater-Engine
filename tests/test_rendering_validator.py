from dataclasses import replace

from src.document_model import build_document_model_from_texts
from src.formatting_plan import build_formatting_plan
from src.validation import (
    DuplicateParagraph,
    InvalidFormattingPlan,
    InvalidParagraph,
    InvalidSpan,
    MissingStyle,
    OverlappingSpan,
    UnknownStyle,
    validate_formatting_plan,
)
from src.style_engine import StyleEngine
from src.style_loader import load_style_sheet_from_text

STYLE = """
name: validation-test
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
  replique:
    text_color: "#000000"
  inline_stage:
    italic: true
"""


def make_plan():
    model = build_document_model_from_texts(["FIGUR A. Hallo (leise)"])
    style_sheet = load_style_sheet_from_text(STYLE)
    return build_formatting_plan(model, StyleEngine(style_sheet)), style_sheet


def first_error_of_type(report, error_type):
    return next(error for error in report.errors if isinstance(error, error_type))


def test_valid_plan_returns_report_with_statistics():
    plan, style_sheet = make_plan()

    report = validate_formatting_plan(plan, style_sheet)

    assert report.valid is True
    assert report.errors == ()
    assert report.statistics.paragraph_count == 1
    assert report.statistics.run_count == 3


def test_duplicate_paragraph_is_rejected():
    plan, style_sheet = make_plan()
    duplicate = replace(plan.paragraphs[0], index=plan.paragraphs[0].index)
    broken = replace(plan, paragraphs=(plan.paragraphs[0], duplicate))

    report = validate_formatting_plan(broken, style_sheet)

    assert report.valid is False
    assert isinstance(
        first_error_of_type(report, DuplicateParagraph), DuplicateParagraph
    )


def test_overlapping_spans_are_rejected():
    plan, style_sheet = make_plan()
    paragraph = plan.paragraphs[0]
    overlapping_run = replace(paragraph.runs[1], start_offset=0)
    broken_paragraph = replace(
        paragraph, runs=(paragraph.runs[0], overlapping_run, paragraph.runs[2])
    )
    broken = replace(plan, paragraphs=(broken_paragraph,))

    report = validate_formatting_plan(broken, style_sheet)

    assert report.valid is False
    assert isinstance(first_error_of_type(report, OverlappingSpan), OverlappingSpan)


def test_non_continuous_span_order_is_rejected():
    plan, style_sheet = make_plan()
    paragraph = plan.paragraphs[0]
    broken_run = replace(paragraph.runs[1], span_index=3)
    broken = replace(
        plan,
        paragraphs=(
            replace(paragraph, runs=(paragraph.runs[0], broken_run, paragraph.runs[2])),
        ),
    )

    report = validate_formatting_plan(broken, style_sheet)

    assert report.valid is False
    assert isinstance(first_error_of_type(report, InvalidSpan), InvalidSpan)


def test_invalid_alignment_is_rejected():
    plan, style_sheet = make_plan()
    paragraph = plan.paragraphs[0]
    broken_style = replace(paragraph.runs[0].style, alignment="diagonal")
    broken_run = replace(paragraph.runs[0], style=broken_style)
    broken = replace(
        plan, paragraphs=(replace(paragraph, runs=(broken_run, *paragraph.runs[1:])),)
    )

    report = validate_formatting_plan(broken, style_sheet)

    assert report.valid is False
    assert isinstance(first_error_of_type(report, InvalidParagraph), InvalidParagraph)


def test_missing_style_is_rejected():
    plan, style_sheet = make_plan()
    paragraph = plan.paragraphs[0]
    broken_run = replace(paragraph.runs[0], style=None)
    broken = replace(
        plan, paragraphs=(replace(paragraph, runs=(broken_run, *paragraph.runs[1:])),)
    )

    report = validate_formatting_plan(broken, style_sheet)

    assert report.valid is False
    assert isinstance(first_error_of_type(report, MissingStyle), MissingStyle)


def test_unknown_style_id_is_rejected():
    plan, style_sheet = make_plan()
    paragraph = plan.paragraphs[0]
    broken_run = replace(paragraph.runs[0], style_id="unknown")
    broken = replace(
        plan, paragraphs=(replace(paragraph, runs=(broken_run, *paragraph.runs[1:])),)
    )

    report = validate_formatting_plan(broken, style_sheet)

    assert report.valid is False
    assert isinstance(first_error_of_type(report, UnknownStyle), UnknownStyle)


def test_invalid_color_is_rejected():
    plan, style_sheet = make_plan()
    paragraph = plan.paragraphs[0]
    broken_style = replace(paragraph.runs[0].style, text_color="blue")
    broken_run = replace(paragraph.runs[0], style=broken_style)
    broken = replace(
        plan, paragraphs=(replace(paragraph, runs=(broken_run, *paragraph.runs[1:])),)
    )

    report = validate_formatting_plan(broken, style_sheet)

    assert report.valid is False
    assert isinstance(first_error_of_type(report, InvalidParagraph), InvalidParagraph)


def test_invalid_font_size_is_rejected():
    plan, style_sheet = make_plan()
    paragraph = plan.paragraphs[0]
    broken_style = replace(paragraph.runs[0].style, font_size=0)
    broken_run = replace(paragraph.runs[0], style=broken_style)
    broken = replace(
        plan, paragraphs=(replace(paragraph, runs=(broken_run, *paragraph.runs[1:])),)
    )

    report = validate_formatting_plan(broken, style_sheet)

    assert report.valid is False
    assert isinstance(first_error_of_type(report, InvalidParagraph), InvalidParagraph)


def test_empty_plan_is_rejected():
    plan, style_sheet = make_plan()
    broken = replace(plan, paragraphs=())

    report = validate_formatting_plan(broken, style_sheet)

    assert report.valid is False
    assert isinstance(
        first_error_of_type(report, InvalidFormattingPlan), InvalidFormattingPlan
    )
