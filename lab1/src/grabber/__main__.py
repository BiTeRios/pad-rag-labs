"""CLI: python -m src.grabber [--dry-run] [--limit N] [--config PATH].

Коды выхода: 0 — успех, 1 — источник недоступен, 2 — часть документов не получена
(корпус пригоден, повторный запуск докачает их).
"""

import argparse
import logging
import os
import sys

from src.config import load_config, resolve_path
from src.grabber.github_source import GitHubSource, SourceError
from src.grabber.grabber import Grabber
from src.logging_setup import setup_logging

log = logging.getLogger("grabber")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Синхронизация корпуса документов с GitHub")
    parser.add_argument("--config", help="YAML-конфиг (по умолчанию configs/config.yaml)")
    parser.add_argument("--dry-run", action="store_true", help="показать изменения, ничего не скачивая")
    parser.add_argument("--limit", type=int, help="скачать не больше N документов (для отладки)")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)["grabber"]
    setup_logging(resolve_path(cfg["log_file"]), args.log_level)

    source = GitHubSource(
        repo=cfg["repo"],
        ref=cfg["ref"],
        docs_root=cfg["docs_root"],
        sections=cfg["sections"],
        extensions=cfg["extensions"],
        token=os.getenv("GITHUB_TOKEN") or None,
        timeout_s=cfg["timeout_s"],
        max_retries=cfg["max_retries"],
        backoff_s=cfg["backoff_s"],
        pool_size=cfg["max_workers"],
    )
    grabber = Grabber(
        source,
        raw_dir=resolve_path(cfg["raw_dir"]),
        manifest_path=resolve_path(cfg["manifest_file"]),
        site_url=cfg["site_url"],
        source_name=cfg["source_name"],
        max_workers=cfg["max_workers"],
    )

    try:
        stats = grabber.sync(dry_run=args.dry_run, limit=args.limit)
    except SourceError as error:
        log.error("Источник недоступен: %s", error)
        return 1

    log.info(
        "Итог%s: добавлено %d, обновлено %d, без изменений %d, удалено %d, дублей %d, ошибок %d",
        " (dry-run)" if args.dry_run else "",
        stats.added, stats.updated, stats.unchanged, stats.deleted, stats.duplicates, stats.failed,
    )
    return 2 if stats.failed else 0


if __name__ == "__main__":
    sys.exit(main())
