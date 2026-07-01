from __future__ import annotations

from .document_model_builder import (
    build_document_model_from_docx,
    build_document_model_from_texts,
)
from .document_model_types import DocumentModel, DocumentParagraph

__all__ = [
    "DocumentModel",
    "DocumentParagraph",
    "build_document_model_from_docx",
    "build_document_model_from_texts",
]
