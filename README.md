
Pasted text(20260909-085624).txt
Document
there are no signup, signing. here the terminal output


after start I go this page and when I spinout then that page come.

Pasted text(20260909-090643).txt
Document
is this ok? give me full fixed code.


button front color should be white and after hover bluse. how to fixed this?
now can I give inpu and it works?
in last the front color shod just white. 



new input movies review rag is not working. poster are not come automatically. 


terminal I think ok but in ui?

Pasted text(20260909-100018).txt
Document
import streamlit as st

from database.mongodb import movies_collection


def get_count(query=None):

    if query is None:
        query = {}

    return movies_collection.count_documents(
        query
    )


def render_explore():

    st.markdown(
        """
        <div class="rr-explore-panel">

            <div class="rr-explore-title">
                Explore
            </div>

            <div class="rr-explore-subtitle">
                Browse Roy's collection
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    must_watch = get_count(
        {"verdict": "Must Watch"}
    )

    good_watch = get_count(
        {"verdict": "Good Watch"}
    )

    dont_watch = get_count(
        {"verdict": "Don't Watch"}
    )

    five_star = get_count(
        {"roy_rating": 5.0}
    )

    if st.button(
        f"››› Must Watch  ·  {must_watch}",
        use_container_width=True,
    ):

        st.session_state.explore_filter = (
            "Must Watch"
        )

        st.session_state.page = "explore_results"

        st.rerun()

    if st.button(
        f"››› Good Watch  ·  {good_watch}",
        use_container_width=True,
    ):

        st.session_state.explore_filter = (
            "Good Watch"
        )

        st.session_state.page = "explore_results"

        st.rerun()

    if st.button(
        f"››› Don't Watch  ·  {dont_watch}",
        use_container_width=True,
    ):

        st.session_state.explore_filter = (
            "Don't Watch"
        )

        st.session_state.page = "explore_results"

        st.rerun()

    if st.button(
        f"››› ★★★★★  ·  {five_star}",
        use_container_width=True,
    ):

        st.session_state.explore_filter = (
            "5 Star"
        )

        st.session_state.page = "explore_results"

        st.rerun()


def render_explore_results():

    filter_name = st.session_state.get(
        "explore_filter",
        "Must Watch",
    )

    if filter_name == "5 Star":

        query = {
            "roy_rating": 5.0
        }

    else:

        query = {
            "verdict": filter_name
        }

    movies = list(
        movies_collection.find(
            query,
            {"_id": 0},
        )
        .sort("roy_rating", -1)
    )

    st.markdown(
        f"""
        <div class="rr-result-header">

            <div class="rr-kicker">
                EXPLORE
            </div>

            <h1>
                {filter_name}
            </h1>

            <p>
                {len(movies)} movies in this collection.
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "← Explore",
        key="back_explore",
    ):

        st.session_state.page = "explore"
        st.rerun()

    columns = st.columns(4)

    for index, movie in enumerate(movies):

        with columns[index % 4]:

            poster = movie.get(
                "poster_url"
            )

            title = movie.get(
                "title",
                "Movie",
            )

            rating = movie.get(
                "roy_rating",
                0,
            )

            if poster:

                st.image(
                    poster,
                    use_container_width=True,
                )

            else:

                st.markdown(
                    """
                    <div class="rr-small-poster">
                        🎬
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                f"""
                <div class="rr-grid-title">
                    {title}
                </div>

                <div class="rr-grid-rating">
                    ★ {rating}/5
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button(
                "Open",
                key=f"explore_{movie.get('movie_id')}",
                use_container_width=True,
            ):

                st.session_state.selected_movie_id = (
                    movie.get("movie_id")
                )

                st.session_state.page = "movie"

                st.rerun()
fixed that yeollow
Perfect — your staged files look correct. The ignored venv/, chroma_db/, __pycache__/, and .streamlit/secrets.toml are not appearing, so don't unstage anything.
Now connect this local repository to:

https://github.com/ArponRoy007/RoyReview.git

1. Add the GitHub remote
Run:
git remote add origin https://github.com/ArponRoy007/RoyReview.git
Verify:
git remote -v
You should see:
origin  https://github.com/ArponRoy007/RoyReview.git (fetch)
origin  https://github.com/ArponRoy007/RoyReview.git (push)
2. Commit your project
git commit -m "Initial RoyReview release"
Then check:
git status
You should get something like:
On branch main
nothing to commit, working tree clean
3. Push to GitHub
Because your GitHub repository is presumably empty:
git push -u origin main
If GitHub asks you to authenticate, complete the GitHub authentication in your browser/credential prompt.
4. Verify
Open your repository:
RoyReview on GitHub

You should see your project structure:

RoyReview
├── ai/
├── auth/
├── config/
├── database/
├── movies/
├── rag/
├── scripts/
├── tests/
├── ui/
├── utils/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
And importantly, you should NOT see:
.streamlit/secrets.toml
venv/
chroma_db/
__pycache__/
One final safety check before pushing
Since you have already staged the files, run:
git diff --cached --stat
Then:
git status
Your current staged list looks clean based on what you showed. You can proceed with the remote → commit → push commands above.
venv) arponroy007@Arpons-MacBook-Air RoyReview % git diff --cached --stat
(venv) arponroy007@Arpons-MacBook-Air RoyReview % git status
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
Perfect. ✅ GitHub is connected and your working tree is clean.
This line is especially important:

