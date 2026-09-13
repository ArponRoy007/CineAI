# RoyReview — AI-Powered Personalized Movie Reviews & Recommendations

> A personal movie-review platform enhanced with Generative AI, RAG, semantic search, hybrid recommendations, analytics, and interaction-based personalization.

**Built with:** Python · Streamlit · MongoDB Atlas · ChromaDB · Sentence Transformers · Groq · TMDB · pytest

---

## Overview

RoyReview is a full-stack-style Python/Streamlit movie-review application that combines a real movie product with a Generative AI layer.

Users can:

- Browse and search movies
- View Roy's verified ratings, verdicts, and personal reviews
- Explore movie details and external metadata
- Get personalized movie recommendations
- Ask **Ask Roy** natural-language questions about Roy's review knowledge base
- Explore movie analytics
- Build a lightweight personalized experience from interactions

The central AI principle is simple:

> **The LLM generates the explanation, but Roy's verified reviews remain the source of truth.**

Only confirmed reviews are indexed into the RAG knowledge base. AI-generated draft reviews are kept separate until explicitly approved.

---

## Key Features

### 🎬 Movie Platform
- Movie dashboard and search
- Movie detail pages
- Posters and metadata through TMDB
- Roy's personal 5-point ratings
- `Must Watch`, `Good Watch`, and `Don't Watch` verdicts
- Personal review text
- IMDb information when available

### 🤖 Ask Roy — Generative AI
- Natural-language questions about Roy's movie reviews
- Movie-specific RAG when opened from a movie page
- Semantic retrieval using embeddings
- Grounded prompt design
- Unsupported-question fallback
- Bounded agentic RAG with tool-based retrieval

### 🔎 Hybrid Search
RoyReview uses the right retrieval method for different query types:

- **MongoDB:** structured filters such as ratings and verdicts
- **ChromaDB:** semantic and opinion-based questions
- **Hybrid logic:** combines structured and semantic signals when appropriate

### 🍿 Recommendations
- Content-based recommendations
- Embedding similarity
- Genre overlap
- Roy-rating quality
- Hybrid recommendation scoring
- User preference signal
- Source-movie exclusion
- Safer preference for positively reviewed movies

### 📊 Movie Analytics
- Rating distribution
- Verdict distribution
- Genre patterns
- Zone patterns
- Year-wise trends
- Highest-rated movies
- Review statistics

### 👤 Personalization
RoyReview records lightweight interaction events such as:

- `viewed`
- `searched`
- `asked_roy`
- `favorited`

Interaction history is used to infer genre and zone preferences. Personalization becomes active after a minimum interaction threshold; new users continue to receive the generic movie experience until enough history exists.

Interaction logging is best-effort and non-blocking so a logging failure does not stop the main user flow.

### 🔐 Authentication & Admin
- Signup
- Login
- Session-based authentication
- Logout
- Admin authentication
- Protected application pages
- Add/manage movie reviews
- Review approval workflow
- RAG ingestion workflow

---

## Generative AI Architecture

```text
                     User
                       │
                       ▼
                Streamlit Application
                       │
          ┌────────────┼─────────────┐
          ▼            ▼             ▼
     Movie/Search   Ask Roy      Recommendations
          │            │             │
          ▼            ▼             ▼
       MongoDB      Query Router   Hybrid Scoring
          │            │             │
          │      ┌─────┴─────┐       │
          │      ▼           ▼       │
          │  MongoDB      ChromaDB   │
          │  Exact       Semantic   │
          │  Search      Retrieval  │
          │      └─────┬─────┘       │
          │            ▼             │
          │      Retrieved Context   │
          │            │             │
          │            ▼             │
          │        Groq LLM          │
          │            │             │
          └────────────┴─────────────┘
                       │
                       ▼
                  User Response
```

---

## RAG Pipeline

```text
Confirmed Movie Review
        │
        ▼
Structured Review Document
        │
        ▼
Sentence Transformer
(all-MiniLM-L6-v2)
        │
        ▼
Embedding
        │
        ▼
ChromaDB
(royreview_reviews)
        ▲
        │
User Question
        │
        ▼
Question Embedding
        │
        ▼
Similarity Retrieval
        │
        ▼
Relevant Review Context
        │
        ▼
Grounding Prompt
        │
        ▼
Groq LLM
(openai/gpt-oss-120b)
        │
        ▼
Grounded Answer
```

