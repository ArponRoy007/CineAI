from auth.security import hash_password


class UserCollection:
    def __init__(self):
        self.user = {"_id": "user-1", "name": "Darr fan", "username": "darrfan", "email": "darr@example.com", "password_hash": hash_password("password123"), "role": "user", "is_active": True}

    def find_one(self, _query):
        return self.user


class MovieCursor:
    def __init__(self, movies):
        self.movies = movies

    def sort(self, *_args, **_kwargs):
        return self

    def __iter__(self):
        return iter(self.movies)


class MovieCollection:
    def __init__(self):
        self.movies = [{"movie_id": "darr", "title": "Darr", "year": 1993, "zone": "Bollywood", "genre": "Thriller", "roy_rating": 5.0, "verdict": "Must Watch", "review_text": "A memorable thriller.", "review_status": "CONFIRMED", "ingest_to_rag": True}]

    def find(self, _query, _projection=None):
        return MovieCursor(self.movies)


def test_core_services_smoke_auth_movie_lookup_and_ask_roy(monkeypatch):
    import ai.llm
    import auth.login
    import rag.qa
    import ui.home

    users = UserCollection()
    movies = MovieCollection()
    monkeypatch.setattr(auth.login, "users_collection", users)
    monkeypatch.setattr(ui.home, "enrich_movie", lambda *_args: {})
    monkeypatch.setattr(rag.qa, "build_context", lambda **_kwargs: ("Movie: Darr\nRoy's Review: A memorable thriller.", [{"metadata": {"title": "Darr"}}]))
    monkeypatch.setattr(ai.llm, "generate_answer", lambda **_kwargs: "Roy calls Darr a memorable thriller.")

    user = auth.login.authenticate_user("darrfan", "password123")
    results = ui.home._search(movies, "Darr")
    answer = rag.qa.answer_question("Why did Roy like Darr?", movie_title=results[0]["title"])

    assert user["username"] == "darrfan"
    assert results[0]["title"] == "Darr"
    assert "memorable thriller" in answer["answer"]
