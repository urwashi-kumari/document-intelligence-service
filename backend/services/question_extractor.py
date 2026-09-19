import re


QUESTION_START_PATTERN = re.compile(
    r"^\s*(?:Q(?:uestion)?\s*)?(\d+)[\.\):-]\s*(.+)$",
    re.IGNORECASE,
)

OPTION_PATTERN = re.compile(
    r"^\s*[\(\[]?([A-Ha-h])[\)\].:-]\s*(.+)$"
)

QUESTION_WORD_PATTERN = re.compile(
    r"\b(what|which|who|where|when|why|how|explain|define|describe|"
    r"identify|list|compare|calculate|write|state|discuss|select|"
    r"choose|give|mention)\b",
    re.IGNORECASE,
)

NON_QUESTION_PATTERN = re.compile(
    r"\b(by|publication|publishing|publisher|manning|packt|"
    r"reference|references|bibliography|author|authors)\b",
    re.IGNORECASE,
)


def looks_like_question(text: str) -> bool:
    """
    Decide whether a numbered line is likely to be an actual question.

    We deliberately prefer review/uncertain over silently treating
    headings, references, or bibliography entries as questions.
    """

    text = text.strip()

    if not text:
        return False

    # Very long numbered lines are often references/headings.
    if len(text) > 220:
        return False

    # Common reference/bibliography indicators.
    if NON_QUESTION_PATTERN.search(text):
        return False

    # Actual question wording.
    if QUESTION_WORD_PATTERN.search(text):
        return True

    # A question mark is a strong signal.
    if "?" in text:
        return True

    return False


def extract_questions(text: str) -> list[dict]:
    """
    Extract likely questions and options from extracted/OCR text.

    Returns:
        list[dict]
    """

    lines = text.splitlines()

    questions = []
    current_question = None
    current_page = None

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            continue

        # Page marker.
        page_match = re.match(
            r"^\[PAGE\s+(\d+)\]$",
            line,
            re.IGNORECASE,
        )

        if page_match:
            current_page = int(page_match.group(1))
            continue

        # Detect numbered question candidate.
        question_match = QUESTION_START_PATTERN.match(line)

        if question_match:
            question_number = question_match.group(1)
            question_text = question_match.group(2).strip()

            # Only start a new question when the line looks like
            # an actual question.
            if looks_like_question(question_text):

                if current_question is not None:
                    questions.append(current_question)

                current_question = {
                    "question_number": question_number,
                    "question_text": question_text,
                    "options": {},
                    "question_type": "unknown",
                    "source_pages": (
                        str(current_page)
                        if current_page
                        else None
                    ),
                    "extraction_confidence": 0.0,
                    "review_status": "review",
                }

                continue

        # Detect options.
        option_match = OPTION_PATTERN.match(line)

        if option_match and current_question is not None:
            option_key = option_match.group(1).upper()
            option_text = option_match.group(2).strip()

            current_question["options"][option_key] = option_text
            continue

        # Continuation text.
        if current_question is not None:
            current_question["question_text"] += " " + line

    # Save final question.
    if current_question is not None:
        questions.append(current_question)

    # Calculate confidence.
    for question in questions:
        question_text = question["question_text"]
        option_count = len(question["options"])

        if option_count >= 2:
            question["question_type"] = "MCQ"

        if (
            question["question_number"]
            and question_text.strip()
            and option_count >= 2
        ):
            question["extraction_confidence"] = 0.95
            question["review_status"] = "extracted"

        elif (
            question["question_number"]
            and question_text.strip()
            and looks_like_question(question_text)
        ):
            question["extraction_confidence"] = 0.80
            question["review_status"] = "review"

        else:
            question["extraction_confidence"] = 0.40
            question["review_status"] = "uncertain"

    return questions