### Grounding Rules

Ask Roy is instructed to:

- Use retrieved RoyReview context as its source of truth
- Never invent Roy's opinion
- Never invent a rating or verdict
- Never claim Roy reviewed a movie when it is not in the knowledge base
- Keep Roy's personal opinion separate from general movie facts
- Return a controlled fallback when the available context does not support an answer

Fallback:

```text
I couldn't find that in Roy's movie notes.
```

---

## Agentic RAG

RoyReview also includes a bounded agentic retrieval path.

The agent can use a small set of controlled tools for:

1. Movie-title search
2. Verdict/rating filtering
3. Scoped movie-review retrieval
4. General semantic review search

The agent is intentionally bounded to a maximum of **3 tool calls** per request and preserves the same grounding rules as the normal RAG path.

This provides an agentic architecture without allowing unrestricted tool execution or unsupported movie knowledge.

---

## Review Integrity

A major design decision is separating Roy's actual opinions from AI-generated content.

```text
New / Draft Review
       │
       ▼
NEEDS_USER_APPROVAL
       │
       ├── Not approved ──► Not indexed
       │
       ▼
    CONFIRMED
       │
       ▼
Embedding Generation
       │
       ▼
ChromaDB
       │
       ▼
Ask Roy Knowledge Base
```

Only confirmed reviews are ingested into RAG.

This prevents an AI-generated draft from accidentally becoming part of Roy's personal opinion database.

---

## Recommendation Architecture

RoyReview combines several signals:

```text
Content Similarity
       +
Embedding Similarity
       +
Roy Rating Quality
       +
Genre / Preference Match
       │
       ▼
Hybrid Recommendation Score
       │
       ▼
Ranked Movies
```

Personalization acts as an additional ranking signal rather than a hard dependency.

---

## Personalization Architecture

```text
User Interaction
      │
      ├── viewed
      ├── searched
      ├── asked_roy
      └── favorited
             │
             ▼
      MongoDB Interaction Data
             │
             ▼
     Preference Profile
       ┌─────┴─────┐
       ▼           ▼
    Genres       Zones
       └─────┬─────┘
             ▼
    Recommendation Signal
             │
             ▼
       Personalized Ranking
```

Interaction weights are intentionally different: stronger actions such as favoriting and asking about a movie contribute more than a simple view.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python |
| UI | Streamlit |
| Database | MongoDB Atlas |
| Movie Metadata | TMDB API |
| LLM Provider | Groq |
| LLM Model | `openai/gpt-oss-120b` |
| Embedding Model | `all-MiniLM-L6-v2` |
| Embedding Library | Sentence Transformers |
| Vector Database | ChromaDB |
| ML / Evaluation | scikit-learn |
| Testing | pytest |
| Version Control | Git / GitHub |
| Deployment Target | Streamlit Community Cloud |

---

## Project Structure

