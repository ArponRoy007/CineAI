def test_rebuild_ingests_confirmed_reviews_and_marks_them_ready(monkeypatch):
    import scripts.rebuild_embeddings as rebuild

    movie = {"_id": "darr", "title": "Darr", "review_status": "CONFIRMED", "review_text": "A memorable thriller."}
    updates = []

    class Movies:
        def find(self, _query):
            return [movie]

        def update_one(self, query, update):
            updates.append((query, update))

    monkeypatch.setattr(rebuild, "movies_collection", Movies())
    monkeypatch.setattr(rebuild, "ingest_movie_review", lambda item: item["title"] == "Darr")

    rebuild.main()

    assert updates == [({"_id": "darr"}, {"$set": {"ingest_to_rag": True}})]


def test_rebuild_exits_cleanly_when_mongo_is_unavailable(monkeypatch, capsys):
    import scripts.rebuild_embeddings as rebuild

    class Movies:
        def find(self, _query):
            raise RuntimeError("MongoDB unavailable")

    monkeypatch.setattr(rebuild, "movies_collection", Movies())
    rebuild.main()

    assert "Could not load confirmed reviews" in capsys.readouterr().out
