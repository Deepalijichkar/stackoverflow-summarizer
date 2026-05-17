import requests
from bs4 import BeautifulSoup
from database import create_table, insert_question, get_all_questions

BASE_URL = "https://api.stackexchange.com/2.3"

def clean_html(html_text):
    """
    Stack Overflow returns HTML like <p>How do I use <code>yield</code>?</p>
    This strips all tags and returns plain text.
    BeautifulSoup is a library that parses HTML like a browser does.
    """
    if not html_text:
        return ""
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def fetch_questions(tag="python", count=50):
    """
    Fetches programming questions from Stack Overflow.
    """
    url = f"{BASE_URL}/questions"

    params = {
        "order": "desc",
        "sort": "votes",
        "tagged": tag,
        "site": "stackoverflow",
        "pagesize": count,
        "filter": "withbody"
    }

    print(f"Fetching {count} questions tagged '{tag}'...")

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []

    data = response.json()
    questions = data.get("items", [])

    cleaned = []
    for q in questions:
        cleaned.append({
            "id":           q["question_id"],
            "title":        q["title"],
            "body":         clean_html(q.get("body", "")),  # clean HTML here
            "tags":         q.get("tags", []),
            "score":        q.get("score", 0),
            "answer_count": q.get("answer_count", 0),
            "link":         q.get("link", "")
        })

    return cleaned


if __name__ == "__main__":
    # Step 1 — make sure DB and table exist
    create_table()

    # Step 2 — fetch questions for multiple tags
    tags = ["python", "javascript", "sql"]
    total = 0

    for tag in tags:
        questions = fetch_questions(tag=tag, count=50)
        for q in questions:
            insert_question(q)
            total += 1
        print(f"Saved {len(questions)} '{tag}' questions to database.")

    print(f"\nTotal questions in DB: {total}")

    # Step 3 — verify by reading back from DB
    all_q = get_all_questions()
    print(f"Confirmed: {len(all_q)} rows in database.")