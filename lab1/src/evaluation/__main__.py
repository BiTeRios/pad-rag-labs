"""CLI: python -m src.evaluation --name NAME [--retrieval-only] [--no-judge] [--llm KEY] [--prompt NAME]
                                [--no-rerank] [--top-k N] [--model KEY] [параметры chunking] [--only f01,m02].
     python -m src.evaluation --rejudge NAME [--name NEW] — только судья на сохранённых ответах прогона NAME.

Результаты: experiments/results/<NAME>/{summary.json, results.jsonl, report.md}.
"""

import argparse
import logging
import sys
from datetime import datetime

from src.config import load_config, resolve_path
from src.evaluation.evaluate import evaluate, rejudge
from src.factory import add_chunking_args, chunking_params
from src.generation.llm import LLMError
from src.logging_setup import setup_logging

log = logging.getLogger("evaluation")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Оценка RAG на наборе вопросов")
    parser.add_argument("--name", help="имя прогона (папка результатов); по умолчанию run-<дата-время>")
    parser.add_argument("--rejudge", metavar="NAME", help="перезапустить только судью на ответах прогона NAME")
    parser.add_argument("--config", help="YAML-конфиг (по умолчанию configs/config.yaml)")
    parser.add_argument("--retrieval-only", action="store_true", help="только метрики retrieval, без LLM")
    parser.add_argument("--no-judge", action="store_true", help="без LLM-судьи")
    parser.add_argument("--llm", help="ключ LLM из llm.models")
    parser.add_argument("--prompt", help="вариант промпта")
    parser.add_argument("--no-rerank", action="store_true", help="без reranker")
    parser.add_argument("--top-k", type=int, help="сколько chunks передавать LLM")
    parser.add_argument("--model", help="ключ embedding-модели")
    parser.add_argument("--only", help="id вопросов через запятую")
    add_chunking_args(parser)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    setup_logging(resolve_path(cfg["evaluation"]["log_file"]), args.log_level)
    args.name = args.name or args.rejudge or datetime.now().strftime("run-%Y%m%d-%H%M")
    try:
        if args.rejudge:
            result = rejudge(cfg, args.rejudge, args.name)
        else:
            result = evaluate(
                cfg,
                args.name,
                model=args.model,
                chunking=chunking_params(cfg, args),
                use_reranker=False if args.no_rerank else None,
                llm=args.llm,
                prompt=args.prompt,
                top_k=args.top_k,
                generate=not args.retrieval_only,
                judge=not args.no_judge,
                question_ids=args.only.split(",") if args.only else None,
            )
    except (FileNotFoundError, ValueError, LLMError) as error:
        log.error("%s", error)
        return 1

    summary = result["summary"]
    top_k = result["params"]["top_k"]
    overall = summary["retrieval"]["overall"]
    print(f"\nПрогон {args.name}: {result['params']['questions']} вопросов, {summary['elapsed_s']} с")
    print(f"Retrieval: Hit@{top_k} {overall[f'hit@{top_k}']}, Recall@{top_k} {overall[f'recall@{top_k}']}, MRR {overall['mrr']}")
    if "generation" in summary:
        generation = summary["generation"]
        print(f"Отказы: верные {generation['correct_refusal_rate']}, ложные {generation['false_refusal_rate']}; "
              f"citation hit {generation['citation_hit_rate']}")
    if "judge" in summary:
        overall_judge = summary["judge"]["overall"]
        print(f"Судья: correctness {overall_judge['correctness']}, faithfulness {overall_judge['faithfulness']}")
    print(f"Отчёт: {resolve_path(cfg['evaluation']['results_dir']) / args.name / 'report.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