Your branch is up to date with 'origin/main'.
And:
nothing to commit, working tree clean
means your local project and GitHub main are currently synchronized.
One thing to notice
You ran:
git diff --cached --stat
and got no output because the changes have already been committed and pushed. That's why there is nothing staged anymore. ✅
So your status is effectively:

RoyReview
├── Tests                 ✅ 18 passed
├── Python compilation   ✅
├── MongoDB              ✅
├── TMDB                 ✅
├── Embeddings           ✅
├── ChromaDB             ✅ 84 docs
├── RAG                  ✅
├── Groq                 ✅
├── Ask Roy UI           ✅
├── Poster UI            ✅
├── Git                  ✅
└── GitHub               ✅
You can verify the repository here:
ArponRoy007/RoyReview on GitHub

🚀 Next step: Deploy RoyReview
Now I recommend not changing the code unnecessarily.
The next stage is:

GitHub → Streamlit Community Cloud → MongoDB Atlas + TMDB + Groq → Live RoyReview

Before deployment, we need to make sure requirements.txt contains everything required by the deployed app and then configure Streamlit Cloud Secrets.

If you want, we can do the deployment step-by-step without breaking your current GitHub version.
now write profetional readme file with can I use to make ppt when I need to submit project. make in detail, shith things I learn from internship, I project which things I apply and the full feature of the royreview. write in detail profetional readm.md fimle
Analysis paused

Analysis paused
Done. I created a professional, detailed README.md for RoyReview that you can use for both:
GitHub project documentation
Internship/project submission
PPT preparation
Project viva/presentation
Explaining what you learned during the internship
Explaining exactly which Generative AI concepts you implemented
It covers the complete project: problem statement, objectives, internship learning outcomes, features, architecture, RAG pipeline, embeddings, ChromaDB, Groq, TMDB, MongoDB, hybrid search, authentication, admin workflow, security, testing, challenges, solutions, metrics, future scope, and a 16-slide PPT structure.
📄 Download the professional README
Download RoyReview_Professional_README.md
You can replace your current GitHub README.md with this file.

One important point: I kept the README presentation-friendly, so later you can directly take sections like Problem → Objectives → Tech Stack → Architecture → RAG → Features → Challenges → Learning → Results → Future Scope and turn them into PPT slides.

RoyReview_Professional_README.md
Document







Library
/
RoyReview_Professional_README.md


RoyReview --- AI-Powered Personal Movie Review Platform
Internship Project | Generative AI with LLMs | Python | Streamlit
| MongoDB Atlas | RAG | ChromaDB | Groq | TMDB
RoyReview is an AI-powered personal movie review platform that combines
a real-world movie application with modern Generative AI techniques.
Users can explore movies, view Roy's verified ratings and reviews,
search films, and interact with Ask Roy, an AI assistant grounded in
RoyReview's movie-review knowledge base.
This project was developed as a practical application of concepts
learned during a Generative AI with LLMs internship, including
AI/NLP foundations, LLMs, prompt engineering, APIs, embeddings, vector
databases, document processing, semantic search, Retrieval-Augmented
Generation (RAG), hybrid search, evaluation, testing, and deployment.

1. Project Overview
Problem Statement
Movie information is widely available online, but a personal review
platform has a different requirement: the system must preserve the
reviewer's own opinions, ratings, verdicts, and writing style.
Traditional keyword search can find a movie, but it cannot reliably
answer questions such as:

Why did Roy give this movie a high rating?
What does Roy say about this movie?
Which movies does Roy consider Must Watch?
Which movies did Roy rate 5/5?
What is Roy's opinion of a particular film?
RoyReview solves this by combining structured database search with
semantic retrieval and a Large Language Model.
Core Concept
Movie Reviews
     ↓
