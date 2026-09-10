"""Run hand-checked hybrid recommendation pairs before changing weights."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.recommender import rank_candidates


SANITY_CASES = [
    {
        "name": "Psychological thriller should favour crime thriller",
        "source": {"title": "Darr", "genre": "Psychological Thriller", "review_text": "A tense memorable thriller with a dangerous obsession."},
        "candidates": [
            {"title": "Baazigar", "genre": "Crime Thriller", "review_text": "A tense thriller driven by dangerous obsession and memorable performances.", "roy_rating": 4.5, "verdict": "Must Watch", "embedding_distance": 0.10},
            {"title": "Light Romance", "genre": "Romance", "review_text": "A warm gentle love story.", "roy_rating": 4.5, "verdict": "Good Watch", "embedding_distance": 0.18},
            {"title": "Weak Thriller", "genre": "Thriller", "review_text": "A tense thriller with obsession.", "roy_rating": 2.0, "verdict": "Don't Watch", "embedding_distance": 0.04},
        ],
        "expected_top": "Baazigar",
    },
    {
        "name": "Reflective science-fiction should favour reflective science-fiction",
        "source": {"title": "Arrival", "genre": "Science Fiction Drama", "review_text": "A thoughtful emotional story about language, time and human connection."},
        "candidates": [
            {"title": "Interstellar", "genre": "Science Fiction Drama", "review_text": "A thoughtful emotional journey through time, family and human connection.", "roy_rating": 5.0, "verdict": "Must Watch", "embedding_distance": 0.12},
            {"title": "Broad Comedy", "genre": "Comedy", "review_text": "A loud silly comic adventure.", "roy_rating": 4.0, "verdict": "Good Watch", "embedding_distance": 0.20},
        ],
        "expected_top": "Interstellar",
    },
]


def main():
    for case in SANITY_CASES:
        ranked = rank_candidates(case["source"], case["candidates"], limit=3)
        titles = ", ".join(f"{movie['title']} ({movie['recommendation_score']:.3f})" for movie in ranked)
        print(f"{case['name']}: {titles or 'no qualifying recommendations'}")


if __name__ == "__main__":
    main()