```text
RoyReview/
│
├── app.py
│
├── config/
│   ├── __init__.py
│   └── settings.py
│
├── database/
│   ├── __init__.py
│   ├── mongodb.py
│   └── models.py
│
├── auth/
│   ├── __init__.py
│   ├── login.py
│   ├── signup.py
│   └── security.py
│
├── movies/
│   ├── __init__.py
│   ├── movie_service.py
│   ├── tmdb.py
│   └── imdb.py
│
├── rag/
│   ├── __init__.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── prompts.py
│   ├── qa.py
│   ├── ingest.py
│   ├── hybrid.py
│   └── evaluation.py
│
├── ai/
│   ├── __init__.py
│   ├── llm.py
│   ├── recommender.py
│   ├── agent.py
│   └── personalization.py
│
├── ui/
│   ├── __init__.py
│   ├── home.py
│   ├── dashboard.py
│   ├── movie_details.py
│   ├── ask_roy.py
│   ├── explore.py
│   ├── analytics.py
│   ├── profile.py
│   └── design.py
│
├── scripts/
│   ├── import_movies.py
│   ├── build_embeddings.py
│   ├── rebuild_embeddings.py
│   ├── run_rag_eval.py
│   └── tune_recommender.py
│
├── tests/
│   ├── rag_eval/
│   │   └── eval_set.json
│   ├── test_auth.py
│   ├── test_movies.py
│   ├── test_database.py
│   ├── test_rag.py
│   ├── test_agent.py
│   ├── test_analytics.py
│   ├── test_evaluation.py
│   ├── test_personalization.py
│   ├── test_rebuild.py
│   ├── test_recommender.py
│   ├── test_resilience.py
│   └── test_smoke.py
│
├── data/
├── utils/
│
├── .streamlit/
│   └── secrets.toml          # local only; never commit
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Database Design

### MongoDB Atlas

Database:

```text
royreview
```

Primary collection:

```text
movies
```

Typical movie fields:

```text
movie_id
title
year
zone
genre
roy_rating
verdict
review_text
review_status
ingest_to_rag
tmdb_id
poster_url
tmdb_overview
tmdb_rating
imdb_id
```

A separate user-interaction collection stores personalization events.

### ChromaDB

Collection:

```text
royreview_reviews
```

Each vector record contains:

- Document ID
- Review document
- Embedding
- Movie metadata

The current verified local knowledge base contains **84 embedded confirmed review documents**.

---

## External APIs

### TMDB

Used for:

- Movie metadata
- Posters
- Backdrops
- Release information
- Genres
- TMDB ratings
- IMDb IDs when available

Roy's rating is stored separately from external ratings.

### Groq

Used to generate the final natural-language response for Ask Roy.

The LLM is not treated as the source of Roy's opinions. Retrieved review context is supplied to it at runtime.

---

## Dataset

The application contains **100+ movie records**, including:

- Confirmed reviews
- AI-draft candidate reviews
- Movie metadata
- Posters
- Review status
- RAG ingestion status

Only confirmed reviews are treated as Roy's actual opinions.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/ArponRoy007/RoyReview.git
cd RoyReview
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

macOS / Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure local secrets

Create:

```text
.streamlit/secrets.toml
```

Use the secret names expected by the application.

Example structure:

```toml
MONGODB_URI = "your-mongodb-connection-string"
TMDB_API_KEY = "your-tmdb-api-key"
GROQ_API_KEY = "your-groq-api-key"

ADMIN_USERNAME = "your-admin-username"
ADMIN_PASSWORD = "your-admin-password"
```

**Never commit this file or expose the values publicly.**

### 5. Run the application

```bash
streamlit run app.py
```

---

## Testing

RoyReview has an automated test suite covering authentication, database behavior, movie services, RAG components, recommendations, personalization, resilience, rebuilding, analytics, agent behavior, and smoke-level integration.

Latest verified result:

```text
70 passed, 1 warning
```

Compilation verification:

```bash
python -m compileall -q .
```

The compilation check completed without errors.

The remaining warning is a dependency-side ChromaDB/Python deprecation warning and does not cause test failure.

### Run tests

```bash
pytest -q
```

### Run compilation check

```bash
python -m compileall -q .
```

---

## RAG Evaluation

The project contains a labeled evaluation set:

```text
tests/rag_eval/eval_set.json
```

It covers:

- Grounded questions
- Unsupported questions
- Ambiguous titles
- Typo / partial-title inputs
- Expected facts and fallback behavior

Run the baseline evaluation manually:

```bash
python scripts/run_rag_eval.py
```

Run the agentic path:

```bash
python scripts/run_rag_eval.py --agent
```

These evaluations call the Groq API, so they are intentionally separate from the normal `pytest` suite.

### Evaluation note

The current evaluation shows **strong retrieval performance**, while answer faithfulness/correctness still has room for improvement. This is expected to be treated as an engineering optimization area rather than hidden behind the automated test count.

The retrieval layer should therefore not be described as "perfect" simply because the automated suite is green.

---

## Rebuilding the RAG Knowledge Base

When confirmed reviews change or new confirmed reviews are added:

```bash
python scripts/rebuild_embeddings.py
```

The workflow is:

```text
MongoDB Confirmed Reviews
        ↓
