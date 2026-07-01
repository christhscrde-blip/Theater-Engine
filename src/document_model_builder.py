from __future__ import annotations

import hashlib
from pathlib import Path

from docx import Document

from .classifier import classify_texts
from .document_model_types import DocumentModel, DocumentParagraph
from .document_spans import build_spans
from .models import ClassifiedParagraph
from .verifier import visible_text_hash


def build_document_model_from_docx(docx_path: str | Path) -> DocumentModel:
    path = Path(docx_path)
    doc = Document(str(path))
    texts = [paragraph.text for paragraph in doc.paragraphs]
    return build_document_model_from_texts(
        texts,
        source_file=str(path),
        expected_visible_text_sha256=visible_text_hash(path),
    )


def build_document_model_from_texts(
    texts: list[str] | tuple[str, ...],
    source_file: str = "",
    expected_visible_text_sha256: str | None = None,
) -> DocumentModel:
    normalized_texts = [text if text is not None else "" for text in texts]
    classifications = classify_texts(normalized_texts)
    paragraphs = tuple(
        _build_document_paragraph(text, classification)
        for text, classification in zip(normalized_texts, classifications, strict=True)
    )
    visible_text = "\n".join(normalized_texts)
    text_hash = (
        expected_visible_text_sha256
        or hashlib.sha256(visible_text.encode("utf-8")).hexdigest()
    )
    model = DocumentModel(
        source_file=source_file,
        visible_text_sha256=text_hash,
        paragraphs=paragraphs,
    )
    _assert_model_integrity(model)
    return model


def _build_document_paragraph(
    text: str, classification: ClassifiedParagraph
) -> DocumentParagraph:
    spans = build_spans(text, classification)
    paragraph = DocumentParagraph(
        index=classification.index,
        text=text,
        classification=classification,
        spans=spans,
    )
    if not paragraph.has_integrity:
        raise ValueError(
            f"DocumentModel integrity error in paragraph {classification.index}: "
            "span text does not reconstruct paragraph text"
        )
    return paragraph


def _assert_model_integrity(model: DocumentModel) -> None:
    if not model.has_integrity:
        raise ValueError("DocumentModel integrity error: visible text hash mismatch")