MongoDB Atlas
     ↓
Confirmed Reviews
     ↓
Document Preparation
     ↓
Sentence Transformer Embeddings
     ↓
ChromaDB
     ↓
Semantic Retrieval
     ↓
Relevant Context
     ↓
Prompt Engineering
     ↓
Groq LLM
     ↓
Ask Roy Answer
2. Project Objectives
Build a complete working movie-review web application.
Store movie and review information using MongoDB Atlas.
Integrate TMDB for movie metadata and posters.
Maintain a verified personal movie-review knowledge base.
Convert confirmed reviews into semantic embeddings.
Store embeddings in a vector database.
Implement Retrieval-Augmented Generation.
Build a grounded AI assistant called Ask Roy.
Prevent the AI from inventing Roy's opinions.
Add authentication and administrative review management.
Support exact structured search as well as semantic search.
Test the application using pytest.
Prepare the application for cloud deployment.
Demonstrate practical implementation of Generative AI concepts
learned during the internship.
3. What I Learned During the Internship
3.1 AI and NLP Foundations
I learned how Natural Language Processing allows applications to work
with human language.
Key concepts:

Text representation
Semantic meaning
Text similarity
Natural-language queries
Information retrieval
Vector representations
NLP-based search
Application in RoyReview
Movie reviews are natural-language documents. RoyReview converts them
into semantic vector representations so that user questions can be
matched to relevant reviews based on meaning rather than only exact
keywords.
3.2 Large Language Models
I learned the fundamentals of Large Language Models and how LLM APIs can
be integrated into applications.
Important concepts:

System prompts
User prompts
Context
Temperature
Token limits
API-based inference
Grounded generation
Application
RoyReview uses a Groq-hosted LLM for the final natural-language response
generated by Ask Roy.
The model does not independently determine Roy's opinion. Relevant
review information is retrieved first and supplied as context.

3.3 Prompt Engineering
I learned how prompt design can control the behavior of an LLM.
The Ask Roy system prompt defines:

The role of the assistant
The allowed information
The source of truth
Unsupported-answer behavior
Response style
Hallucination restrictions
Important rules include:
Never invent Roy's opinion.
Never create an unsupported rating.
Never claim Roy reviewed a movie unless it appears in the knowledge
base.
Keep Roy's opinion separate from general movie facts.
Use retrieved context as the source of truth.
Say "I couldn't find that in Roy's movie notes." when the
context does not support an answer.
This demonstrates practical prompt engineering and grounded generation.
3.4 Embeddings
I learned that text can be converted into numerical vectors called
embeddings.
Embeddings make it possible to compare text according to semantic
meaning.

RoyReview uses:

Sentence Transformers
Model: all-MiniLM-L6-v2
A complete confirmed review is converted into an embedding.
For example:

Movie: Jai Bhim
Year: 2021
Genre: Crime/Thriller
Roy's Rating: 4.5/5
Verdict: Must Watch
Roy's Review: ...
The user's question is also converted into an embedding, after which the
system searches for semantically relevant review documents.
3.5 Vector Databases
I learned why vector databases are important for modern AI applications.
They provide capabilities for:

Storing embeddings
Similarity search
Semantic retrieval
Metadata filtering
RAG applications
RoyReview uses ChromaDB as its persistent vector database.
Collection:

royreview_reviews
The current implementation contains 84 embedded confirmed review
documents.
3.6 Retrieval-Augmented Generation
RAG was one of the most important concepts applied in this project.
RAG combines:

Retrieval + Generation
Instead of asking an LLM to answer only from its general knowledge,
RoyReview first retrieves relevant information from Roy's private review
knowledge base.
RAG Pipeline
User Question
      ↓
Question Embedding
      ↓
ChromaDB Similarity Search
      ↓
Top Relevant Reviews
      ↓
Context Construction
      ↓
System Prompt + User Prompt
      ↓
Groq LLM
      ↓
Grounded Answer
3.7 Hybrid Search
I learned that vector search is not ideal for every question.
For example:

Which movies did Roy rate 5/5?
is primarily a structured database query.
RoyReview therefore uses two query paths.

Exact Queries
MongoDB handles:
Rating filters
Verdict filters
Minimum ratings
Structured movie lists
Semantic Queries
ChromaDB handles:
Why questions
Opinion-related questions
Natural-language review questions
Semantic similarity
Hybrid Architecture
                    User Question
                          ↓
                    Query Router
                    ↙          ↘
             Exact Query     Semantic Query
                  ↓                ↓
              MongoDB          Embedding
                  ↓                ↓
             Exact Data        ChromaDB
                    ↘          ↙
                    Final Answer
