from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..formatting_plan_models import (
    FormattingPlan,
    FormattingRun,
    ParagraphFormattingPlan,
)
from ..models import TextSpanType
from ..style_models import StyleSheet, TextAlignment, TextStyle
from .validation_errors import (
    DuplicateParagraph,
    InvalidFormattingPlan,
    InvalidParagraph,
    InvalidSpan,
    MissingStyle,
    OverlappingSpan,
    UnknownStyle,
)

HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


@dataclass(frozen=True)
class ValidationStatistics:
    paragraph_count: int = 0
    run_count: int = 0
    manual_review_count: int = 0


@dataclass(frozen=True)
class ValidationReport:
    valid: bool
    errors: tuple[InvalidFormattingPlan, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    statistics: ValidationStatistics = field(default_factory=ValidationStatistics)


def validate_formatting_plan(
    plan: FormattingPlan, style_sheet: StyleSheet | None = None
) -> ValidationReport:
    errors: list[InvalidFormattingPlan] = []
    errors.extend(_validate_plan_shape(plan))
    errors.extend(_validate_paragraphs(plan, style_sheet))
    return ValidationReport(
        valid=not errors,
        errors=tuple(errors),
        statistics=_statistics(plan),
    )


def assert_valid_formatting_plan(
    plan: FormattingPlan, style_sheet: StyleSheet | None = None
) -> ValidationReport:
    report = validate_formatting_plan(plan, style_sheet)
    if not report.valid:
        raise report.errors[0]
    return report


def _validate_plan_shape(plan: FormattingPlan) -> list[InvalidFormattingPlan]:
    errors: list[InvalidFormattingPlan] = []
    if not plan.paragraphs:
        errors.append(InvalidFormattingPlan("FormattingPlan is empty"))
    if not plan.has_integrity:
        errors.append(
            InvalidFormattingPlan("FormattingPlan visible-text hash is invalid")
        )
    return errors


def _validate_paragraphs(
    plan: FormattingPlan, style_sheet: StyleSheet | None
) -> list[InvalidFormattingPlan]:
    errors: list[InvalidFormattingPlan] = []
    seen: set[int] = set()
    previous_index = 0
    for position, paragraph in enumerate(plan.paragraphs, start=1):
        if paragraph.index in seen:
            errors.append(
                DuplicateParagraph(f"Duplicate paragraph id {paragraph.index}")
            )
        seen.add(paragraph.index)
        if paragraph.index <= previous_index:
            errors.append(
                InvalidParagraph(
                    f"Paragraph order is not strictly increasing at position {position}: "
                    f"paragraph id {paragraph.index} follows {previous_index}"
                )
            )
        previous_index = paragraph.index
        errors.extend(_validate_paragraph(paragraph, style_sheet))
    return errors


def _validate_paragraph(
    paragraph: ParagraphFormattingPlan, style_sheet: StyleSheet | None
) -> list[InvalidFormattingPlan]:
    errors: list[InvalidFormattingPlan] = []
    if not paragraph.paragraph_style_id:
        errors.append(
            InvalidParagraph(f"Paragraph {paragraph.index} has no ParagraphStyle")
        )
    if not paragraph.runs:
        errors.append(
            InvalidParagraph(f"Paragraph {paragraph.index} has no TextSpan styles")
        )
        return errors

    expected_offset = 0
    paragraph_length = len(paragraph.reconstructed_text)
    for expected_span_index, run in enumerate(paragraph.runs):
        errors.extend(
            _validate_run(
                paragraph=paragraph,
                run=run,
                expected_span_index=expected_span_index,
                expected_offset=expected_offset,
                paragraph_length=paragraph_length,
                style_sheet=style_sheet,
            )
        )
        expected_offset = run.end_offset
    return errors


def _validate_run(
    paragraph: ParagraphFormattingPlan,
    run: FormattingRun,
    expected_span_index: int,
    expected_offset: int,
    paragraph_length: int,
    style_sheet: StyleSheet | None,
) -> list[InvalidFormattingPlan]:
    errors: list[InvalidFormattingPlan] = []
    if run.span_index != expected_span_index:
        errors.append(
            InvalidSpan(
                f"Paragraph {paragraph.index} span order is not continuous: "
                f"expected {expected_span_index}, got {run.span_index}"
            )
        )
    if run.start_offset < expected_offset:
        errors.append(
            OverlappingSpan(
                f"Paragraph {paragraph.index} span {run.span_index} overlaps previous span"
            )
        )
    if run.start_offset > expected_offset:
        errors.append(
            InvalidSpan(
                f"Paragraph {paragraph.index} span {run.span_index} has a gap before it"
            )
        )
    if run.end_offset != run.start_offset + len(run.text):
        errors.append(
            InvalidSpan(
                f"Paragraph {paragraph.index} span {run.span_index} range does not match text length"
            )
        )
    if run.end_offset > paragraph_length:
        errors.append(
            InvalidSpan(
                f"Paragraph {paragraph.index} span {run.span_index} exceeds paragraph boundaries"
            )
        )
    errors.extend(_validate_style_reference(paragraph, run, style_sheet))
    return errors


def _validate_style_reference(
    paragraph: ParagraphFormattingPlan,
    run: FormattingRun,
    style_sheet: StyleSheet | None,
) -> list[InvalidFormattingPlan]:
    errors: list[InvalidFormattingPlan] = []
    if not run.style_id:
        errors.append(
            MissingStyle(
                f"Paragraph {paragraph.index} span {run.span_index} has no style id"
            )
        )
    elif run.style_id not in _known_style_ids(style_sheet):
        errors.append(
            UnknownStyle(
                f"Paragraph {paragraph.index} span {run.span_index} references unknown style '{run.style_id}'"
            )
        )
    if run.style is None:
        errors.append(
            MissingStyle(
                f"Paragraph {paragraph.index} span {run.span_index} has no style"
            )
        )
        return errors
    errors.extend(_validate_style(paragraph, run, run.style))
    return errors


def _known_style_ids(style_sheet: StyleSheet | None) -> set[str]:
    if style_sheet is None:
        return {span_type.value for span_type in TextSpanType}
    return {
        span_type.value
        for span_type in TextSpanType
        if style_sheet.style_for(span_type)
    }


def _validate_style(
    paragraph: ParagraphFormattingPlan, run: FormattingRun, style: TextStyle
) -> list[InvalidFormattingPlan]:
    errors: list[InvalidFormattingPlan] = []
    if not isinstance(style.alignment, TextAlignment):
        errors.append(
            InvalidParagraph(
                f"Paragraph {paragraph.index} span {run.span_index} has invalid alignment"
            )
        )
    if not _valid_color(style.text_color):
        errors.append(
            InvalidParagraph(
                f"Paragraph {paragraph.index} span {run.span_index} has invalid text color"
            )
        )
    if style.highlight_color is not None and not _valid_color(style.highlight_color):
        errors.append(
            InvalidParagraph(
                f"Paragraph {paragraph.index} span {run.span_index} has invalid highlight color"
            )
        )
    if style.font_size <= 0:
        errors.append(
            InvalidParagraph(
                f"Paragraph {paragraph.index} span {run.span_index} has non-positive font size"
            )
        )
    return errors


def _valid_color(value: object) -> bool:
    return isinstance(value, str) and bool(HEX_COLOR_PATTERN.fullmatch(value))


def _statistics(plan: FormattingPlan) -> ValidationStatistics:
    return ValidationStatistics(
        paragraph_count=len(plan.paragraphs),
        run_count=sum(len(paragraph.runs) for paragraph in plan.paragraphs),
        manual_review_count=len(plan.manual_review_paragraphs),
    )
