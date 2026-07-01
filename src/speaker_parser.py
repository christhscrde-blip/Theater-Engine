from __future__ import annotations

import re

CHARACTER_ALIASES: dict[str, str] = {
    "franz": "Franz",
    "franz von moor": "Franz",
    "d. a. moor": "Der alte Moor",
    "der alte moor": "Der alte Moor",
    "alter moor": "Der alte Moor",
    "karl v. moor": "Karl von Moor",
    "karl von moor": "Karl von Moor",
    "moor": "Karl von Moor",
    "amalia": "Amalia",
    "spiegelberg": "Spiegelberg",
    "schweizer": "Schweizer",
    "roller": "Roller",
    "razmann": "Razmann",
    "schufterle": "Schufterle",
    "hermann": "Hermann",
    "daniel": "Daniel",
    "kosinsky": "Kosinsky",
    "schwarz": "Schwarz",
    "grimm": "Grimm",
    "ein räuber": "Ein Räuber",
    "räuber": "Räuber",
    "alle": "Alle",
    "ein bedienter": "Ein Bedienter",
    "bedienter": "Bedienter",
    "pastor moser": "Pastor Moser",
    "moser": "Moser",
    "pater": "Pater",
}


def normalize_name(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.strip(".:; ")
    return text.lower()


def parse_speaker_line(text: str) -> dict[str, str] | None:
    stripped = text.strip()
    lowered = stripped.lower()

    for alias in sorted(CHARACTER_ALIASES, key=len, reverse=True):
        if not lowered.startswith(alias):
            continue

        raw_name = stripped[: len(alias)].strip()
        remainder = stripped[len(alias) :]
        match = re.match(
            r"^\s*(?P<stage>\([^)]*\))?\s*[\.:]\s*(?P<after>.*)$",
            remainder,
        )
        if not match:
            continue

        return {
            "raw": raw_name,
            "canonical": CHARACTER_ALIASES[alias],
            "stage_inline": (match.group("stage") or "").strip(),
            "after": (match.group("after") or "").strip(),
        }

    return None
