from __future__ import annotations

import re

DIFFICULT_WORDS: tuple[str, ...] = (
    "Korrespondenten",
    "Galan",
    "Genugtuung",
    "Liederlichkeiten",
    "Verzärtelung",
    "Schurke",
    "Eumenide",
    "corrosivisch",
    "Walstatt",
    "Prognosticieren",
    "Cavalier",
    "Canaille",
    "Dukaten",
    "Säkulum",
    "Plutarch",
    "Josephus",
    "Prometheus",
    "Salmiakgeist",
    "Collegium",
    "Kastraten",
    "Konventionen",
    "Schnürbrust",
    "verpalisadieren",
    "Manifest",
    "Palästina",
    "Victoria",
    "Schuldturm",
    "Almosen",
    "Almanach",
    "Schandsäulen",
    "Jasminlaube",
    "Böhmen",
    "Tragi-Komödie",
    "Crucifix",
    "Merrettig",
    "enterben",
    "Furie",
    "Otterbrut",
    "Ambrosiadüften",
    "Äsopischen",
    "Siechenhause",
    "Laster",
    "Tyrannin",
    "totenbleich",
    "Gassenjungen",
    "Pfennige",
    "Missetäter",
    "Fronte",
    "Universalkopfs",
    "Oceans",
    "Façon",
)


def find_difficult_words(text: str) -> tuple[str, ...]:
    hits: list[str] = []
    for word in DIFFICULT_WORDS:
        pattern = r"\b" + re.escape(word) + r"\b"
        if re.search(pattern, text, flags=re.IGNORECASE):
            hits.append(word)
    return tuple(hits)
