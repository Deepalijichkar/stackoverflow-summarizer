import streamlit as st
from summarizer import generate_answer
from embeddings import find_similar_questions

# --- Page Config ---
st.set_page_config(
    page_title="Stack Overflow AI Summarizer",
    page_icon="🔍",
    layout="centered"
)

# --- Header ---
st.title("🔍 Stack Overflow AI Summarizer")
st.markdown("""
Ask any programming question and get an AI-generated answer 
based on real Stack Overflow discussions.
""")

st.divider()

# --- Input ---
query = st.text_input(
    "💬 Ask a programming question:",
    placeholder="e.g. how do I iterate over a list in python"
)

col1, col2 = st.columns([1, 4])
with col1:
    search_btn = st.button("🚀 Get Answer", type="primary")

# --- Results ---
if search_btn and query:

    # Similar questions section
    with st.spinner("Searching similar Stack Overflow questions..."):
        similar = find_similar_questions(query, top_k=5)

    if not similar:
        st.error("No similar questions found. Try a different query.")
    else:
        # Show similar questions
        st.subheader("📚 Similar Stack Overflow Discussions Found")
        for q in similar:
            with st.expander(f"[{q['similarity']}] {q['title']}"):
                st.write(f"**Votes:** {q['score']}")
                st.write(f"**Link:** [{q['link']}]({q['link']})")

        st.divider()

        # Generate AI answer
        with st.spinner("Generating AI answer..."):
            result = generate_answer(query)

        if isinstance(result, tuple):
            answer, _ = result

            st.subheader("🤖 AI Generated Answer")
            st.markdown(answer)
        else:
            st.error(result)

elif search_btn and not query:
    st.warning("Please enter a question first.")

# --- Footer ---
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8em;'>
Built with Python · Stack Overflow API · Sentence Transformers · Groq (Llama 3) · Streamlit
</div>
""", unsafe_allow_html=True)