3.8 Document Processing
I learned that information should be transformed into consistent
retrieval units before being indexed.
RoyReview creates a structured review document containing:

Movie title
Year
Zone
Genre
Roy's rating
Verdict
Roy's review
This makes retrieval more consistent and gives the LLM useful metadata
alongside the review text.
3.9 Fine-Tuning vs Prompting and RAG
I learned the difference between fine-tuning and runtime knowledge
injection.
Fine-Tuning
Adapts a model using additional training data.
Prompting + RAG
Provides instructions and relevant knowledge at runtime.
RoyReview uses RAG because Roy's movie-review knowledge base is
relatively small and can change as new reviews are added.

This allows new reviews to be added and indexed without retraining an
LLM.

3.10 LLM Evaluation
I learned that a fluent AI response is not automatically a correct
response.
AI applications need evaluation for:

Retrieval quality
Context relevance
Grounding
Correctness
Hallucination
Application reliability
RoyReview separates deterministic application logic from the LLM layer
and tests the important components independently.
3.11 AI Application Development
I learned how to move from an AI concept or chatbot demo to a complete
software product.
RoyReview combines:

UI
+
Authentication
+
Database
+
External API
+
Embeddings
+
Vector Database
+
RAG
+
LLM
+
Testing
+
Deployment Preparation
3.12 Testing and Engineering
I learned the importance of automated testing before deployment.
RoyReview uses:

pytest
Final automated test result:
18 passed, 1 warning
The warning was a ChromaDB/Python deprecation warning and did not cause
test failure.
Python compilation was also checked using:

python -m compileall -q .
3.13 Deployment and Secret Management
I learned how to prepare an AI application for deployment.
Important practices:

requirements management
Git/GitHub
environment configuration
secret management
API integration
cloud deployment preparation
API keys and database credentials are kept outside the Git repository
using Streamlit secrets.
4. Full RoyReview Feature Set
4.1 User Authentication
RoyReview provides:
Signup
Login
Session-based authentication
Logout
Admin authentication
Protected application pages
Normal users and administrative functionality are separated.
4.2 Movie Dashboard
The main interface provides:
Movie posters
Film names
Release years
Zones
Genres
Roy's ratings
Verdicts
Personal reviews
Search functionality
4.3 Movie Search
Users can search movies by title.
Movie records are retrieved from MongoDB and can be enriched with TMDB
metadata when required.

4.4 Movie Details
The detail page provides:
Large movie poster
Movie title
Year
Zone
Genre
Roy's rating
Verdict
IMDb information when available
Roy's personal review
Ask Roy interface
4.5 Roy's Rating System
RoyReview uses a 5-point personal rating scale.
Examples:

5/5
4.5/5
4/5
3.5/5
...
Roy's rating is kept separate from external movie ratings.
4.6 Verdict System
Three personal verdict categories are used:
Must Watch
A strong recommendation.
Good Watch
A positive recommendation.
Don't Watch
A movie Roy does not recommend according to his review.
4.7 Personal Reviews
Each confirmed movie contains a concise personal review.
Reviews focus on areas such as:

Story
Screenplay
Acting
Songs
Emotional impact
Entertainment value
Rewatchability
Overall filmmaking
4.8 TMDB Integration
RoyReview integrates with TMDB to retrieve:
TMDB ID
Movie title
Original title
Overview
Release date
Runtime
Genres
TMDB rating
Vote count
Poster
Backdrop
IMDb ID when available
Important Design Decision
TMDB's rating and Roy's rating are stored separately.
The external rating is never presented as Roy's personal rating.

5. Ask Roy --- Generative AI Assistant
5.1 Purpose
Ask Roy is the main Generative AI feature of the platform.
Users can ask natural-language questions about Roy's movie-review
knowledge base.

Examples:

Why did Roy give this rating?

What does Roy say about this movie?

Which movies does Roy consider Must Watch?

Which movies did Roy rate 5/5?

Tell me about Roy's opinion of Jai Bhim.
5.2 Quick Questions
The interface provides predefined questions so users can interact with
Ask Roy easily.
Users can also enter custom questions.

5.3 Grounded Answers
Ask Roy is designed to avoid hallucinating personal opinions.
The AI uses retrieved reviews as its source of truth.

When information is unavailable, it should respond:

I couldn't find that in Roy's movie notes.
This makes the system more reliable than a general-purpose chatbot for
this specific knowledge base.
5.4 Movie-Specific RAG
When Ask Roy is opened from a movie detail page, retrieval can be
restricted to the selected movie.
Example:

