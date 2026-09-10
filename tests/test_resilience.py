import pytest


class FailingCollection:
    def find_one(self, *_args, **_kwargs):
        raise RuntimeError("MongoDB is unavailable")

    def find(self, *_args, **_kwargs):
        raise RuntimeError("MongoDB is unavailable")


def test_login_degrades_gracefully_when_mongo_is_unavailable(monkeypatch):
    import auth.login

    monkeypatch.setattr(auth.login, "users_collection", FailingCollection())
    assert auth.login.authenticate_user("member", "password") is None


def test_signup_degrades_gracefully_when_mongo_is_unavailable(monkeypatch):
    import auth.signup

    monkeypatch.setattr(auth.signup, "users_collection", FailingCollection())
    success, message = auth.signup.create_user("Member", "member", "member@example.com", "password123")
    assert not success
    assert "temporarily unavailable" in message


def test_exact_movie_lookup_returns_empty_result_when_mongo_fails(monkeypatch):
    import rag.hybrid

    monkeypatch.setattr(rag.hybrid, "movies_collection", FailingCollection())
    assert rag.hybrid.get_exact_movies(verdict="Must Watch") == []


def test_answer_question_returns_grounded_fallback_when_retrieval_fails(monkeypatch):
    import rag.qa

    def fail_context(**_kwargs):
        raise RuntimeError("ChromaDB is unavailable")

    monkeypatch.setattr(rag.qa, "build_context", fail_context)
    result = rag.qa.answer_question("Why did Roy like Darr?", movie_title="Darr")
    assert result == {"answer": "I couldn't find that in Roy's movie notes.", "sources": []}


def test_answer_question_returns_grounded_fallback_when_groq_fails(monkeypatch):
    import ai.llm
    import rag.qa

    monkeypatch.setattr(rag.qa, "build_context", lambda **_kwargs: ("Darr review", [{"metadata": {"title": "Darr"}}]))

    def fail_answer(**_kwargs):
        raise RuntimeError("Groq is unavailable")

    monkeypatch.setattr(ai.llm, "generate_answer", fail_answer)
    result = rag.qa.answer_question("Why did Roy like Darr?", movie_title="Darr")
    assert result == {"answer": "I couldn't find that in Roy's movie notes.", "sources": []}


def test_ingestion_returns_false_when_embedding_provider_fails(monkeypatch):
    import rag.ingest

    monkeypatch.setattr(rag.ingest, "embed_text", lambda _text: (_ for _ in ()).throw(RuntimeError("Model unavailable")))
    movie = {"movie_id": "darr", "title": "Darr", "review_status": "CONFIRMED", "review_text": "A memorable thriller."}
    assert rag.ingest.ingest_movie_review(movie) is False


def test_enrich_movie_returns_empty_metadata_when_tmdb_fails(monkeypatch):
    import movies.tmdb

    monkeypatch.setattr(movies.tmdb, "build_movie_metadata", lambda **_kwargs: (_ for _ in ()).throw(movies.tmdb.TMDBError("Unavailable")))
    metadata = movies.tmdb.enrich_movie("Darr", 1993)
    assert metadata["poster_url"] == ""
    assert metadata["tmdb_id"] is None


def test_retrieval_returns_empty_list_when_embedder_fails(monkeypatch):
    import rag.retriever

    monkeypatch.setattr(rag.retriever, "embed_text", lambda _text: (_ for _ in ()).throw(RuntimeError("Model unavailable")))
    assert rag.retriever.retrieve_reviews("Why Darr?") == []
