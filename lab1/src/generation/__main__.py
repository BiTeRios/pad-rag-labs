"""CLI: python -m src.generation "вопрос" [--llm KEY] [--prompt NAME] [--no-rerank] [--top-k N] [--show-context].

Полный RAG: поиск контекста → ответ LLM → источники.
"""

import argparse
import logging
import sys

from src.config import load_config, resolve_path
from src.factory import add_chunking_args, build_rag, chunking_params
from src.generation.llm import LLMError
from src.logging_setup import setup_logging
from src.retrieval.filters import body_text

log = logging.getLogger("generation")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ответ на вопрос по документации Kubernetes")
    parser.add_argument("question", help="вопрос")
    parser.add_argument("--config", help="YAML-конфиг (по умолчанию configs/config.yaml)")
    parser.add_argument("--llm", help="ключ LLM из llm.models")
    parser.add_argument("--prompt", help="вариант промпта из generation.prompts_file")
    parser.add_argument("--no-rerank", action="store_true", help="без reranker")
    parser.add_argument("--top-k", type=int, help="сколько chunks передать LLM")
    parser.add_argument("--section", help="искать только в разделе, например concepts/workloads/pods")
    parser.add_argument("--model", help="ключ embedding-модели из embeddings.models")
    parser.add_argument("--show-context", action="store_true", help="показать контекст, переданный LLM")
    add_chunking_args(parser)
    parser.add_argument("--log-level", default="WARNING")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    setup_logging(resolve_path(cfg["generation"]["log_file"]), args.log_level)

    try:
        rag, client = build_rag(
            cfg,
            model=args.model,
            chunking=chunking_params(cfg, args),
            llm=args.llm,
            prompt=args.prompt,
            use_reranker=False if args.no_rerank else None,
        )
    except (FileNotFoundError, ValueError) as error:
        log.error("%s", error)
        return 1

    try:
        result = rag.ask(args.question, args.top_k, {"section": args.section} if args.section else None)
    except LLMError as error:
        log.error("Ошибка LLM: %s", error)
        return 1
    finally:
        client.close()

    answer = result.answer
    print(f"Вопрос: {answer.question}\n\nОтвет:\n{answer.text}\n")
    if answer.sources:
        print("Источники:")
        for source in answer.sources:
            print(f"- [{source['n']}] {source['heading']} — {source['url']}")
        print()
    if args.show_context:
        for n, chunk in enumerate(answer.context, 1):
            print(f"--- [{n}] {chunk['heading']}\n{body_text(chunk)}\n")

    stages = " → ".join(f"{stage} {count}" for stage, count in result.stages.items())
    llm_info = "LLM не вызывалась (нет контекста)"
    if answer.llm:
        llm_info = (
            f"LLM {answer.llm.model}: {result.generation_s:.1f} с, "
            f"{answer.llm.prompt_tokens} + {answer.llm.completion_tokens} токенов"
        )
    print(f"[поиск {result.retrieval_s:.2f} с: {stages}; {llm_info}; отказ: {'да' if answer.refused else 'нет'}]")
    log.info("question=%r refused=%s sources=%s stages=%s", answer.question, answer.refused,
             [s["url"] for s in answer.sources], result.stages)
    return 0


if __name__ == "__main__":
    sys.exit(main())
