from __future__ import annotations

from .document_model_types import DocumentModel, DocumentParagraph
from .formatting_plan_models import (
    FormattingPlan,
    FormattingRun,
    ParagraphFormattingPlan,
)
from .models import TextSpan
from .style_engine import StyleEngine


class FormattingPlanError(ValueError):
    pass


def build_formatting_plan(
    document_model: DocumentModel, style_engine: StyleEngine
) -> FormattingPlan:
    _assert_document_model_integrity(document_model)
    paragraphs = tuple(
        _build_paragraph_plan(paragraph, style_engine)
        for paragraph in document_model.paragraphs
    )
    plan = FormattingPlan(
        source_file=document_model.source_file,
        visible_text_sha256=document_model.visible_text_sha256,
        style_name=style_engine.style_sheet.name,
        paragraphs=paragraphs,
    )
    _assert_plan_integrity(plan, document_model)
    return plan


def _build_paragraph_plan(
    paragraph: DocumentParagraph, style_engine: StyleEngine
) -> ParagraphFormattingPlan:
    runs = tuple(
        _build_formatting_run(span_index, span, style_engine)
        for span_index, span in enumerate(paragraph.spans)
    )
    paragraph_plan = ParagraphFormattingPlan(
        index=paragraph.index,
        paragraph_type=paragraph.classification.type,
        speaker=paragraph.classification.speaker,
        needs_manual_review=paragraph.needs_manual_review,
        runs=runs,
    )
    if paragraph_plan.reconstructed_text != paragraph.text:
        raise FormattingPlanError(
            f"FormattingPlan integrity error in paragraph {paragraph.index}: "
            "run text does not reconstruct paragraph text"
        )
    return paragraph_plan


def _build_formatting_run(
    span_index: int, span: TextSpan, style_engine: StyleEngine
) -> FormattingRun:
    return FormattingRun(
        span_index=span_index,
        span_type=span.type,
        text=span.text,
        style=style_engine.get_style(span.type),
        speaker=span.speaker,
        flags=span.flags,
    )


def _assert_document_model_integrity(document_model: DocumentModel) -> None:
    if not document_model.has_integrity:
        raise FormattingPlanError("DocumentModel integrity check failed")


def _assert_plan_integrity(plan: FormattingPlan, document_model: DocumentModel) -> None:
    if plan.visible_text != document_model.visible_text or not plan.has_integrity:
        raise FormattingPlanError("FormattingPlan visible text integrity check failed")
