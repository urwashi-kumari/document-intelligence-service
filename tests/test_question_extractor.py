from backend.services.question_extractor import extract_questions


def test_extract_mcq_questions():
    text = """
[PAGE 1]

1. What is Python?
A. A programming language
B. A database
C. An operating system
D. A web browser

2. Which data structure follows FIFO?
A. Stack
B. Queue
C. Tree
D. Graph
"""

    questions = extract_questions(text)

    assert len(questions) == 2

    assert questions[0]["question_number"] == "1"
    assert questions[0]["question_text"] == "What is Python?"
    assert questions[0]["question_type"] == "MCQ"
    assert questions[0]["options"]["A"] == "A programming language"
    assert questions[0]["options"]["D"] == "A web browser"
    assert questions[0]["source_pages"] == "1"
    assert questions[0]["review_status"] == "extracted"

    assert questions[1]["question_number"] == "2"
    assert questions[1]["options"]["B"] == "Queue"


def test_ignore_bibliography_entries():
    text = """
[PAGE 2]

1. MONGODB FUNDAMENTALS: A HANDS-ON GUIDE
by AMIT PHALTANKAR, JUNED AHSAN, PACKT PUBLISHING

2. MONGODB IN ACTION by KYLE BANKER,
Manning Publication
"""

    questions = extract_questions(text)

    assert len(questions) == 0