Selected Movie: Jai Bhim
Question: Why did Roy give this rating?
              ↓
Retrieve Jai Bhim Review
              ↓
Build Context
              ↓
Groq LLM
              ↓
Grounded Answer
6. Admin Dashboard
The Admin Dashboard allows management of the movie-review knowledge
base.
It provides:

Total movie count
Confirmed review count
Add New Review workflow
Review management
RAG ingestion workflow
6.1 Add New Review
The administrator can add:
Movie title
Year
Zone
Genre
Roy's rating
Verdict
Review text
TMDB can then be used for movie metadata enrichment.
6.2 Review Approval Workflow
RoyReview separates confirmed opinions from AI-generated candidates.
Candidate reviews can have:

review_status = NEEDS_USER_APPROVAL
ingest_to_rag = NO
Only confirmed reviews are allowed into the RAG knowledge base.
This prevents unapproved AI-generated text from becoming part of Roy's
personal opinion database.

6.3 RAG Rebuilding
The project includes a rebuilding workflow:
MongoDB Confirmed Reviews
        ↓
Review Document Preparation
        ↓
Embedding Generation
        ↓
ChromaDB Upsert
        ↓
RAG Knowledge Base Updated
7. System Architecture
                         ┌──────────────────┐
                         │       User       │
                         └────────┬─────────┘
                                  ↓
                         ┌──────────────────┐
                         │   Streamlit UI   │
                         └────────┬─────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             ↓                    ↓                    ↓
      Authentication        Movie Search          Ask Roy
             ↓                    ↓                    ↓
        Auth Logic          MongoDB Atlas         QA Router
                                  │                ↙      ↘
                                  ↓               ↓        ↓
                                 TMDB          MongoDB   ChromaDB
                              Metadata         Exact     Semantic
                                                  Search  Search
                                                        ↓
                                               Retrieved Context
                                                        ↓
                                                 Prompt Builder
                                                        ↓
                                                   Groq LLM
                                                        ↓
                                                 AI Response
8. RAG Architecture
             CONFIRMED MOVIE REVIEWS
                       ↓
              Review Document
                  Preparation
                       ↓
              Sentence Transformer
               all-MiniLM-L6-v2
                       ↓
                  Embeddings
                       ↓
                   ChromaDB
                       ↑
                       │
                Similarity Search
                       ↑
                       │
                 User Question
                       ↓
              Question Embedding
                       ↓
               Top-K Retrieval
                       ↓
               Context Builder
                       ↓
           System Prompt + Context
                       ↓
                    Groq LLM
                       ↓
                Grounded Answer
9. Database Design
MongoDB Atlas
Database:
royreview
Collection:
movies
Important fields include:
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
MongoDB acts as the primary source for application movie data.
10. Vector Database Design
ChromaDB collection:
royreview_reviews
Each record contains:
ID
Review Document
Embedding
Metadata
Metadata includes:
movie_id
title
year
zone
genre
roy_rating
verdict
11. External API Integration
TMDB
Used for movie metadata, posters, backdrops, and IMDb IDs when
available.
Groq
Used to access the LLM for Ask Roy.
12. Technology Stack
Layer Technology
Language Python
UI Streamlit
Database MongoDB Atlas
Movie Metadata TMDB API
LLM Provider Groq
LLM Model openai/gpt-oss-120b
Embedding Model all-MiniLM-L6-v2
Embedding Library Sentence Transformers
Vector Database ChromaDB
Testing pytest
Version Control Git / GitHub
Deployment Target Streamlit Community Cloud
13. Project Structure
RoyReview/
├── app.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── database/
│   ├── __init__.py
│   ├── mongodb.py
│   └── models.py
├── auth/
│   ├── __init__.py
│   ├── login.py
│   ├── signup.py
│   └── security.py
├── movies/
│   ├── __init__.py
│   ├── movie_service.py
│   ├── tmdb.py
│   └── imdb.py
├── rag/
│   ├── __init__.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── retriever.py
│   ├── prompts.py
│   ├── qa.py
│   ├── ingest.py
│   └── hybrid.py
├── ai/
│   ├── __init__.py
│   ├── llm.py
│   ├── recommender.py
│   └── agent.py
├── ui/
│   ├── __init__.py
│   ├── home.py
│   ├── dashboard.py
│   ├── movie_details.py
│   ├── ask_roy.py
│   └── explore.py
├── data/
├── scripts/
│   ├── import_movies.py
│   ├── build_embeddings.py
│   └── rebuild_embeddings.py
├── tests/
│   ├── test_auth.py
│   ├── test_movies.py
│   ├── test_database.py
│   └── test_rag.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
├── .streamlit/
│   └── secrets.toml
├── requirements.txt
├── .gitignore
└── README.md
14. Security and Secret Management
Sensitive credentials are not stored directly in the source code.
Local secrets are stored in:

