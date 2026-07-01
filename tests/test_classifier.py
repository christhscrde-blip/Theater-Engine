from src.classifier import classify_texts
from src.models import ParagraphType


def test_basic_dialogue_classification():
    paragraphs = classify_texts(
        [
            "Erster Akt",
            "1. Szene",
            "Saal im Moorischen Schloss.",
            "Franz.",
            "Aber ist Euch auch wohl, Vater?",
            "D. a. Moor (begierig).",
            "Nachrichten von meinem Sohne Karl?",
            "Seite 1",
        ]
    )

    assert paragraphs[0].type == ParagraphType.ACT_HEADING
    assert paragraphs[1].type == ParagraphType.SCENE_HEADING
    assert paragraphs[2].type == ParagraphType.LOCATION
    assert paragraphs[3].type == ParagraphType.SPEAKER
    assert paragraphs[3].speaker == "Franz"
    assert paragraphs[4].type == ParagraphType.REPLIQUE
    assert paragraphs[4].speaker == "Franz"
    assert paragraphs[5].type == ParagraphType.SPEAKER_WITH_STAGE
    assert paragraphs[5].speaker == "Der alte Moor"
    assert paragraphs[6].type == ParagraphType.REPLIQUE
    assert paragraphs[6].speaker == "Der alte Moor"
    assert paragraphs[7].type == ParagraphType.PAGE_MARKER


def test_speaker_with_replique_is_detected():
    paragraph = classify_texts(["Franz. Aber ist Euch auch wohl, Vater?"])[0]
    assert paragraph.type == ParagraphType.SPEAKER_WITH_REPLIQUE
    assert paragraph.speaker == "Franz"
    assert "speaker_and_text_same_paragraph" in paragraph.flags


def test_unknown_without_context_requires_review():
    paragraph = classify_texts(["Irgendein einzelner Satz ohne Sprecher."])[0]
    assert paragraph.type == ParagraphType.UNCLASSIFIED
    assert "needs_manual_review" in paragraph.flags


def test_abbreviated_speaker_with_stage_is_detected_without_context_leak():
    paragraph = classify_texts(["D. a. Moor (begierig)."])[0]

    assert paragraph.type == ParagraphType.SPEAKER_WITH_STAGE
    assert paragraph.speaker == "Der alte Moor"


def test_abbreviated_speaker_with_replique_is_detected():
    paragraph = classify_texts(["D. a. Moor: Nachrichten von meinem Sohne Karl?"])[0]

    assert paragraph.type == ParagraphType.SPEAKER_WITH_REPLIQUE
    assert paragraph.speaker == "Der alte Moor"
