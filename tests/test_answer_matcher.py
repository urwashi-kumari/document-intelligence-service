from backend.services.answer_matcher import (
    extract_answer_key,
    match_answers_to_questions,
)


def test_extract_answer_key():
    text = """
    ANSWER KEY

    1. B
    2. C
    3. A
    4. D
    """

    answers = extract_answer_key(text)

    assert answers == {
        "1": "B",
        "2": "C",
        "3": "A",
        "4": "D",
    }


def test_extract_answer_key_with_different_formats():
    text = """
    Q1: A
    Question 2 - B
    3) C
    4. D
    """

    answers = extract_answer_key(text)

    assert answers == {
        "1": "A",
        "2": "B",
        "3": "C",
        "4": "D",
    }


def test_match_answers_to_questions():
    questions = [
        {
            "question_number": "1",
            "question_text": "What is Python?",
            "question_type": "MCQ",
            "options": {
                "A": "Database",
                "B": "Programming language",
                "C": "Browser",
                "D": "Operating system",
            },
            "extraction_confidence": 0.95,
            "review_status": "extracted",
        },
        {
            "question_number": "2",
            "question_text": "Which data structure follows FIFO?",
            "question_type": "MCQ",
            "options": {
                "A": "Stack",
                "B": "Tree",
                "C": "Queue",
                "D": "Graph",
            },
            "extraction_confidence": 0.95,
            "review_status": "extracted",
        },
    ]

    answer_key = {
        "1": "B",
        "2": "C",
    }

    results = match_answers_to_questions(questions, answer_key)

    assert results[0]["answer"] == "B"
    assert results[0]["answer_confidence"] == 0.98

    assert results[1]["answer"] == "C"
    assert results[1]["answer_confidence"] == 0.98


def test_missing_answer_requires_review():
    questions = [
        {
            "question_number": "1",
            "question_text": "What is Python?",
            "question_type": "MCQ",
            "options": {
                "A": "Database",
                "B": "Programming language",
            },
            "extraction_confidence": 0.95,
            "review_status": "extracted",
        },
        {
            "question_number": "2",
            "question_text": "Which data structure follows FIFO?",
            "question_type": "MCQ",
            "options": {
                "A": "Stack",
                "B": "Queue",
            },
            "extraction_confidence": 0.95,
            "review_status": "extracted",
        },
    ]

    answer_key = {
        "1": "B",
    }

    results = match_answers_to_questions(questions, answer_key)

    assert results[0]["answer"] == "B"

    # Question 2 has no explicit answer-key entry.
    # It must NOT receive a guessed answer.
    assert results[1]["answer"] is None
    assert results[1]["answer_confidence"] == 0.0
    assert results[1]["review_status"] == "review"