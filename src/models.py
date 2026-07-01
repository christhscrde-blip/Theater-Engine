from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ParagraphType(str, Enum):
    EMPTY = "empty"
    PAGE_MARKER = "page_marker"
    ACT_HEADING = "act_heading"
    SCENE_HEADING = "scene_heading"
    LOCATION = "location"
    SPEAKER = "speaker"
    SPEAKER_WITH_STAGE = "speaker_with_stage"
    SPEAKER_WITH_REPLIQUE = "speaker_with_replique"
    REPLIQUE = "replique"
    STAGE_DIRECTION = "stage_direction"
    UNCLASSIFIED = "unclassified"


class TextSpanType(str, Enum):
    PLAIN = "plain"
    SPEAKER = "speaker"
    REPLIQUE = "replique"
    STAGE_DIRECTION = "stage_direction"
    INLINE_STAGE = "inline_stage"


@dataclass(frozen=True)
class TextSpan:
    type: TextSpanType
    text: str
    speaker: str = ""
    flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class ClassifiedParagraph:
    index: int
    text: str
    type: ParagraphType
    speaker: str = ""
    difficult_words: tuple[str, ...] = ()
    flags: tuple[str, ...] = ()
    note: str = ""


@dataclass
class AnalysisReport:
    source_file: str
    visible_text_sha256: str
    paragraph_count: int
    type_counts: dict[str, int] = field(default_factory=dict)
    speaker_counts: dict[str, int] = field(default_factory=dict)
    difficult_word_counts: dict[str, int] = field(default_factory=dict)
    manual_review_count: int = 0
    manual_review_items: list[dict[str, str | int]] = field(default_factory=list)
