from backend.app.rag.embeddings import DeterministicEmbeddingService


def test_deterministic_embedding_dimension_and_stability():
    service = DeterministicEmbeddingService(dimension=16)

    first = service.embed("project risk delay")
    second = service.embed("project risk delay")

    assert len(first) == 16
    assert first == second
    assert any(value != 0 for value in first)