.streamlit/secrets.toml
and excluded from Git using .gitignore.
Production deployment should use Streamlit's secret-management system.

Architecture:

Source Code → GitHub
Secrets     → Secure Secret Configuration
15. Testing
RoyReview uses pytest for automated testing.
Final result:

18 passed, 1 warning
Testing covers important application areas such as:
Authentication
Movie functionality
Database behavior
RAG components
Python compilation was also verified:
python -m compileall -q .
No compilation errors were reported.
16. Integration Verification
TMDB Verification
A TMDB enrichment test successfully returned:
TMDB ID
Poster URL
Movie title
Overview
TMDB rating
IMDb ID
ChromaDB Verification
The vector database was populated successfully.
Current verified count:

84 documents
Retriever Verification
A movie-specific retrieval test successfully retrieved the Jai Bhim
review containing:
Roy's Rating: 4.5/5
Verdict: Must Watch
LLM Verification
A test question:
Why did Roy give this rating?
successfully generated a grounded response using the retrieved Jai Bhim
review.
17. Challenges and Solutions
Challenge 1 --- Preventing Hallucination
Problem
An LLM can generate plausible information that is not part of Roy's
actual reviews.
Solution
Use RAG and a strict grounding prompt. The retrieved review context is
treated as the source of truth.
Challenge 2 --- Exact vs Semantic Questions
Problem
Vector similarity is not the best method for exact rating or verdict
filtering.
Solution
Use MongoDB for structured queries and ChromaDB for semantic retrieval.
Challenge 3 --- Unapproved AI Reviews
Problem
AI-generated draft reviews should not automatically become Roy's
opinions.
Solution
Use explicit review status and RAG ingestion status.
Only confirmed reviews are indexed.

Challenge 4 --- External Movie Metadata
Problem
Movie records require reliable posters and metadata.
Solution
A dedicated TMDB service was created for searching and enriching movie
records.
Challenge 5 --- ML Dependency Compatibility
Problem
The embedding stack required compatible Python machine-learning
dependencies.
Solution
The required ML dependencies were configured and tested until the
embedding and RAG workflow executed successfully.
Challenge 6 --- Testing AI Systems
Problem
LLM output can be variable and is harder to test like normal
deterministic functions.
Solution
Separate deterministic retrieval/database logic from generation and test
the application components independently.
18. Key Technical Decisions
Why MongoDB?
MongoDB is suitable for the application's structured but flexible
movie-review documents and provides a cloud-hosted Atlas database.
Why ChromaDB?
ChromaDB provides persistent vector storage and similarity search
suitable for a student-scale RAG application.
Why Sentence Transformers?
Sentence Transformers provides efficient semantic text embeddings for
review retrieval.
Why RAG?
The objective is not to train an LLM to become Roy.
Instead:

Roy's Verified Reviews
        ↓
Stored in Database
        ↓
Retrieved when relevant
        ↓
Provided to LLM as Context
        ↓
LLM Explains the Context
Why Groq?
Groq provides API access to LLMs suitable for interactive AI
applications.
Why Streamlit?
Streamlit makes it possible to build an interactive Python AI
application quickly while keeping the project architecture manageable.
19. Most Important AI Design Principle
RoyReview treats personal opinion as controlled data.
The system does not allow the AI to freely create an opinion on behalf
of Roy.

Correct flow:

Confirmed Roy Review
        ↓
Embedding
        ↓
RAG Knowledge Base
        ↓
Retrieved Evidence
        ↓
LLM Explanation
Incorrect flow:
LLM Generates Opinion
        ↓
Pretends It Belongs to Roy
This separation is an important reliability feature.
20. Internship Concepts Applied to the Project
What I Learned How I Applied It
AI / NLP Natural-language movie questions
Text Similarity Semantic review retrieval
LLMs Groq LLM
Prompt Engineering Ask Roy system prompt
Embeddings Sentence Transformers
Vector Databases ChromaDB
RAG Retrieved reviews + LLM
Document Processing Structured review documents
Semantic Search Vector similarity
Hybrid Search MongoDB + ChromaDB
LLM API Integration Groq
Grounding Retrieved context as source of truth
Hallucination Control Strict prompt + fallback
Evaluation Retrieval and application tests
Database MongoDB Atlas
External APIs TMDB
Authentication Signup / Login / Admin
Testing pytest
Version Control Git / GitHub
Deployment Streamlit Community Cloud preparation
21. Project Data
The application contains 100+ movie records.
The dataset includes:

