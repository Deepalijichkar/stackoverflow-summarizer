import requests
import time
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

    # Stack Overflow rate limits — if we hit it, wait and retry
    if response.status_code == 429:
        print("Rate limited by Stack Overflow. Waiting 30 seconds...")
        time.sleep(30)
        response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Error fetching '{tag}': {response.status_code} — skipping.")
        return []

    data = response.json()

    # Check if API quota is running low
    quota_remaining = data.get("quota_remaining", 999)
    if quota_remaining < 10:
        print(f"⚠️  API quota low: {quota_remaining} requests remaining today.")

    questions = data.get("items", [])

    cleaned = []
    for q in questions:
        cleaned.append({
            "id":           q["question_id"],
            "title":        q["title"],
            "body":         clean_html(q.get("body", "")),
            "tags":         q.get("tags", []),
            "score":        q.get("score", 0),
            "answer_count": q.get("answer_count", 0),
            "link":         q.get("link", "")
        })

    return cleaned


if __name__ == "__main__":
    # Step 1 — make sure DB and table exist
    create_table()

    # Step 2 — fetch questions for all tags
    tags = [
        # Core languages
        "python", "javascript", "java", "c++", "c#",
        "typescript", "php", "ruby", "swift", "kotlin",

        # Web frontend
        "html", "css", "react", "angular", "vue.js",
        "bootstrap", "jquery",

        # Web backend
        "nodejs", "django", "flask", "fastapi",
        "spring-boot", "express",

        # Database
        "sql", "mysql", "postgresql", "mongodb",
        "sqlite", "redis",

        # Data & AI
        "pandas", "numpy", "matplotlib", "scikit-learn",
        "tensorflow", "pytorch", "machine-learning",

        # DevOps & Tools
        "git", "docker", "linux", "bash",
        "aws", "github-actions",

        # Mobile
        "android", "ios", "react-native", "flutter",

        # CS Concepts
        "algorithms", "data-structures", "recursion",
        "object-oriented", "rest", "api"
    ]

    total_saved = 0
    total_skipped = 0

    for tag in tags:
        questions = fetch_questions(tag=tag, count=50)

        saved = 0
        for q in questions:
            insert_question(q)
            saved += 1
            total_saved += 1

        print(f"✓ Saved {saved} '{tag}' questions. Total so far: {total_saved}")

        # Small delay between requests to be respectful to the API
        # and avoid hitting rate limits
        time.sleep(1)

    print(f"\n{'='*50}")
    print(f"DONE! Total questions saved: {total_saved}")

    # Verify by reading back from DB
    all_q = get_all_questions()
    print(f"Confirmed: {len(all_q)} rows in database.")
    print(f"{'='*50}")