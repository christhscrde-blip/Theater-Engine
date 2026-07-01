from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from .models import ClassifiedParagraph, ParagraphType, TextSpan


@dataclass(frozen=True)
class DocumentParagraph:
    """A single paragraph in the internal, text-preserving document model."""

    index: int
    text: str
    classification: ClassifiedParagraph
    spans: tuple[TextSpan, ...] = field(default_factory=tuple)

    @property
    def reconstructed_text(self) -> str:
        return "".join(span.text for span in self.spans)

    @property
    def has_integrity(self) -> bool:
        return self.reconstructed_text == self.text

    @property
    def needs_manual_review(self) -> bool:
        return (
            self.classification.type == ParagraphType.UNCLASSIFIED
            or "needs_manual_review" in self.classification.flags
        )


@dataclass(frozen=True)
class DocumentModel:
    """Internal representation used between classification and formatting."""

    source_file: str
    visible_text_sha256: str
    paragraphs: tuple[DocumentParagraph, ...]

    @property
    def paragraph_count(self) -> int:
        return len(self.paragraphs)

    @property
    def visible_text(self) -> str:
        return "\n".join(paragraph.text for paragraph in self.paragraphs)

    @property
    def has_integrity(self) -> bool:
        expected_hash = hashlib.sha256(self.visible_text.encode("utf-8")).hexdigest()
        return expected_hash == self.visible_text_sha256 and all(
            paragraph.has_integrity for paragraph in self.paragraphs
        )

    @property
    def manual_review_paragraphs(self) -> tuple[DocumentParagraph, ...]:
        return tuple(
            paragraph for paragraph in self.paragraphs if paragraph.needs_manual_review
        )
