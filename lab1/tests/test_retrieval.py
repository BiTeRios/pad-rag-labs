import pytest
from qdrant_client import QdrantClient

from src.embeddings.embedder import Embedder
from src.embeddings.indexer import document_fingerprint, index_chunks
from src.factory import chunking_params, collection_name
from src.retrieval.retriever import Retriever
from src.retrieval.vector_store import QdrantStore, point_id
from tests.helpers import DIM, BagOfWordsModel, make_chunk

CHUNKS = [
    make_chunk("pods", 0, "pods restart policy always onfailure never", section="concepts/workloads"),
    make_chunk("pods", 1, "pods lifecycle phases pending running", section="concepts/workloads"),
    make_chunk("services", 0, "service exposes pods network clusterip nodeport", section="concepts/services"),
    make_chunk("volumes", 0, "persistent volume claim storage class", section="concepts/storage"),
]


@pytest.fixture
def model():
    return BagOfWordsModel()


@pytest.fixture
def embedder(model):
    return Embedder("fake", query_prefix="query: ", passage_prefix="passage: ", model=model)


@pytest.fixture
def store():
    return QdrantStore(QdrantClient(":memory:"), "test")


def test_embedder_applies_model_prefixes(embedder, model):
    embedder.embed_documents(["pods"])
    embedder.embed_query("what is a pod")
    assert model.encoded == ["passage: pods", "query: what is a pod"]
    assert embedder.dim == DIM


def test_index_then_retrieve_returns_relevant_chunks_with_metadata(embedder, store):
    stats = index_chunks(CHUNKS, embedder, store)

    results = Retriever(embedder, store, top_k=2).retrieve("persistent storage volume")

    assert (stats.added, stats.chunks_indexed, store.count()) == (3, 4, 4)
    assert len(results) == 2
    assert results[0]["document_id"] == "volumes"
    assert results[0]["url"] == "https://kubernetes.io/docs/volumes/"
    assert results[0]["score"] >= results[1]["score"]


def test_reindex_without_changes_embeds_nothing(embedder, store, model):
    index_chunks(CHUNKS, embedder, store)
    model.encoded.clear()

    stats = index_chunks(CHUNKS, embedder, store)

    assert model.encoded == []
    assert (stats.unchanged, stats.chunks_indexed, store.count()) == (3, 0, 4)


def test_changed_document_replaces_all_its_chunks(embedder, store, model):
    index_chunks(CHUNKS, embedder, store)
    model.encoded.clear()
    new_pods = [make_chunk("pods", 0, "pods are the smallest deployable units", sha="v2")]

    stats = index_chunks(new_pods + CHUNKS[2:], embedder, store)

    assert (stats.updated, stats.unchanged, stats.chunks_indexed) == (1, 2, 1)
    assert model.encoded == ["passage: pods are the smallest deployable units"]
    assert store.count() == 3  # старый chunk pods#1 удалён
    assert store.indexed_documents()["pods"] == document_fingerprint(new_pods)


def test_changed_text_with_same_source_sha_is_reindexed(embedder, store):
    """Изменилась очистка, а версия в источнике прежняя: chunks всё равно обновляются."""
    index_chunks(CHUNKS, embedder, store)
    recleaned = [{**CHUNKS[3], "text": "persistent volume claim storage class etcd"}]

    stats = index_chunks(CHUNKS[:3] + recleaned, embedder, store)

    assert (stats.updated, stats.chunks_indexed) == (1, 1)


def test_removed_document_is_deleted_from_index(embedder, store):
    index_chunks(CHUNKS, embedder, store)

    stats = index_chunks(CHUNKS[:3], embedder, store)

    assert stats.deleted == 1
    assert "volumes" not in store.indexed_documents()


def test_rebuild_after_clear_reindexes_everything(embedder, tmp_path, model):
    store = QdrantStore(QdrantClient(path=str(tmp_path)), "test")  # дисковый режим, как в CLI
    index_chunks(CHUNKS, embedder, store)

    store.clear()
    stats = index_chunks(CHUNKS, embedder, store)

    assert (stats.added, stats.chunks_indexed, store.count()) == (3, 4, 4)
    store.client.close()


def test_top_k_and_metadata_filter(embedder, store):
    index_chunks(CHUNKS, embedder, store)
    retriever = Retriever(embedder, store, top_k=10)

    assert len(retriever.retrieve("pods", top_k=3)) == 3
    filtered = retriever.retrieve("pods", filters={"section": "concepts/workloads"})
    assert {chunk["document_id"] for chunk in filtered} == {"pods"}
    any_of = retriever.retrieve("pods", filters={"section": ["concepts/services", "concepts/storage"]})
    assert {chunk["document_id"] for chunk in any_of} == {"services", "volumes"}


def test_point_id_is_deterministic():
    assert point_id("pods#0") == point_id("pods#0") != point_id("pods#1")


def test_collection_name_encodes_model_and_chunking():
    cfg = {
        "vector_store": {"collection_prefix": "k8s"},
        "chunking": {"strategy": "paragraph", "chunk_size": 800, "chunk_overlap": 100, "include_heading": False},
    }
    params = chunking_params(cfg)
    assert params["chunk_overlap"] == 0  # overlap есть только у fixed
    assert collection_name(cfg, "bge-m3", params) == "k8s__bge-m3__paragraph-800-0-nh"
