from __future__ import annotations

from pathlib import Path

from .document_model import build_document_model_from_docx
from .formatting_plan import build_formatting_plan
from .renderer import WordRenderer
from .style_engine import load_style_engine
from .validation import assert_valid_formatting_plan
from .verifier import assert_visible_text_unchanged

DEFAULT_STYLE_PATH = Path(__file__).resolve().parent.parent / "styles" / "theater.yaml"


def format_docx(
    input_docx: str | Path, output_docx: str | Path, style_path: str | Path | None = None
) -> Path:
    input_path = Path(input_docx)
    output_path = Path(output_docx)
    engine = load_style_engine(_style_path(style_path))
    document_model = build_document_model_from_docx(input_path)
    formatting_plan = build_formatting_plan(document_model, engine)
    assert_valid_formatting_plan(formatting_plan, engine.style_sheet)
    rendered_path = WordRenderer().render(
        input_path,
        output_path,
        document_model,
        formatting_plan,
    )
    assert_visible_text_unchanged(input_path, rendered_path)
    return rendered_path


def _style_path(style_path: str | Path | None) -> Path:
    if style_path is None:
        return DEFAULT_STYLE_PATH
    return Path(style_path)
