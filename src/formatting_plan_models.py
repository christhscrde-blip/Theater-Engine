from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from .models import ParagraphType, TextSpanType
from .style_models import TextStyle


@dataclass(frozen=True)
class FormattingRun:
    span_index: int
    span_type: TextSpanType
    text: str
    style: TextStyle
    speaker: str = ""
    flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class ParagraphFormattingPlan:
    index: int
    paragraph_type: ParagraphType
    speaker: str
    needs_manual_review: bool
    runs: tuple[FormattingRun, ...] = field(default_factory=tuple)

    @property
    def reconstructed_text(self) -> str:
        return "".join(run.text for run in self.runs)


@dataclass(frozen=True)
class FormattingPlan:
    source_file: str
    visible_text_sha256: str
    style_name: str
    paragraphs: tuple[ParagraphFormattingPlan, ...]

    @property
    def paragraph_count(self) -> int:
        return len(self.paragraphs)

    @property
    def visible_text(self) -> str:
        return "\n".join(paragraph.reconstructed_text for paragraph in self.paragraphs)

    @property
    def has_integrity(self) -> bool:
        expected_hash = hashlib.sha256(self.visible_text.encode("utf-8")).hexdigest()
        return expected_hash == self.visible_text_sha256

    @property
    def manual_review_paragraphs(self) -> tuple[ParagraphFormattingPlan, ...]:
        return tuple(
            paragraph for paragraph in self.paragraphs if paragraph.needs_manual_review
        )
