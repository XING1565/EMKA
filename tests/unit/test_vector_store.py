from backend.app.core.vector_store import EMKA_DOCUMENT_CHUNKS_COLLECTION, InMemoryVectorStore


def test_in_memory_vector_store_creates_inserts_and_searches():
    store = InMemoryVectorStore(dimension=3)

    assert store.collection_name == EMKA_DOCUMENT_CHUNKS_COLLECTION
    assert store.ensure_collection() is True
    assert store.insert_chunk_vector(
        "emb-1",
        [1.0, 0.0, 0.0],
        {"document_id": "doc-1", "title": "风险表"},
    )
    assert store.insert_chunk_vector(
        "emb-2",
        [0.0, 1.0, 0.0],
        {"document_id": "doc-2", "title": "会议纪要"},
    )

    hits = store.search([1.0, 0.0, 0.0], top_k=1)

    assert len(hits) == 1
    assert hits[0].embedding_id == "emb-1"
    assert hits[0].metadata["document_id"] == "doc-1"
