from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from docx import Document

from .difficult_words import find_difficult_words
from .models import AnalysisReport, ClassifiedParagraph, ParagraphType
from .speaker_parser import CHARACTER_ALIASES, normalize_name, parse_speaker_line
from .verifier import visible_text_hash

LOCATION_KEYWORDS = (
    "saal",
    "zimmer",
    "schlafzimmer",
    "schenke",
    "schloss",
    "wald",
    "gegend",
    "ort",
    "kloster",
    "turm",
    "moorischen",
    "böhmischen",
)


def is_page_marker(text: str) -> bool:
    return bool(re.fullmatch(r"Seite\s+\d+", text.strip(), flags=re.IGNORECASE))


def is_act_heading(text: str) -> bool:
    return bool(
        re.fullmatch(
            r"(Erster|Zweiter|Dritter|Vierter|Fünfter)\s+Akt\.?",
            text.strip(),
            flags=re.IGNORECASE,
        )
    )


def is_scene_heading(text: str) -> bool:
    stripped = text.strip()
    return bool(
        re.fullmatch(r"\d+\.\s*Szene\.?", stripped, flags=re.IGNORECASE)
        or re.fullmatch(
            r"(Erste|Zweite|Dritte|Vierte|Fünfte)\s+Sc?ene\.?",
            stripped,
            flags=re.IGNORECASE,
        )
    )


def is_location(text: str) -> bool:
    stripped = text.strip()
    if not stripped.endswith(".") or len(stripped) > 100:
        return False
    lowered = stripped.lower()
    return any(keyword in lowered for keyword in LOCATION_KEYWORDS)


def is_stage_only(text: str) -> bool:
    return bool(re.fullmatch(r"\([^)]{1,300}\)\.?", text.strip()))


def has_inline_stage(text: str) -> bool:
    return bool(re.search(r"\([^)]{1,160}\)", text))


def classify_texts(texts: list[str]) -> list[ClassifiedParagraph]:
    current_speaker = ""
    result: list[ClassifiedParagraph] = []

    for index, text in enumerate(texts, start=1):
        stripped = text.strip()
        flags: list[str] = []
        note = ""
        speaker = ""

        if not stripped:
            paragraph_type = ParagraphType.EMPTY
        elif is_page_marker(stripped):
            paragraph_type = ParagraphType.PAGE_MARKER
            current_speaker = ""
        elif is_act_heading(stripped):
            paragraph_type = ParagraphType.ACT_HEADING
            current_speaker = ""
        elif is_scene_heading(stripped):
            paragraph_type = ParagraphType.SCENE_HEADING
            current_speaker = ""
        elif is_location(stripped):
            paragraph_type = ParagraphType.LOCATION
            current_speaker = ""
        elif is_stage_only(stripped):
            paragraph_type = ParagraphType.STAGE_DIRECTION
            speaker = current_speaker
        else:
            parsed_speaker = parse_speaker_line(stripped)
            if parsed_speaker:
                speaker = parsed_speaker["canonical"]
                current_speaker = speaker
                if parsed_speaker["after"]:
                    paragraph_type = ParagraphType.SPEAKER_WITH_REPLIQUE
                    flags.append("speaker_and_text_same_paragraph")
                elif parsed_speaker["stage_inline"]:
                    paragraph_type = ParagraphType.SPEAKER_WITH_STAGE
                else:
                    paragraph_type = ParagraphType.SPEAKER
                note = f"Sprecher erkannt: {parsed_speaker['raw']}"
            elif current_speaker:
                paragraph_type = ParagraphType.REPLIQUE
                speaker = current_speaker
                if has_inline_stage(stripped):
                    flags.append("inline_stage_in_replique")
            else:
                paragraph_type = ParagraphType.UNCLASSIFIED
                flags.append("needs_manual_review")

        result.append(
            ClassifiedParagraph(
                index=index,
                text=text,
                type=paragraph_type,
                speaker=speaker,
                difficult_words=find_difficult_words(stripped),
                flags=tuple(flags),
                note=note,
            )
        )

    return result


def classify_docx(docx_path: str | Path) -> list[ClassifiedParagraph]:
    doc = Document(str(docx_path))
    return classify_texts([paragraph.text for paragraph in doc.paragraphs])


def build_report(
    docx_path: str | Path, paragraphs: list[ClassifiedParagraph]
) -> AnalysisReport:
    type_counts = Counter(item.type.value for item in paragraphs)
    speaker_counts = Counter(item.speaker for item in paragraphs if item.speaker)
    difficult_counts = Counter(
        word for item in paragraphs for word in item.difficult_words
    )
    manual_review_items = [
        {
            "paragraph": item.index,
            "type": item.type.value,
            "text": item.text[:220],
            "flags": "; ".join(item.flags),
        }
        for item in paragraphs
        if item.type == ParagraphType.UNCLASSIFIED
        or "needs_manual_review" in item.flags
    ]
    return AnalysisReport(
        source_file=str(docx_path),
        visible_text_sha256=visible_text_hash(docx_path),
        paragraph_count=len(paragraphs),
        type_counts=dict(type_counts),
        speaker_counts=dict(speaker_counts),
        difficult_word_counts=dict(difficult_counts),
        manual_review_count=len(manual_review_items),
        manual_review_items=manual_review_items,
    )
