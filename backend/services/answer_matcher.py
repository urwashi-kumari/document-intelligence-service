import re


ANSWER_LINE_PATTERN = re.compile(
    r"^\s*(?:Q(?:uestion)?\s*)?(\d+)\s*[\.\):-]\s*([A-Ha-h])\s*$",
    re.IGNORECASE,
)

ANSWER_KEY_HEADER_PATTERN = re.compile(
    r"\b(answer\s*key|answers?|solutions?)\b",
    re.IGNORECASE,
)


def normalize_answer(answer: str) -> str:
    """
    Normalize an answer value such as:
    'A', 'a', '(A)', 'Option A' -> 'A'
    """
    answer = answer.strip().upper()

    match = re.search(r"\b([A-H])\b", answer)
    if match:
        return match.group(1)

    return answer


def extract_answer_key(text: str) -> dict[str, str]:
    """
    Extract question-number -> answer-option mappings.

    Supported examples:

        1. A
        2. C
        3. B

    Also supports:

        Q1: A
        Question 2 - C
        3) D

    Only explicit answer mappings are extracted.
    """

    answers: dict[str, str] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        match = ANSWER_LINE_PATTERN.match(line)

        if not match:
            continue

        question_number = match.group(1)
        answer = normalize_answer(match.group(2))

        if answer in {"A", "B", "C", "D", "E", "F", "G", "H"}:
            answers[question_number] = answer

    return answers


def match_answers_to_questions(
    questions: list[dict],
    answer_key: dict[str, str],
) -> list[dict]:
    """
    Associate extracted answers with extracted questions.

    Answers are assigned only when the question number has
    an explicit matching entry in the answer key.

    Missing mappings remain uncertain and require review.
    """

    results = []

    for question in questions:
        question_number = str(question.get("question_number", "")).strip()

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