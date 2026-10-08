"""Chunking: три стратегии, выбор и параметры задаются в config (секция chunking).

- fixed     — окно фиксированного размера в символах; overlap > 0 даёт вариант «с перекрытием»
              (overlap учитывается только этой стратегией);
- paragraph — абзацы (и блоки кода целиком) упаковываются в chunk до chunk_size;
- heading   — chunk = секция между заголовками; большая секция делится по абзацам.

У каждого chunk есть путь заголовков «Title > Section > Subsection», с include_heading
он добавляется в начало текста.
"""

import bisect
import re
from dataclasses import dataclass

from src.preprocessing.segments import split_code

STRATEGIES = ("fixed", "paragraph", "heading")
DOC_FIELDS = ("source", "url", "title", "section", "updated_at")

_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_WHITESPACE = re.compile(r"\s")


@dataclass(frozen=True)
class Block:
    text: str
    path: tuple[str, ...]  # (title, h2, h3, ...)
    is_heading: bool = False


def chunk_document(
    doc: dict,
    strategy: str,
    chunk_size: int,
    chunk_overlap: int = 0,
    include_heading: bool = True,
) -> list[dict]:
    if strategy not in STRATEGIES:
        raise ValueError(f"неизвестная стратегия chunking '{strategy}', допустимо: {STRATEGIES}")

    blocks = parse_blocks(doc["text"], doc["title"])
    if strategy == "fixed":
        pieces = _chunk_fixed(blocks, chunk_size, chunk_overlap)
    elif strategy == "paragraph":
        pieces = _pack(blocks, chunk_size)
    else:
        pieces = _chunk_heading(blocks, chunk_size)

    chunks = []
    for path, body in pieces:
        heading = " > ".join(path)
        index = len(chunks)
        chunks.append(
            {
                "chunk_id": f"{doc['document_id']}#{index}",
                "document_id": doc["document_id"],
                "chunk_index": index,
                "text": f"{heading}\n\n{body}" if include_heading else body,
                "heading": heading,
                **{field: doc.get(field) for field in DOC_FIELDS},
                "doc_sha": doc.get("sha"),  # версия документа в источнике
            }
        )
    return chunks


def parse_blocks(text: str, title: str) -> list[Block]:
    """Абзацы, блоки кода и заголовки с путём заголовков, в котором они находятся."""
    blocks: list[Block] = []
    stack: list[tuple[int, str]] = []
    paragraph: list[str] = []

    def path() -> tuple[str, ...]:
        return (title, *(name for _, name in stack))

    def flush() -> None:
        if paragraph:
            blocks.append(Block("\n".join(paragraph).strip(), path()))
            paragraph.clear()

    for is_code, segment in split_code(text):
        if is_code:
            flush()
            blocks.append(Block(segment.strip("\n"), path()))
            continue
        for line in segment.split("\n"):
            match = _HEADING.match(line)
            if match:
                flush()
                level, name = len(match.group(1)), match.group(2)
                if level == 1 and name == title:
                    continue
                while stack and stack[-1][0] >= level:
                    stack.pop()
                stack.append((level, name))
                blocks.append(Block(line.strip(), path(), is_heading=True))
            elif line.strip():
                paragraph.append(line)
            else:
                flush()
    flush()
    return blocks


def split_fixed(text: str, size: int, overlap: int = 0) -> list[tuple[int, str]]:
    """Окна до size символов, без разрыва слов; [(позиция начала, текст), ...]."""
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError(f"нужно size > 0 и 0 <= overlap < size, получено size={size}, overlap={overlap}")
    pieces, start, length = [], 0, len(text)
    while start < length:
        end = min(start + size, length)
        if end < length:
            cut = max(text.rfind(" ", start, end + 1), text.rfind("\n", start, end + 1))
            if cut > start + size // 2:
                end = cut
        piece = text[start:end].strip()
        if piece:
            pieces.append((start, piece))
        if end >= length:
            break
        next_start = end - overlap
        if overlap and not text[next_start - 1].isspace():
            space = _WHITESPACE.search(text, next_start, end)
            if space:
                next_start = space.end()
        start = max(next_start, start + 1)
    return pieces


def _chunk_fixed(blocks: list[Block], size: int, overlap: int) -> list[tuple[tuple[str, ...], str]]:
    texts, offsets, position = [], [], 0
    for block in blocks:
        offsets.append(position)
        texts.append(block.text)
        position += len(block.text) + 2
    pieces = split_fixed("\n\n".join(texts), size, overlap)
    return [(blocks[bisect.bisect_right(offsets, start) - 1].path, piece) for start, piece in pieces]


def _pack(blocks: list[Block], size: int) -> list[tuple[tuple[str, ...], str]]:
    """Последовательные блоки упаковываются в chunk до size символов; большой блок режется split_fixed.

    Заголовок в конце chunk переносится в следующий, чтобы не отрываться от своего текста.
    """
    pieces: list[tuple[tuple[str, ...], str]] = []
    current: list[Block] = []

    def emit() -> list[Block]:
        carry = []
        while current and current[-1].is_heading:
            carry.insert(0, current.pop())
        if any(not block.is_heading for block in current):
            pieces.append((current[0].path, "\n\n".join(block.text for block in current)))
        current.clear()
        return carry

    for block in blocks:
        parts = [block] if len(block.text) <= size else [
            Block(text, block.path) for _, text in split_fixed(block.text, size)
        ]
        for part in parts:
            if current and _length(current) + 2 + len(part.text) > size:
                current.extend(emit())
            current.append(part)
    emit()
    return pieces


def _chunk_heading(blocks: list[Block], size: int) -> list[tuple[tuple[str, ...], str]]:
    pieces = []
    sections: list[list[Block]] = [[]]
    for block in blocks:
        if block.is_heading:
            sections.append([])
        else:
            sections[-1].append(block)
    for section in sections:
        if not section:
            continue  # заголовок без текста, например сразу за ним подзаголовок
        if _length(section) <= size:
            pieces.append((section[0].path, "\n\n".join(block.text for block in section)))
        else:
            pieces.extend(_pack(section, size))
    return pieces


def _length(blocks: list[Block]) -> int:
    return sum(len(block.text) for block in blocks) + 2 * (len(blocks) - 1)