Confirmed reviews
AI-draft candidate reviews
Movie metadata
Posters
Review status
RAG ingestion status
Only confirmed reviews are treated as Roy's actual opinions.
This separation protects the integrity of the personal knowledge base.

22. UI / UX Design
RoyReview uses a modern, clean and premium movie-focused interface.
Primary visual palette:

Background : #F4F4F4
Dark       : #393A3A
Secondary  : #575959
Soft Blue  : #B8D5E5
Primary    : #F89344
Accent     : #FF642F
Text       : #17181C
White      : #FFFFFF
The interface focuses on:
Clean layouts
Strong movie imagery
Clear ratings
Simple navigation
Premium typography
Responsive interaction
Integrated AI experience
23. Main User Flow
Home
 ↓
Search Movie
 ↓
Movie Result
 ↓
Movie Details
 ↓
Rating + Verdict + Review
 ↓
Ask Roy
 ↓
RAG Retrieval
 ↓
AI Answer
24. Admin Flow
Admin Login
     ↓
Admin Dashboard
     ↓
Add New Review
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
25. End-to-End Example: Jai Bhim
For the movie Jai Bhim, RoyReview stores:
Rating: 4.5/5
Verdict: Must Watch
and a verified personal review describing the film as a standout
achievement in Tamil cinema and praising its filmmaking.
A user asks:

Why did Roy give this rating?
Step 1 --- Question
Ask Roy receives the question.
Step 2 --- Embedding
The question is converted into a vector using:
all-MiniLM-L6-v2
Step 3 --- Retrieval
ChromaDB finds the relevant Jai Bhim review.
Step 4 --- Context
The retrieved document contains:
Movie: Jai Bhim
Rating: 4.5/5
Verdict: Must Watch
Roy's Review: ...
Step 5 --- Prompt
The review is inserted into the controlled Ask Roy prompt.
Step 6 --- Generation
The Groq LLM generates an explanation using the supplied context.
Step 7 --- Result
The user receives a natural-language explanation grounded in Roy's
verified review.
Complete pipeline:

Question
   ↓
Embedding
   ↓
Retrieval
   ↓
Context
   ↓
Prompt
   ↓
LLM
   ↓
Answer
26. Why RoyReview Is More Than a Chatbot
RoyReview is a complete application rather than only an LLM demo.
Product Layer
Authentication
Movie Search
Movie Details
Movie Reviews
Ratings
Verdicts
Admin Dashboard
TMDB Integration
AI Layer
Embeddings
Vector Database
Semantic Retrieval
RAG
Prompt Engineering
LLM
Grounded QA
Engineering Layer
Modular Architecture
Testing
Git/GitHub
Secret Management
Deployment Preparation
This demonstrates both software-engineering and Generative-AI skills.
27. Current Project Metrics
Metric Status
Movie Records 100+
Confirmed Reviews 80+
RAG Documents 84
Authentication Implemented
Admin Dashboard Implemented
Movie Search Implemented
Movie Details Implemented
TMDB Integration Implemented
Ask Roy Implemented
Embeddings Implemented
ChromaDB Implemented
RAG Implemented
Hybrid Search Implemented
Automated Tests 18
Test Result 18 Passed
GitHub Configured
Deployment Preparation Completed
28. Future Scope
28.1 AI Movie Recommendation
Build a recommendation engine using:
Roy's ratings
Genres
Semantic similarity
Movie metadata
User preferences
28.2 Advanced Recommendation
Combine:
Content Similarity
+
Embedding Similarity
+
Roy's Ratings
+
Genre Preference
to generate more personalized recommendations.
28.3 AI Agent
A future Ask Roy agent could:
Understand User Intent
        ↓
Select Tool
        ↓
Search Movies
        ↓
Retrieve Reviews
        ↓
Apply Filters
        ↓
Generate Answer
28.4 Advanced RAG Evaluation
Future versions can measure:
Retrieval precision
Retrieval recall
Context relevance
Answer faithfulness
Answer correctness
Hallucination rate
28.5 Movie Analytics
Possible dashboards:
Rating distribution
Verdict distribution
Genre preferences
Zone-wise ratings
Year-wise trends
Highest-rated movies
Review themes
28.6 Personalized User Recommendations
A future version can use user behavior such as:
Watch history
Ratings
Favorite genres
Favorite actors
Favorite directors
Semantic preferences
to provide personalized recommendations.
29. Deployment Architecture
RoyReview is prepared for deployment using Streamlit Community Cloud.
GitHub
   ↓
