"""Очистка Markdown документации Kubernetes: front matter, шорткоды Hugo, HTML, ссылки, emphasis.

Код (fenced blocks) защищён: в нём заменяются только шорткоды, остальное не трогается,
иначе пострадают плейсхолдеры вида `kubectl logs <pod-name>`.
"""

import html
import re

from src.grabber.metadata import split_front_matter
from src.preprocessing.segments import split_code

# Блоки, которые удаляются вместе с содержимым.
_DROP_BLOCKS = re.compile(
    r"\{\{[<%]\s*(comment|mermaid)\b.*?[>%]\}\}.*?\{\{[<%]\s*/\s*\1\s*[>%]\}\}", re.DOTALL
)
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_SHORTCODE = re.compile(r"\{\{[<%]\s*(/?)\s*([\w/-]+)(.*?)\s*[>%]\}\}", re.DOTALL)
_ATTR = re.compile(r'([\w-]+)\s*=\s*"([^"]*)"')
_POSITIONAL = re.compile(r'^\s*"([^"]*)"')

# Шорткод {{% heading "..." %}} на сайте превращается в стандартный заголовок раздела.
_HEADINGS = {
    "objectives": "Objectives",
    "prerequisites": "Before you begin",
    "whatsnext": "What's next",
    "cleanup": "Clean up",
    "synopsis": "Synopsis",
    "options": "Options",
    "seealso": "See also",
}
_CALLOUTS = {"note": "Note:", "caution": "Caution:", "warning": "Warning:"}
# Содержимое этих шорткодов берётся из других частей сайта (glossary, includes), в корпусе его нет.
_DROP_TAGS = {
    "include", "version-check", "thirdparty-content", "glossary_definition", "api-reference",
    "tutorials/modules", "legacy-repos-deprecation",
}

# Удаляются только известные HTML-теги; <pod-name> и подобные плейсхолдеры остаются.
_HTML_TAG_NAMES = (
    "a|abbr|b|blockquote|br|caption|center|code|dd|del|details|div|dl|dt|em|figcaption|figure|font|"
    "h[1-6]|hr|i|img|ins|kbd|li|mark|nobr|ol|p|pre|s|section|small|span|strong|sub|summary|sup|"
    "table|tbody|td|tfoot|th|thead|tr|tt|u|ul"
)
_HTML_ROW = re.compile(r"<tr\b[^>]*>(.*?)</tr\s*>", re.IGNORECASE | re.DOTALL)
_HTML_CELL = re.compile(r"<t[dh]\b[^>]*>(.*?)</t[dh]\s*>", re.IGNORECASE | re.DOTALL)
_TABLE_ROW_GAP = re.compile(r"(?<=\|)[ \t]*\n(?:[ \t]*\n)+(?=[ \t]*\|)")
_HTML_LIST_ITEM = re.compile(r"<li\b[^>]*>", re.IGNORECASE)
_HTML_BREAK = re.compile(r"<br\s*/?>|</(?:p|li|div|ul|ol|table|caption|h[1-6]|summary)\s*>", re.IGNORECASE)
_HTML_TAG = re.compile(rf"</?(?:{_HTML_TAG_NAMES})\b[^<>]*>", re.IGNORECASE)
_HTML_SCRIPT = re.compile(r"<(script|style)\b.*?</\1\s*>", re.IGNORECASE | re.DOTALL)

_IMAGE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")
_REF_LINK = re.compile(r"\[([^\]]+)\]\[[^\]]*\]")
_REF_DEFINITION = re.compile(r"^\s*\[[^\]]+\]:\s+\S+.*$", re.MULTILINE)
# Emphasis может переноситься на следующую строку исходника, но не через пустую строку.
_BOLD = re.compile(r"(\*\*|__)(?=\S)((?:[^\n]|\n(?!\s*\n))+?)(?<=\S)\1")
_ITALIC = re.compile(r"(?<![\w*])([*_])(?=\S)((?:[^*_\n]|\n(?!\s*\n))+?)(?<=\S)\1(?![\w*])")
_HEADING_ANCHOR = re.compile(r"[ \t]*\{#[\w.:-]+\}")  # Hugo: ## Title {#custom-id}
_TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$", re.MULTILINE)
_INLINE_CODE = re.compile(r"`[^`\n]+`")


