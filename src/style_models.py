from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .models import TextSpanType

REQUIRED_STYLE_FIELDS = (
    "font_family",
    "font_size",
    "bold",
    "italic",
    "underline",
    "text_color",
    "highlight_color",
    "alignment",
    "left_indent",
    "right_indent",
    "first_line_indent",
    "spacing_before",
    "spacing_after",
    "line_spacing",
)


class TextAlignment(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


@dataclass(frozen=True)
class TextStyle:
    font_family: str
    font_size: float
    bold: bool
    italic: bool
    underline: bool
    text_color: str
    highlight_color: str | None
    alignment: TextAlignment
    left_indent: float
    right_indent: float
    first_line_indent: float
    spacing_before: float
    spacing_after: float
    line_spacing: float


@dataclass(frozen=True)
class StyleSheet:
    name: str
    defaults: TextStyle
    styles: dict[TextSpanType, TextStyle] = field(default_factory=dict)

    def style_for(self, span_type: TextSpanType) -> TextStyle:
        return self.styles.get(span_type, self.defaults)
