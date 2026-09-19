import re


QUESTION_START_PATTERN = re.compile(
    r"(?<!\d)(\d+)[\.\):-]\s+"
)

OPTION_PATTERN = re.compile(
    r"^\s*[\(\[]?([A-Ha-h])[\)\].:-]\s*(.+)$"
)

NON_QUESTION_PATTERN = re.compile(
    r"\b(by|publication|publishing|publisher|manning|packt|"
    r"reference|references|bibliography|author|authors|"
    r"prepared\s+by)\b",
    re.IGNORECASE,
)

QUESTION_WORD_PATTERN = re.compile(
    r"\b(what|which|who|where|when|why|how|explain|define|describe|"
    r"identify|list|compare|calculate|write|state|discuss|select|"
    r"choose|give|mention|output|correct|following|process|"
    r"syntax|year|language|function|operator|value|use|used|"
    r"true|false|support|cannot|does|is|are|was|were|"
    r"created|developed)\b",
    re.IGNORECASE,
)

CODE_PATTERN = re.compile(
    r"(=|\(|\)|\[|\]|::|->|\\|"
    r"\bprint\b|\bopen\b|\bfrom\b|\bimport\b|\bdef\b)",
    re.IGNORECASE,
)


def looks_like_question(text: str) -> bool:
    text = text.strip()

    if not text:
        return False

    if len(text) > 220:
        return False

    if NON_QUESTION_PATTERN.search(text):
        return False

    if "?" in text:
        return True

    if QUESTION_WORD_PATTERN.search(text):
        return True

    if CODE_PATTERN.search(text):
        return True

    return False


def split_numbered_questions(
    text: str,
    expected_number: int | None = None,
) -> list[tuple[str, str]]:
    """
    Split a line containing numbered questions.

    Only question numbers that follow the expected sequence are
    treated as question starts. This prevents values such as:

        Python 3.0
        a[3:5]
        list1.addEnd(5)

    from being interpreted as new questions.
    """

    matches = list(QUESTION_START_PATTERN.finditer(text))

    if not matches:
        return []

    valid_matches = []

    for match in matches:
        number = int(match.group(1))

        if expected_number is None:
            continue

        # Only accept the next expected question number.
        if number == expected_number:
            valid_matches.append(match)

    if not valid_matches:
        return []

    results = []

    for index, match in enumerate(valid_matches):
        question_number = match.group(1)

        start = match.end()

        if index + 1 < len(valid_matches):
            end = valid_matches[index + 1].start()
        else:
            end = len(text)

        question_text = text[start:end].strip()

        if question_text:
            results.append(
                (
                    question_number,
                    question_text,
                )
            )

    return results


def extract_questions(text: str) -> list[dict]:
    lines = text.splitlines()

    questions = []
    current_question = None
    current_page = None

    expected_question_number = 1

    for raw_line in lines:
        line = raw_line.strip()

        if not line:
            continue

        # Page marker
        page_match = re.match(
            r"^\[PAGE\s+(\d+)\]$",
            line,
            re.IGNORECASE,
        )

        if page_match:
            current_page = int(page_match.group(1))
            continue

        # Detect the next expected numbered question.
        numbered_parts = split_numbered_questions(
            line,
            expected_number=expected_question_number,
        )

        if numbered_parts:
            for question_number, question_text in numbered_parts:

                if not looks_like_question(question_text):
                    continue

                if current_question is not None:
                    questions.append(current_question)

                current_question = {
                    "question_number": question_number,
                    "question_text": question_text,
                    "options": {},
                    "question_type": "unknown",
                    "source_pages": (
                        str(current_page)
                        if current_page is not None
                        else None
                    ),
                    "extraction_confidence": 0.0,
                    "review_status": "review",
                }

                expected_question_number = (
                    int(question_number) + 1
                )

            continue

        # Standard option line.
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