def clean_markdown(raw: str) -> str:
    _, body = split_front_matter(raw)
    text = _DROP_BLOCKS.sub("", body)
    text = _HTML_COMMENT.sub("", text)
    text = _SHORTCODE.sub(_render_shortcode, text)
    return "\n".join(seg if is_code else _clean_prose(seg) for is_code, seg in split_code(text))


def _render_shortcode(match: re.Match) -> str:
    closing, name, raw_attrs = match.groups()
    attrs = dict(_ATTR.findall(raw_attrs))
    positional = _POSITIONAL.match(raw_attrs)
    arg = positional.group(1) if positional else ""

    if name == "highlight":  # {{< highlight yaml >}} ... {{< /highlight >}} — тот же блок кода
        return "```" if closing else f"```{raw_attrs.split()[0] if raw_attrs.split() else ''}"
    if closing or name in _DROP_TAGS:
        return ""
    if name == "glossary_tooltip":  # без text сайт показывает сам термин
        return attrs.get("text") or attrs.get("term_id", "")
    if name == "link":
        return attrs.get("text", "")
    if name in _CALLOUTS:
        return _CALLOUTS[name]
    if name == "alert":
        return f"{attrs.get('title', 'Note')}:"
    if name == "heading":
        return _HEADINGS.get(arg, arg.replace("-", " ").capitalize())
    if name == "feature-state":
        if "for_k8s_version" in attrs:
            return f"Feature state: Kubernetes {attrs['for_k8s_version']} [{attrs.get('state', '')}]"
        return f"Feature gate: {attrs['feature_gate_name']}" if "feature_gate_name" in attrs else ""
    if name in ("code_sample", "codenew", "example"):
        return f"Example manifest: {attrs['file']}" if "file" in attrs else ""
    if name == "figure":
        return attrs.get("caption") or attrs.get("alt", "")
    if name in ("tab", "details", "table", "pageinfo"):
        label = attrs.get("name") or attrs.get("summary") or attrs.get("caption") or ""
        return f"{label}:" if label else ""
    if name in ("skew", "param"):
        return "<version>" if arg in ("currentVersion", "version", "latestVersion") or name == "skew" else f"<{arg}>"
    return ""  # tabs, relref и прочие служебные шорткоды: остаётся только содержимое


def _clean_prose(text: str) -> str:
    # Inline code прячется под плейсхолдеры, чтобы его не задели правила для HTML и emphasis.
    spans: list[str] = []

    def hide(match: re.Match) -> str:
        spans.append(match.group(0))
        return f"\x00{len(spans) - 1}\x00"

    text = _INLINE_CODE.sub(hide, text)
    text = _HTML_SCRIPT.sub("", text)
    text = _TABLE_ROW_GAP.sub("\n", _HTML_ROW.sub(_render_row, text))
    text = _HTML_LIST_ITEM.sub("\n- ", text)
    text = _HTML_BREAK.sub("\n", text)
    text = _HTML_TAG.sub("", text)
    text = _IMAGE.sub(r"\1", text)
    text = _LINK.sub(r"\1", text)
    text = _REF_LINK.sub(r"\1", text)
    text = _REF_DEFINITION.sub("", text)
    text = _HEADING_ANCHOR.sub("", text)
    text = _BOLD.sub(r"\2", text)
    text = _ITALIC.sub(r"\2", text)
    text = _TABLE_SEPARATOR.sub("", text)
    text = html.unescape(text)
    return re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], text)


def _render_row(match: re.Match) -> str:
    """HTML-строка таблицы -> строка Markdown-таблицы в одну строку."""
    cells = [" ".join(cell.split()) for cell in _HTML_CELL.findall(match.group(1))]
    return f"\n| {' | '.join(cells)} |\n" if cells else "\n"
