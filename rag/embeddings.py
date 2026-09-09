from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


_model = None


def get_embedding_model():
    """
    Load the embedding model once and reuse it.
    """
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def embed_text(text: str) -> list[float]:
    """
    Convert one text string into an embedding vector.
    """
    if not text or not text.strip():
        raise ValueError("Cannot embed empty text.")

    model = get_embedding_model()

    vector = model.encode(
        text,
        normalize_embeddings=True,
    )

    return vector.tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Convert multiple texts into embedding vectors.
    """
    if not texts:
        return []

    model = get_embedding_model()

    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    return vectors.tolist()