Review Document Preparation
        ↓
Embedding Generation
        ↓
ChromaDB Upsert
        ↓
Updated RAG Knowledge Base
```

---

## Recommendation Tuning

The project includes a small sanity-check script for recommendation ranking:

```bash
python scripts/tune_recommender.py
```

It checks representative recommendation pairs and helps verify that expected related movies rank appropriately.

---

## Security

### Never commit:

```text
.streamlit/secrets.toml
.env
API keys
Database passwords
Private credentials
```

Secrets should be supplied through Streamlit's secret-management system in deployment.

If a credential is accidentally exposed, rotate it immediately.

---

## Deployment

### Recommended free deployment

**Streamlit Community Cloud**

Target architecture:

```text
GitHub
   │
   ▼
Streamlit Community Cloud
   │
   ├── MongoDB Atlas
   ├── Groq API
   └── TMDB API
```

Deployment settings:

```text
Repository: ArponRoy007/RoyReview
Branch: main
Main file: app.py
```

Configure the required secrets in the deployment platform rather than committing `.streamlit/secrets.toml`.

### Important ChromaDB deployment consideration

RoyReview currently uses a local persistent ChromaDB directory for its vector store.

A cloud deployment should not assume that local runtime storage is permanent. Before treating the deployed RAG store as production-grade, verify how the deployment environment persists or rebuilds the vector database.

For a college/demo deployment, the vector-store strategy should be tested immediately after deployment:

```text
Open App
   ↓
Ask Roy
   ↓
Run a known grounded question
   ↓
Verify retrieved review / answer
```

If the deployed instance starts without the expected 84 vector documents, the RAG initialization strategy must be adjusted before the deployment is considered complete.

---

## Main User Flow

```text
Home
  ↓
Search Movie
  ↓
Movie Details
  ↓
Rating + Verdict + Review
  ↓
Recommendations
  ↓
Ask Roy
  ↓
Retrieval
  ↓
Grounded AI Answer
```

---

## Admin Flow

```text
Admin Login
    ↓
Admin Dashboard
    ↓
Add / Manage Review
    ↓
TMDB Enrichment
    ↓
Confirm Review
    ↓
Generate Embedding
    ↓
ChromaDB
    ↓
Available to Ask Roy
```

---

## Example: Jai Bhim

A verified Jai Bhim record contains:

```text
Rating: 4.5/5
Verdict: Must Watch
```

A user can ask:

```text
Why did Roy give this rating?
```

The system:

```text
Question
   ↓
Embedding
   ↓
ChromaDB Retrieval
   ↓
Jai Bhim Review
   ↓
Grounded Context
   ↓
Groq LLM
   ↓
Answer
```

The answer is generated from the retrieved review rather than from the LLM's general movie knowledge.

---

## Challenges & Engineering Solutions

| Challenge | Solution |
|---|---|
| Preventing hallucinated opinions | RAG + strict grounding prompt + fallback |
| Exact rating/verdict questions | MongoDB structured queries |
| Semantic review questions | Sentence Transformer + ChromaDB |
| Unapproved AI reviews | Explicit approval and ingestion status |
| External movie metadata | Dedicated TMDB service |
| Variable LLM output | Separate deterministic retrieval/evaluation logic |
| Recommendation quality | Hybrid scoring signals |
| User preference learning | Interaction-based profile |
| AI tool execution | Bounded agent loop |
| Production resilience | Defensive error handling and regression tests |

---

## Why RAG Instead of Fine-Tuning?

RoyReview's goal is to answer using a changing collection of personal reviews.

RAG is suitable because new confirmed reviews can be added and indexed without retraining the LLM.

```text
Confirmed Review
      ↓
Embedding
      ↓
Vector Store
      ↓
Retrieve When Relevant
      ↓
