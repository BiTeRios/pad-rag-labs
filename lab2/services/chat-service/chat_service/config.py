from pathlib import Path

from rag_common.app import ServiceSettings

SERVICE_ROOT = Path(__file__).resolve().parent.parent


class Settings(ServiceSettings):
    service_name: str = "chat-service"
    database_url: str = "postgresql+asyncpg://chat:chat@localhost:5432/chat"
    rabbitmq_url: str | None = "amqp://guest:guest@localhost:5672/"

    retrieval_url: str = "http://localhost:8005"
    retrieval_timeout_s: float = 60

    # LLM выбрана в Lab1 (E8): qwen3:8b без режима рассуждений; Ollama — внешний сервис на хосте
    llm_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen3:8b"
    llm_think: bool | None = False      # None — не передавать (модели без thinking, например gemma3)
    llm_temperature: float = 0.1
    llm_num_ctx: int = 8192
    llm_seed: int | None = 42
    llm_timeout_s: float = 120

    prompts_file: Path = SERVICE_ROOT / "prompts.yaml"
    prompt_name: str = "strict"
    no_context_answer: str = "В документации недостаточно информации для ответа на этот вопрос."
    refusal_marker: str = "недостаточно информации"  # по этой фразе ответ модели считается отказом

    max_question_chars: int = 1000
