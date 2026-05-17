import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from database import get_all_questions, get_connection

# Load the model — this downloads ~80MB on first run, then cached locally
# all-MiniLM-L6-v2 is small, fast, and very good for sentence similarity
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded!")


def get_embedding(text):
    """
    Converts a string of text into a vector of 384 numbers.
    
    Example:
    "how to use yield in python" 
    → [0.231, -0.512, 0.089, ... 384 numbers total]
    
    Similar sentences will produce similar number patterns.
    """
    return model.encode(text)


def store_embeddings():
    """
    Goes through every question in the DB,
    generates its embedding, and saves it back.
    
    We store embeddings as binary blobs (bytes) in SQLite
    because SQLite doesn't have a vector column type.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Add embedding column if it doesn't exist yet
    try:
        cursor.execute("ALTER TABLE questions ADD COLUMN embedding BLOB")
        conn.commit()
        print("Added embedding column to database.")
    except Exception:
        print("Embedding column already exists, skipping.")

    # Fetch all questions that don't have embeddings yet
    cursor.execute("SELECT id, title, body FROM questions WHERE embedding IS NULL")
    rows = cursor.fetchall()

    if not rows:
        print("All questions already have embeddings!")
        conn.close()
        return

    print(f"Generating embeddings for {len(rows)} questions...")

    for i, row in enumerate(rows):
        # Combine title + body for richer embedding
        # Title alone misses context; body alone is too noisy
        text = f"{row['title']}. {row['body'][:500]}"  # cap body at 500 chars

        embedding = get_embedding(text)

        # Convert numpy array → bytes for SQLite storage
        embedding_bytes = embedding.tobytes()

        cursor.execute(
            "UPDATE questions SET embedding = ? WHERE id = ?",
            (embedding_bytes, row["id"])
        )

        # Progress update every 10 questions
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(rows)}...")

    conn.commit()
    conn.close()
    print(f"Done! Embeddings stored for {len(rows)} questions.")


def find_similar_questions(user_query, top_k=5):
    """
    The core search function.
    
    Takes a user's question (plain English),
    converts it to an embedding,
    compares it against all stored embeddings,
    returns the top_k most similar questions.
    
    cosine_similarity measures the angle between two vectors.
    Score of 1.0 = identical meaning
    Score of 0.0 = completely unrelated
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Only fetch questions that have embeddings
    cursor.execute("SELECT id, title, link, score, embedding FROM questions WHERE embedding IS NOT NULL")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No embeddings found. Run store_embeddings() first.")
        return []

    # Convert user query to embedding
    query_embedding = get_embedding(user_query).reshape(1, -1)

    # Reconstruct all stored embeddings from bytes back to numpy arrays
    stored_embeddings = []
    metadata = []

    for row in rows:
        emb = np.frombuffer(row["embedding"], dtype=np.float32)
        stored_embeddings.append(emb)
        metadata.append({
            "id":    row["id"],
            "title": row["title"],
            "link":  row["link"],
            "score": row["score"]
        })

    # Stack all embeddings into a matrix for bulk comparison
    embeddings_matrix = np.array(stored_embeddings)

    # Calculate similarity between query and ALL questions at once
    similarities = cosine_similarity(query_embedding, embeddings_matrix)[0]

    # Get indices of top_k highest scores
    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for idx in top_indices:
        results.append({
            **metadata[idx],
            "similarity": round(float(similarities[idx]), 3)
        })

    return results


if __name__ == "__main__":
    # Step 1 — generate and store embeddings for all DB questions
    store_embeddings()

    # Step 2 — test similarity search with a sample query
    print("\n--- Testing Similarity Search ---")
    query = "how do I iterate over a list in python"
    print(f"Query: '{query}'")
    print()

    results = find_similar_questions(query, top_k=5)

    for i, r in enumerate(results):
        print(f"{i+1}. [{r['similarity']}] {r['title']}")
        print(f"   Score: {r['score']} | {r['link']}")
        print()