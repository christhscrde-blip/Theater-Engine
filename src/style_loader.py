from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .models import TextSpanType
from .style_models import REQUIRED_STYLE_FIELDS, StyleSheet, TextAlignment, TextStyle

HEX_COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


class StyleLoaderError(ValueError):
    pass


def load_style_sheet(path: str | Path) -> StyleSheet:
    style_path = Path(path)
    try:
        raw_text = style_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise StyleLoaderError(f"Style file cannot be read: {style_path}") from exc
    return load_style_sheet_from_text(raw_text, source=str(style_path))


def load_style_sheet_from_text(text: str, source: str = "<string>") -> StyleSheet:
    data = _parse_yaml(text, source)
    return _build_style_sheet(data, source)


def _parse_yaml(text: str, source: str) -> dict[str, Any]:
    try:
        loaded = _parse_simple_yaml_mapping(text)
    except StyleLoaderError:
        raise
    except Exception as exc:
        raise StyleLoaderError(f"Invalid YAML in {source}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise StyleLoaderError(f"Style file {source} must contain a YAML mapping")
    return loaded


def _parse_simple_yaml_mapping(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if _is_ignored_yaml_line(raw_line):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent % 2 != 0:
            raise StyleLoaderError(f"Invalid YAML indentation at line {line_number}")

        line = raw_line.strip()
        if ":" not in line:
            raise StyleLoaderError(f"Invalid YAML line {line_number}: missing ':'")

        key, raw_value = line.split(":", 1)
        key = key.strip()
        if not key:
            raise StyleLoaderError(f"Invalid YAML line {line_number}: empty key")

        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise StyleLoaderError(f"Invalid YAML indentation at line {line_number}")

        parent = stack[-1][1]
        raw_value = raw_value.strip()
        if raw_value == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _parse_scalar(raw_value, line_number)

    return root


def _is_ignored_yaml_line(raw_line: str) -> bool:
    stripped = raw_line.strip()
    return not stripped or stripped.startswith("#")


def _parse_scalar(raw_value: str, line_number: int) -> str | bool | float | int | None:
    if raw_value in {"null", "~"}:
        return None
    if raw_value == "true":
        return True
    if raw_value == "false":
        return False
    if raw_value == "{}":
        return {}
    if raw_value.startswith("[") or raw_value.startswith("{"):
        raise StyleLoaderError(f"Invalid YAML line {line_number}: unsupported scalar")
    if raw_value.startswith(('"', "'")):
        return _parse_quoted_scalar(raw_value, line_number)
    try:
        return int(raw_value)
    except ValueError:
        pass
    try:
        return float(raw_value)
    except ValueError:
        return raw_value


def _parse_quoted_scalar(raw_value: str, line_number: int) -> str:
    quote = raw_value[0]
    if len(raw_value) < 2 or raw_value[-1] != quote:
        raise StyleLoaderError(f"Invalid YAML line {line_number}: unterminated string")
    return raw_value[1:-1]


def _build_style_sheet(data: dict[str, Any], source: str) -> StyleSheet:
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        raise StyleLoaderError(f"Style file {source} requires a non-empty 'name'")

    defaults_data = _require_mapping(data, "defaults", source)
    defaults = _build_text_style(defaults_data, context=f"{source}:defaults")

    styles_data = _require_mapping(data, "styles", source)
    styles = {
        _parse_span_type(raw_span_type, source): _build_text_style(
            _merge_style_data(defaults_data, style_data, raw_span_type, source),
            context=f"{source}:styles.{raw_span_type}",
        )
        for raw_span_type, style_data in styles_data.items()
    }

    return StyleSheet(name=name.strip(), defaults=defaults, styles=styles)


def _require_mapping(data: dict[str, Any], key: str, source: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise StyleLoaderError(f"Style file {source} requires mapping '{key}'")
    return value


def _parse_span_type(raw_span_type: Any, source: str) -> TextSpanType:
    if not isinstance(raw_span_type, str):
        raise StyleLoaderError(f"Style file {source} contains a non-string span type")
    try:
        return TextSpanType(raw_span_type)
    except ValueError as exc:
        valid = ", ".join(item.value for item in TextSpanType)
        raise StyleLoaderError(
            f"Style file {source} contains invalid span type '{raw_span_type}'. "
            f"Valid values: {valid}"
        ) from exc


def _merge_style_data(
    defaults_data: dict[str, Any], style_data: Any, raw_span_type: Any, source: str
) -> dict[str, Any]:
    if not isinstance(style_data, dict):
        raise StyleLoaderError(
            f"Style file {source} style '{raw_span_type}' must be a mapping"
        )
    return {**defaults_data, **style_data}


def _build_text_style(data: dict[str, Any], context: str) -> TextStyle:
    _validate_required_fields(data, context)
    return TextStyle(
        font_family=_validate_string(data["font_family"], "font_family", context),
        font_size=_validate_number(data["font_size"], "font_size", context),
        bold=_validate_bool(data["bold"], "bold", context),
        italic=_validate_bool(data["italic"], "italic", context),
        underline=_validate_bool(data["underline"], "underline", context),
        text_color=_validate_color(data["text_color"], "text_color", context),
        highlight_color=_validate_optional_color(
            data["highlight_color"], "highlight_color", context
        ),
        alignment=_validate_alignment(data["alignment"], context),
        left_indent=_validate_number(data["left_indent"], "left_indent", context),
        right_indent=_validate_number(data["right_indent"], "right_indent", context),
        first_line_indent=_validate_number(
            data["first_line_indent"], "first_line_indent", context
        ),
        spacing_before=_validate_number(
            data["spacing_before"], "spacing_before", context
        ),
        spacing_after=_validate_number(data["spacing_after"], "spacing_after", context),
        line_spacing=_validate_number(data["line_spacing"], "line_spacing", context),
    )


def _validate_required_fields(data: dict[str, Any], context: str) -> None:
    missing = [field for field in REQUIRED_STYLE_FIELDS if field not in data]
    if missing:
        joined = ", ".join(missing)
        raise StyleLoaderError(
            f"Style '{context}' is missing required fields: {joined}"
        )


def _validate_string(value: Any, field_name: str, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StyleLoaderError(f"Style '{context}' field '{field_name}' must be text")
    return value.strip()


def _validate_bool(value: Any, field_name: str, context: str) -> bool:
    if not isinstance(value, bool):
        raise StyleLoaderError(
            f"Style '{context}' field '{field_name}' must be boolean"
        )
    return value


def _validate_number(value: Any, field_name: str, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise StyleLoaderError(
            f"Style '{context}' field '{field_name}' must be a number"
        )
    return float(value)


def _validate_color(value: Any, field_name: str, context: str) -> str:
    if not isinstance(value, str) or not HEX_COLOR_PATTERN.fullmatch(value):
        raise StyleLoaderError(
            f"Style '{context}' field '{field_name}' must be a hex color like #AABBCC"
        )
    return value.upper()


def _validate_optional_color(value: Any, field_name: str, context: str) -> str | None:
    if value is None:
        return None
    return _validate_color(value, field_name, context)


def _validate_alignment(value: Any, context: str) -> TextAlignment:
    if not isinstance(value, str):
        raise StyleLoaderError(f"Style '{context}' field 'alignment' must be text")
    try:
        return TextAlignment(value)
    except ValueError as exc:
        valid = ", ".join(item.value for item in TextAlignment)
        raise StyleLoaderError(
            f"Style '{context}' field 'alignment' has invalid value '{value}'. "
            f"Valid values: {valid}"
        ) from exc