Streamlit Community Cloud
   ↓
RoyReview Application
   ↓
MongoDB Atlas
   ↓
TMDB API
   ↓
Groq API
   ↓
RAG / ChromaDB
Secrets should be configured through the deployment platform rather than
committed to GitHub.
30. Recommended PPT Structure
This README can directly serve as the technical source for an
internship/project presentation.
Slide 1 --- Title
RoyReview
AI-Powered Personal Movie Review Platform
Slide 2 --- Problem Statement
Explain why normal movie search cannot answer questions about a personal
reviewer's opinions.
Slide 3 --- Objectives
Present the project's major goals.
Slide 4 --- Proposed Solution
Show the complete system architecture.
Slide 5 --- Technology Stack
Python
Streamlit
MongoDB Atlas
TMDB
Sentence Transformers
ChromaDB
Groq
pytest
GitHub
Slide 6 --- Application Features
Authentication
Movie Search
Movie Details
Ratings
Verdicts
Reviews
Admin Dashboard
Slide 7 --- Generative AI Features
Ask Roy
Embeddings
Semantic Search
RAG
Prompt Engineering
Grounded Answers
Slide 8 --- RAG Architecture
Question
 ↓
Embedding
 ↓
ChromaDB
 ↓
Relevant Review
 ↓
Prompt
 ↓
Groq LLM
 ↓
Answer
Slide 9 --- Hybrid Search
Explain MongoDB exact filtering versus ChromaDB semantic retrieval.
Slide 10 --- Grounding and Reliability
Confirmed Reviews
       ↓
RAG
       ↓
Evidence-Based Answer
Slide 11 --- Admin Workflow
Add Review
 ↓
Confirm
 ↓
Embed
 ↓
ChromaDB
Slide 12 --- Testing
18 Tests
18 Passed
Slide 13 --- Internship Learning
Show the concepts learned and their practical implementation.
Slide 14 --- Challenges and Solutions
Present the major development challenges and solutions.
Slide 15 --- Future Scope
AI Recommendations
AI Agent
Advanced RAG
Evaluation
Analytics
Slide 16 --- Conclusion
Explain how RoyReview demonstrates the practical application of
Generative AI in a real software product.
31. Suggested Evidence for Project Submission
Recommended screenshots for a final report or PPT:
RoyReview landing page
Movie search result
Movie details page
Rating and verdict
Ask Roy interface
Ask Roy response
Admin Dashboard
Add Review form
MongoDB Atlas data
ChromaDB/RAG verification
Terminal showing 18 passed
GitHub repository
Deployed application
These screenshots demonstrate the implementation of both the product and
the AI pipeline.
32. Internship Learning Outcome
Through RoyReview, I progressed from understanding Generative AI
concepts theoretically to applying them in an end-to-end application.
The major practical outcomes were:

Understanding how LLM applications are structured.
Designing effective prompts.
Converting text into embeddings.
Performing semantic retrieval.
Using a vector database.
Implementing RAG.
Combining structured and vector search.
Integrating external APIs.
Grounding LLM responses.
Controlling hallucination.
Testing AI application components.
Managing secrets securely.
Structuring a modular Python application.
Using Git and GitHub.
Preparing an application for cloud deployment.
33. Conclusion
RoyReview demonstrates how Generative AI concepts can be transformed
from internship learning topics into a practical software product.
The project combines:

Natural Language Processing
Embeddings
Vector Search
Retrieval-Augmented Generation
Prompt Engineering
Large Language Models
External API Integration
MongoDB
Authentication
Automated Testing
Git/GitHub
Cloud Deployment Preparation
The central design principle is:
The LLM generates the explanation, but Roy's verified reviews remain
the source of truth.
This makes RoyReview more than a movie-review website and more than a
simple chatbot. It is an end-to-end demonstration of how Generative AI
can be integrated into a real application with data management,
retrieval, grounding, testing, and a user-facing product experience.
Project Status
Core Internship Implementation: Completed
The core application, authentication, movie database, TMDB integration,
RAG pipeline, embeddings, ChromaDB vector search, Ask Roy assistant,
hybrid search, admin workflow, automated testing, and GitHub setup are
implemented.

Future versions can extend the platform with advanced recommendation
systems, AI agents, deeper RAG evaluation, analytics, and personalized
user experiences.

Author
Arpon Roy
B.Tech / CSE Student
Generative AI & Software Development Project
