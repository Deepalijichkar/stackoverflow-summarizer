import sqlite3

DB_NAME = "questions.db"

def get_connection():
    """
    Creates (or opens) the SQLite database file.
    Think of this like opening an Excel file before editing it.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # lets us access columns by name instead of index
    return conn


def create_table():
    """
    Creates the 'questions' table if it doesn't exist yet.
    A table is like a spreadsheet — columns defined here, rows added later.
    """
    conn = get_connection()
    cursor = conn.cursor()  # cursor = the pen that writes to the database

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id          INTEGER PRIMARY KEY,   -- unique Stack Overflow question ID
            title       TEXT NOT NULL,         -- question title
            body        TEXT,                  -- full question text (cleaned)
            tags        TEXT,                  -- stored as comma-separated string
            score       INTEGER,               -- upvote score (quality signal)
            answer_count INTEGER,              -- number of answers
            link        TEXT                   -- URL to original question
        )
    """)

    conn.commit()   # save changes
    conn.close()    # close the file
    print("Database and table ready.")


def insert_question(question):
    """
    Inserts one question into the database.
    Skips it silently if the same question ID already exists (no duplicates).
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO questions 
        (id, title, body, tags, score, answer_count, link)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        question["id"],
        question["title"],
        question["body"],
        ",".join(question["tags"]),   # convert list → "python,django,flask"
        question["score"],
        question["answer_count"],
        question["link"]
    ))

    conn.commit()
    conn.close()


def get_all_questions():
    """
    Retrieves every question from the database.
    Used later for generating embeddings.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM questions")
    rows = cursor.fetchall()

    conn.close()
    return rows


if __name__ == "__main__":
    create_table()
    print(f"Table created successfully.")