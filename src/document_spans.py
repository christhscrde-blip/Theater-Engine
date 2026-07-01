from __future__ import annotations

import re

from .models import ClassifiedParagraph, ParagraphType, TextSpan, TextSpanType
from .speaker_parser import parse_speaker_line

INLINE_STAGE_PATTERN = re.compile(r"\([^)]{1,160}\)")


def build_spans(text: str, classification: ClassifiedParagraph) -> tuple[TextSpan, ...]:
    if text == "":
        return (TextSpan(type=TextSpanType.PLAIN, text=""),)

    if classification.type == ParagraphType.SPEAKER_WITH_REPLIQUE:
        return _split_speaker_prefix_spans(text, classification, split_replique=True)
    if classification.type == ParagraphType.SPEAKER_WITH_STAGE:
        return _split_inline_stage_spans(
            text, TextSpanType.SPEAKER, speaker=classification.speaker
        )

    base_type = _base_span_type(classification.type)
    if classification.type == ParagraphType.REPLIQUE:
        return _split_inline_stage_spans(
            text, base_type, speaker=classification.speaker
        )

    return (TextSpan(type=base_type, text=text, speaker=classification.speaker),)


def _base_span_type(paragraph_type: ParagraphType) -> TextSpanType:
    if paragraph_type in {ParagraphType.SPEAKER, ParagraphType.SPEAKER_WITH_STAGE}:
        return TextSpanType.SPEAKER
    if paragraph_type in {ParagraphType.REPLIQUE, ParagraphType.SPEAKER_WITH_REPLIQUE}:
        return TextSpanType.REPLIQUE
    if paragraph_type == ParagraphType.STAGE_DIRECTION:
        return TextSpanType.STAGE_DIRECTION
    return TextSpanType.PLAIN


def _split_inline_stage_spans(
    text: str, fallback_type: TextSpanType, speaker: str = ""
) -> tuple[TextSpan, ...]:
    spans: list[TextSpan] = []
    cursor = 0
    for match in INLINE_STAGE_PATTERN.finditer(text):
        if match.start() > cursor:
            spans.append(
                TextSpan(
                    type=fallback_type,
                    text=text[cursor : match.start()],
                    speaker=speaker,
                )
            )
        spans.append(TextSpan(type=TextSpanType.INLINE_STAGE, text=match.group(0)))
        cursor = match.end()
    if cursor < len(text):
        spans.append(TextSpan(type=fallback_type, text=text[cursor:], speaker=speaker))
    return tuple(spans) or (TextSpan(type=fallback_type, text=text, speaker=speaker),)


def _split_speaker_prefix_spans(
    text: str, classification: ClassifiedParagraph, split_replique: bool
) -> tuple[TextSpan, ...]:
    parsed = parse_speaker_line(text)
    if not parsed:
        return _single_replique_span(text, classification)

    raw_name = parsed["raw"]
    name_start = text.find(raw_name)
    if name_start < 0:
        return _single_replique_span(text, classification)

    spans: list[TextSpan] = []
    if name_start:
        spans.append(TextSpan(type=TextSpanType.PLAIN, text=text[:name_start]))

    cursor = name_start + len(raw_name)
    stage_inline = parsed["stage_inline"]
    stage_match = (
        re.match(r"\s*" + re.escape(stage_inline), text[cursor:])
        if stage_inline
        else None
    )
    if stage_match:
        speaker_text = text[name_start:cursor]
        spans.append(
            TextSpan(
                type=TextSpanType.SPEAKER,
                text=speaker_text,
                speaker=classification.speaker,
            )
        )
        spans.append(
            TextSpan(type=TextSpanType.INLINE_STAGE, text=stage_match.group(0))
        )
        cursor += stage_match.end()
    else:
        separator_match = re.match(r"\s*[\.:]\s*", text[cursor:])
        if not separator_match:
            return _single_replique_span(text, classification)
        cursor += separator_match.end()
        speaker_text = text[name_start:cursor]
        spans.append(
            TextSpan(
                type=TextSpanType.SPEAKER,
                text=speaker_text,
                speaker=classification.speaker,
            )
        )

    if split_replique and cursor < len(text):
        spans.extend(
            _split_inline_stage_spans(
                text[cursor:], TextSpanType.REPLIQUE, speaker=classification.speaker
            )
        )
    elif cursor < len(text):
        spans.append(TextSpan(type=TextSpanType.PLAIN, text=text[cursor:]))

    if "".join(span.text for span in spans) != text:
        return _single_replique_span(text, classification)
    return tuple(spans)


def _single_replique_span(
    text: str, classification: ClassifiedParagraph
) -> tuple[TextSpan, ...]:
    return (
        TextSpan(type=TextSpanType.REPLIQUE, text=text, speaker=classification.speaker),
    )
