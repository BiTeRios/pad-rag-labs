from rag_common.app import ServiceSettings


class Settings(ServiceSettings):
    service_name: str = "inference-service"

    # Модели выбраны в Lab1 (E4, E6)
    embedding_model: str = "intfloat/multilingual-e5-base"
    query_prefix: str = "query: "      # e5 обучена с префиксами query/passage
    passage_prefix: str = "passage: "
    max_seq_length: int = 512
    embedding_batch_size: int = 32

    reranker_enabled: bool = True
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    reranker_max_length: int = 512
    reranker_batch_size: int = 16

    device: str = "auto"               # auto | cpu | cuda
    max_texts: int = 256               # ограничение размера запроса: защита от перегрузки
    max_text_chars: int = 8000
    max_concurrency: int = 1           # одновременных вычислений: модель всё равно занимает все ядра/GPU
