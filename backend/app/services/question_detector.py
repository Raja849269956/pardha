import re

QUESTION_MARKERS = re.compile(r"\?\s*$|\b(what|why|how|when|where|who|which|can|could|would|will|do|does|did|have|has|had|is|are|was|were|tell me|explain|describe|walk me through)\b", re.IGNORECASE)


def is_question(text: str) -> bool:
    text = text.strip()
    if not text:
        return False
    if text.endswith("?"):
        return True
    if QUESTION_MARKERS.search(text):
        return True
    return False


class QuestionDetector:
    def __init__(self, cooldown_seconds: float = 4.0):
        self.cooldown_seconds = cooldown_seconds
        self.last_question_time = None

    def detect(self, text: str, current_time: float) -> bool:
        if not is_question(text):
            return False
        if self.last_question_time and (current_time - self.last_question_time) < self.cooldown_seconds:
            return False
        self.last_question_time = current_time
        return True
