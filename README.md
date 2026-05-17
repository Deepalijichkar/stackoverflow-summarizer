wn# 🔍 Stack Overflow AI Summarizer

An AI-powered tool that fetches real Stack Overflow discussions, 
finds semantically similar questions using NLP embeddings, 
and generates summarized answers using Llama 3.

## 🎯 Problem It Solves

Stack Overflow has 58 million questions. When a beginner searches something,
they get dozens of duplicate threads, outdated answers, and technical jargon.
This tool finds the most relevant discussions and synthesizes them into one
clean, beginner-friendly answer.

## 🏗️ Architecture
User Query → Sentence Embeddings → Semantic Search → RAG → AI Answer
## 🛠️ Tech Stack

- **Python** — core language
- **Stack Overflow API** — 2000+ real programming discussions
- **SQLite** — local database for storing questions
- **Sentence Transformers** (all-MiniLM-L6-v2) — NLP embeddings for semantic search
- **Groq API** (Llama 3) — AI answer generation
- **Streamlit** — web interface

## 🚀 How It Works

1. Fetches top-voted Stack Overflow questions across 50+ programming tags
2. Stores and cleans questions in SQLite database
3. Generates vector embeddings for each question using Sentence Transformers
4. When user asks a question, finds semantically similar discussions using cosine similarity
5. Uses RAG (Retrieval Augmented Generation) to generate a contextualized answer

## 💡 Key Concepts Demonstrated

- **RAG (Retrieval Augmented Generation)** — architecture behind GitHub Copilot, Notion AI, Perplexity
- **Vector Embeddings** — semantic search beyond keyword matching
- **Cosine Similarity** — measuring meaning distance between questions
- **Data Pipeline** — fetch → clean → store → embed → retrieve → generate
- **API Integration** — Stack Overflow API + Groq API

## 📦 Setup

### 1. Clone the repo
git clone https://github.com/Deepalijichkar/stackoverflow-summarizer.git
cd stackoverflow-summarizer

### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

### 3. Install dependencies
pip install -r requirements.txt

### 4. Add API key
Create a .env file:
GROQ_API_KEY=your_groq_api_key_here

### 5. Fetch data and generate embeddings
python fetcher.py
python embeddings.py

### 6. Run the app
streamlit run app.py

## 📊 Stats
- 2175+ Stack Overflow questions indexed
- 50+ programming tags covered
- Semantic similarity search with cosine distance
- Answers grounded in community-verified discussions