from __future__ import annotations


class InvalidFormattingPlan(ValueError):
    pass


class MissingStyle(InvalidFormattingPlan):
    pass


class OverlappingSpan(InvalidFormattingPlan):
    pass


class InvalidParagraph(InvalidFormattingPlan):
    pass


class InvalidSpan(InvalidFormattingPlan):
    pass


class UnknownStyle(InvalidFormattingPlan):
    pass


class DuplicateParagraph(InvalidFormattingPlan):
    pass
