from rag_common.app import ServiceSettings


class Settings(ServiceSettings):
    service_name: str = "retrieval-service"
    indexing_url: str = "http://localhost:8004"
    inference_url: str = "http://localhost:8003"
    indexing_timeout_s: float = 10
    inference_timeout_s: float = 30    # reranker 20 пар на CPU — секунды

    # Параметры выбраны в Lab1 (E5–E7)
    top_k: int = 5
    max_top_k: int = 20
    candidates: int = 20               # top-N векторного поиска до фильтров и reranker
    score_threshold: float = 0.78      # косинусная близость e5; 0 — выкл
    dedup_threshold: float = 0.8       # Jaccard по 3-словным шинглам; 0 — выкл
    min_chars: int = 50
    max_per_document: int = 0          # 0 — без лимита
    reranker_enabled: bool = True
    rerank_min_score: float = 0.1
    # Reranker недоступен → искать без него (результат помечается degraded), а не отвечать ошибкой
    rerank_fallback: bool = True
    max_query_chars: int = 1000