LLM
```

The model remains the language-generation layer while the review database remains the knowledge source.

---

## Why Hybrid Search?

Not every question is semantic.

For example:

```text
Which movies did Roy rate 5/5?
```

is naturally a structured database query.

While:

```text
Why does Roy like this movie?
```

is naturally a semantic retrieval problem.

Therefore:

```text
Structured Question → MongoDB
Semantic Question   → ChromaDB
Combined Question   → Hybrid Logic
```

This makes the retrieval architecture more appropriate for different query types.

---

## Current Project Metrics

| Metric | Status |
|---|---|
| Movie Records | 100+ |
| Confirmed Reviews | 80+ |
| RAG Documents | 84 |
| Authentication | Implemented |
| Admin Dashboard | Implemented |
| Movie Search | Implemented |
| Movie Details | Implemented |
| TMDB Integration | Implemented |
| Ask Roy | Implemented |
| Embeddings | Implemented |
| ChromaDB | Implemented |
| RAG | Implemented |
| Hybrid Search | Implemented |
| Content-Based Recommendations | Implemented |
| Hybrid Recommendation Scoring | Implemented |
| Movie Analytics | Implemented |
| Interaction Logging | Implemented |
| User Preference Profiles | Implemented |
| Personalization Signal | Implemented |
| Bounded Agentic RAG | Implemented |
| Automated Tests | 70 |
| Latest Automated Test Result | 70 Passed |
| Python Compilation | Passed |
| GitHub | Configured |
| Deployment Target | Streamlit Community Cloud |

---

## Current Engineering Status

### Completed

- Core movie-review application
- Authentication
- MongoDB integration
- TMDB integration
- Review approval workflow
- Embeddings
- ChromaDB vector search
- Ask Roy
- Hybrid search
- Content-based recommendations
- Hybrid recommendation scoring
- Movie analytics
- Interaction logging
- Preference profiles
- Personalization signal
- Bounded agentic RAG
- Automated testing
- Deployment preparation

### Ongoing Quality Work

The application is functionally implemented, but AI answer quality is still an area for improvement.

Future optimization should focus on:

- Stronger answer grounding
- Better unsupported-question handling
- More reliable title resolution
- Better ambiguity handling
- More deterministic agent routing
- Expanded RAG evaluation
- Recommendation ranking evaluation
- Production vector-store persistence

This distinction is important: **70 passing automated tests verify application behavior; they do not prove that every LLM-generated answer is perfect.**

---

## Future Scope

- Improve RAG answer faithfulness and correctness
- Expand the evaluation dataset
- Improve ambiguous and typo title handling
- Add more advanced recommendation ranking
- Add semantic user-preference modeling
- Add time-aware interaction weighting
- Add richer analytics
- Add recommendation evaluation dashboards
- Introduce persistent production-grade vector storage
- Add monitoring and observability
- Optimize cloud startup and model loading
- Improve production security and dependency management

---

## Internship / Academic Learning Outcomes

RoyReview demonstrates practical application of:

- AI and NLP fundamentals
- Text similarity
- Large Language Models
- Prompt engineering
- Embeddings
- Vector databases
- Semantic search
- Retrieval-Augmented Generation
- Hybrid search
- Grounding and hallucination control
- Tool-based agent workflows
- Recommendation systems
- Personalization
- External API integration
- MongoDB
- Authentication
- Automated testing
- Git/GitHub
- Cloud deployment preparation

---

## Project Presentation

A suitable college presentation structure is:

1. Project Title
2. Problem Statement
3. Objectives
4. Proposed Solution
5. Technology Stack
6. System Architecture
7. Application Features
8. Generative AI / Ask Roy
9. RAG Architecture
10. Hybrid Search & Recommendations
11. Personalization
12. Admin Workflow
13. Testing & Evaluation
14. Challenges & Solutions
15. Future Scope
16. Conclusion

---

## Suggested Project Evidence

For a college report or presentation, capture:

1. Home / landing page
2. Movie search
3. Movie details
4. Roy rating and verdict
5. Recommendation section
6. Ask Roy interface
7. Grounded Ask Roy response
8. Analytics dashboard
9. Profile / personalization
10. Admin dashboard
11. Add-review workflow
12. MongoDB Atlas data
13. RAG / ChromaDB verification
14. Terminal showing `70 passed`
15. GitHub repository
16. Final deployed application

---

## Author

**Arpon Roy**

B.Tech / CSE Student  
Generative AI & Software Development Project

---

## License

This project was developed as a college/internship project for educational and portfolio purposes.
