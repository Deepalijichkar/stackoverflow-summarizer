import os
from groq import Groq
from dotenv import load_dotenv
from embeddings import find_similar_questions

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_context(similar_questions):
    """
    Formats similar questions into readable context for the AI.
    Like giving it study material before asking a question.
    """
    if not similar_questions:
        return "No similar questions found."

    context = "Here are the most relevant Stack Overflow discussions:\n\n"

    for i, q in enumerate(similar_questions):
        context += f"{i+1}. Question: {q['title']}\n"
        context += f"   Similarity Score: {q['similarity']}\n"
        context += f"   Stack Overflow Votes: {q['score']}\n"
        context += f"   Link: {q['link']}\n\n"

    return context


def generate_answer(user_query):
    """
    Full RAG pipeline:
    1. Find similar questions using embeddings
    2. Build context from those questions
    3. Send context + query to Groq (Llama 3)
    4. Return the answer
    """

    print(f"\nSearching for similar questions...")
    similar = find_similar_questions(user_query, top_k=5)

    if not similar:
        return "No relevant questions found in the database.", []

    print(f"Found {len(similar)} similar questions. Asking AI...")

    context = build_context(similar)

    prompt = f"""You are a helpful programming assistant.
A developer has asked the following question:

"{user_query}"

Based on these relevant Stack Overflow discussions:

{context}

Please provide:
1. A clear, direct answer to their question
2. The key concepts they should understand
3. A simple code example if relevant
4. Links to the most helpful Stack Overflow discussions

Keep your answer beginner-friendly but technically accurate."""

    # Call Groq API with Llama 3
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",   # Meta's Llama 3 model, free on Groq
        messages=[
            {
                "role": "system",
                "content": "You are a helpful programming assistant that explains concepts clearly to beginners."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=1000
    )

    answer = response.choices[0].message.content
    return answer, similar


if __name__ == "__main__":
    print("=== Stack Overflow AI Summarizer ===\n")

    query = "how do I iterate over a list in python"
    print(f"Question: {query}")
    print("-" * 50)

    result = generate_answer(query)

    if isinstance(result, tuple):
        answer, similar_qs = result
        print("\n--- Similar Questions Found ---")
        for q in similar_qs:
            print(f"  [{q['similarity']}] {q['title']}")

        print("\n--- AI Generated Answer ---")
        print(answer)
    else:
        print(result)