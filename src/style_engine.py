from __future__ import annotations

from pathlib import Path

from .models import TextSpanType
from .style_loader import load_style_sheet
from .style_models import StyleSheet, TextStyle


class StyleEngine:
    def __init__(self, style_sheet: StyleSheet):
        self._style_sheet = style_sheet

    @property
    def style_sheet(self) -> StyleSheet:
        return self._style_sheet

    def get_style(self, span_type: TextSpanType) -> TextStyle:
        return self._style_sheet.style_for(span_type)


def load_style_engine(path: str | Path) -> StyleEngine:
    return StyleEngine(load_style_sheet(path))
