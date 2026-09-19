import re


# Compact format used by the real document:
# 1b
# 21d
# 41a
COMPACT_ANSWER_PATTERN = re.compile(
    r"^\s*(\d+)\s*([A-Ha-h])\s*$"
)

# Formats such as:
# 1. B
# 2) C
# 3: D
STANDARD_ANSWER_PATTERN = re.compile(
    r"^\s*(?:Q(?:uestion)?\s*)?(\d+)\s*[\.\):\-]\s*"
    r"[\(\[]?([A-Ha-h])[\)\]]?\s*$",
    re.IGNORECASE,
)

# Formats such as:
# Q1: A
# Question 2 - B
NAMED_ANSWER_PATTERN = re.compile(
    r"^\s*(?:Q(?:uestion)?\s*)(\d+)\s*[\.\):\-]\s*"
    r"[\(\[]?([A-Ha-h])[\)\]]?\s*$",
    re.IGNORECASE,
)


def normalize_answer(answer: str) -> str:
    """Normalize an answer option to uppercase."""
    return answer.strip().upper()


def extract_answer_key(text: str) -> dict[str, str]:
    """
    Extract question-number -> answer-option mappings.

    Supported formats:

        1b
        21d
        41a

        1. B
        2) C
        3: D

        Q1: A
        Question 2 - B
        Q3) C
    """

    answers: dict[str, str] = {}

    lines = text.splitlines()

    has_answer_key_heading = any(
        re.search(r"\bANSWER\s+KEY\b", line, re.IGNORECASE)
        for line in lines
    )

    # If the document contains an ANSWER KEY heading,
    # ignore numbered content before that heading.
    answer_key_started = not has_answer_key_heading

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            continue

        # Detect answer-key section.
        if re.search(r"\bANSWER\s+KEY\b", line, re.IGNORECASE):
            answer_key_started = True
            continue

        if not answer_key_started:
            continue

        match = (
            NAMED_ANSWER_PATTERN.match(line)
            or STANDARD_ANSWER_PATTERN.match(line)
            or COMPACT_ANSWER_PATTERN.match(line)
        )

        if not match:
            continue

        question_number = match.group(1)
        answer = normalize_answer(match.group(2))

        if answer in {
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
        }:
            answers[question_number] = answer

    return answers


def match_answers_to_questions(
    questions: list[dict],
    answer_key: dict[str, str],
) -> list[dict]:
    """
    Associate answer-key entries with extracted questions.

    If an explicit answer is unavailable, no answer is guessed.
    The question remains in review status.
    """

    results = []

    for question in questions:
        question_number = str(
            question.get("question_number", "")
        ).strip()

        result = question.copy()

        if question_number in answer_key:
            answer = answer_key[question_number]

            result["answer"] = answer
            result["answer_confidence"] = 0.98

            if result.get("review_status") == "extracted":
                result["review_status"] = "extracted"
            else:
                result["review_status"] = "review"

        else:
            result["answer"] = None
            result["answer_confidence"] = 0.0
            result["review_status"] = "review"

        results.append(result)

    return results