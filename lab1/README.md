# Lab1. RAG-система по документации Kubernetes

## 1. Описание проекта
RAG-система отвечает на вопросы по официальной документации Kubernetes и указывает источники, на которых основан ответ: ссылки на страницы kubernetes.io.

### Предметная область
Документация Kubernetes (https://kubernetes.io/docs), английская версия, три раздела:

| Раздел | Содержание | Файлов | Объём |
|--------|-----------|-------:|------:|
| concepts | как устроены объекты и компоненты кластера | 186 | 2.3 MB |
| tasks | пошаговые инструкции | 221 | 1.7 MB |
| tutorials | учебные сценарии | 45 | 0.4 MB |
| **Итого** | | **~450** | **~4.4 MB** |

Данные по состоянию на 2026-10-07. Набор разделов задаётся в config.

Почему выбрана эта тема:
- **Достаточно материала для ≥30 вопросов всех типов**:
  - факт: «какой порт по умолчанию у kubelet?»;
  - несколько документов: «чем Deployment отличается от StatefulSet?»;
  - конкретика: «какое поле задаёт число реплик?»;
  - контекст: «когда нужен DaemonSet?»;
  - вне базы: вопросы про Docker Swarm или не по теме.
- **Структура**: страницы в Markdown с заголовками, поэтому можно сравнить chunking по секциям с chunking фиксированного размера.
- **Документация живая**: она регулярно обновляется, так что инкрементальный grabber проверяется на реальных изменениях.
- **Связь с курсом**: Lab3 посвящена Kubernetes, и система отвечает на вопросы, которые понадобятся на защите.
- **Лицензия**: открытая, CC BY 4.0.

Рассмотренные альтернативы:

| Вариант | Почему не выбран |
|---------|------------------|
| Русская локализация Kubernetes docs | 146 страниц, перевод неполный: многих страниц concepts нет |
| Раздел reference | 1197 файлов (11 MB), в основном автогенерированный API-справочник: много шума, мало пояснений |
| Wikipedia | тема размыта, сложнее составить проверяемые вопросы |
| Документация FastAPI | меньше связи с курсом |

### Источник данных
GitHub-репозиторий [kubernetes/website](https://github.com/kubernetes/website), путь `content/en/docs/{concepts,tasks,tutorials}`.

Grabber (`src/grabber`) скачивает документы сам и при повторном запуске берёт только новые и изменённые. Подробнее в разделе 2.

Язык: документы на английском, вопросы и ответы на русском. Это обеспечивают мультиязычные эмбеддинги и LLM.

Kubernetes Documentation © The Kubernetes Authors, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## 2. Архитектура

### Grabber
```text
GitHub API: коммит ветки → дерево файлов разделов (путь + git blob SHA)
   ↓
сравнение SHA с data/manifest.json
   ├─ SHA совпал и файл на диске есть → пропуск
   ├─ новый или изменённый             → загрузка
   ├─ пропал из источника              → удаление
   └─ содержимое совпадает с другим    → дубль, пропуск
   ↓
загрузка raw.githubusercontent.com (8 потоков, ретраи, проверка SHA)
   ↓
data/raw/<раздел>/…/*.md + data/manifest.json (metadata)
```

- **Инкрементальность**: SHA файла в git меняется при любом изменении содержимого, поэтому сравнение SHA с manifest показывает, что скачивать. Повторный запуск без изменений в источнике тратит 5 запросов к API и ничего не скачивает.
- **Согласованность**: файлы скачиваются с того же коммита, с которого получен список. Хеш скачанного содержимого сверяется с SHA, поэтому повреждённый или неполный файл не сохраняется.
- **Ошибки**:
  - таймаут на каждый запрос; повторы с экспоненциальной паузой при 429/5xx и сетевых сбоях;
  - сбой одного документа логируется и не останавливает сбор; старая версия сохраняется, следующий запуск попробует снова;
  - кончился лимит API → понятное сообщение и код выхода 1.
- **Без дублей**: документ идентифицируется путём (`document_id`), так что повторная загрузка перезаписывает файл, а не создаёт копию. Файл с содержимым, уже встреченным под другим путём, пропускается.
- **Надёжная запись**: документы и manifest пишутся через временный файл, поэтому прерванный запуск не оставит полузаписанных данных.

Metadata документа в `data/manifest.json`:

| Поле | Пример |
|------|--------|
| `document_id` | `concepts/overview/components.md` |
| `source` | `kubernetes-docs` |
| `url` | `https://kubernetes.io/docs/concepts/overview/components/` |
| `title` | `Kubernetes Components` (из front matter) |
| `section` | `concepts/overview` |
| `description`, `content_type` | из front matter, если есть |
| `sha`, `size` | git blob SHA и размер в байтах |
| `commit_sha`, `commit_date` | коммит, с которого получена версия |
| `updated_at` | когда grabber получил эту версию |

### Preprocessing
```text
data/raw/*.md ─► очистка ─► нормализация ─► data/processed/documents.jsonl
                                               │
                                     chunking (strategy из config)
                                               ▼
                                    data/processed/chunks.jsonl
```

**Очистка** (`src/preprocessing/cleaning.py`). Шорткоды Hugo выбраны по статистике корпуса: около 30 видов, 819 подсказок `glossary_tooltip`, 591 блок `note`.

| Что в исходнике | Во что превращается |
|-----------------|---------------------|
| YAML front matter, `<!-- … -->` | удаляется (title и description уже в metadata) |
| `{{< glossary_tooltip text="containers" … >}}` | `containers` |
| `{{< note >}}…{{< /note >}}`, `caution`, `warning`, `alert` | `Note: …`, текст сохраняется |
| `{{< feature-state for_k8s_version="v1.29" state="stable" >}}` | `Feature state: Kubernetes v1.29 [stable]` |
| `{{% heading "prerequisites" %}}` | `Before you begin` |
| `{{< code_sample file="pods/simple-pod.yaml" >}}` | `Example manifest: pods/simple-pod.yaml` |
| `{{< highlight yaml >}}…{{< /highlight >}}` | обычный блок кода |
| `comment`, `mermaid` | удаляются вместе с содержимым |
| `include`, `glossary_definition`, `version-check` | удаляются: их текст хранится вне корпуса |
| `[text](url)`, `![alt](img)`, `**bold**`, `_italic_`, `{#anchor}` | только текст |
| HTML-таблицы и списки | строки `\| a \| b \|` и пункты `- …` |
| прочие HTML-теги, `&lt;` | удаляются / раскодируются |

Блоки кода защищены: в них заменяются только шорткоды. HTML удаляется по списку известных тегов, поэтому плейсхолдеры вроде `kubectl logs <pod-name>` сохраняются. Проверка на корпусе: вне кода не осталось ни шорткодов, ни HTML-тегов, ни Markdown-ссылок. Объём уменьшился с 4.43 до 3.82 млн символов.

**Нормализация** (`src/preprocessing/normalization.py`):
- Unicode NFKC; удаляются невидимые символы (zero-width, soft hyphen); типографские кавычки заменяются на обычные; табуляция заменяется пробелами.
- Строки, разбитые переносом в исходнике, склеиваются в абзац. Заголовки, списки, таблицы и цитаты остаются отдельными строками.
- Лишние пробелы и пустые строки схлопываются. Код не меняется, кроме пробелов в конце строк.
- Регистр сохраняется: embedding-модели его учитывают, а LLM читает исходный текст.

**Chunking** (`src/preprocessing/chunking.py`). Документ разбирается на блоки: абзацы, блоки кода целиком, заголовки. У каждого блока есть путь заголовков «Title > Section > Subsection».

| Стратегия | Как режет |
|-----------|-----------|
| `fixed` | окно `chunk_size` символов, без разрыва слов |
| `fixed` + `chunk_overlap` | то же, следующий chunk повторяет конец предыдущего |
| `paragraph` | абзацы упаковываются в chunk до `chunk_size`; заголовок в конце chunk переносится к своему тексту |
| `heading` | chunk = секция между заголовками; большая секция делится по абзацам |

С `include_heading: true` путь заголовков добавляется в начало chunk. У каждого chunk есть `chunk_id` (`<document_id>#<n>`), `heading` и metadata документа: `url`, `title`, `section`, `source`, `updated_at`.

Структура chunks при `chunk_size=1000`, без префикса заголовков. Это не качество поиска: его сравнивают эксперименты E1–E3.

| Стратегия | Chunks | Средняя длина | Медиана | Мин | Макс | Короче 200 |
|-----------|-------:|---------:|--------:|----:|-----:|-----------:|
| fixed | 4056 | 940 | 995 | 8 | 1000 | 94 |
| fixed + overlap 200 | 4884 | 960 | 996 | 73 | 1000 | 5 |
| paragraph | 4679 | 815 | 883 | 11 | 1055 | 82 |
| heading | 6497 | 567 | 585 | 1 | 1000 | 1022 |

У `heading` много коротких секций, поэтому фильтр коротких chunks (L1-15) для неё особенно важен.

### Embeddings и индекс
```text
documents.jsonl ─► chunking (config) ─► embedding-модель (GPU) ─► Qdrant: коллекция
                                                                  <prefix>__<модель>__<strategy>-<size>-<overlap>-<h|nh>
```

- **Своя коллекция на каждую комбинацию** модели и параметров chunking. Индексы для экспериментов живут рядом и не смешиваются.
- **Инкрементальность**: в payload хранится `doc_fingerprint` — хеш текстов всех chunks документа. Повторная индексация векторизует только документы с изменившимся отпечатком. Отпечаток меняется и при новой версии в источнике, и при изменении очистки, когда SHA в источнике прежний. Старые chunks такого документа сначала удаляются, потому что их число могло измениться. Документы, пропавшие из корпуса, удаляются из коллекции.
- **ID точки** = UUID5 от `chunk_id`, поэтому повторная запись того же chunk перезаписывает точку, а не создаёт дубль.
- **Payload** точки: текст chunk и вся metadata (`url`, `title`, `heading`, `section`, `source`, `updated_at`). По этим полям работают фильтры.

**Embedding-модели.** Вопросы задаются на русском, документы на английском. Поэтому нужна мультиязычная модель, которая сопоставляет смысл между языками.

| Модель | Размерность | Языки | Параметров | Макс. длина | Особенности |
|--------|-----------:|-------|-----------:|------------:|-------------|
| `intfloat/multilingual-e5-base` (основная) | 768 | ~100, включая ru/en | 278M | 512 токенов | префиксы `query:` / `passage:` |
| `BAAI/bge-m3` (для сравнения, E4) | 1024 | 100+ | 568M | 8192 токена | без префиксов |

Почему эти модели:
- бесплатные (MIT), работают локально на GPU;
- хорошо держат кросс-язычный поиск;
- e5-base вдвое легче bge-m3, поэтому выбрана основной;
- на нашем корпусе e5-base лучше без reranker, а bge-m3 с reranker впереди на 1 вопрос при индексации в 13 раз дольше, поэтому основной осталась e5-base (E4, раздел 10).

Chunk в 1000 символов ≈ 250 токенов, поэтому лимит 512 токенов у e5 не обрезает текст.

Замеры на RTX 4070 Ti, e5-base, `heading-1000`:

| Операция | Время |
|----------|------:|
| полная индексация ~6500 chunks (424 документа) | 67–115 с (векторизация ~380 chunks/с, остальное — запись в локальный Qdrant) |
| повторный запуск без изменений | 0.2 с, 0 векторизаций |
| изменился один документ (34 chunks) | 1 с, переиндексирован только он |

Индекс на диске занимает 57 MB.

**Почему Qdrant**

| Вариант | Плюсы | Минусы |
|---------|-------|--------|
| **Qdrant** (выбран) | фильтры по metadata (payload); локальный режим без сервера для Lab1 и официальный Docker-образ для Lab2/3 с тем же клиентом; REST/gRPC API; HNSW-индекс | в локальном режиме поиск полным перебором; для ~5–7 тыс. точек это миллисекунды |
| FAISS | очень быстрый | только библиотека: нет хранения metadata, фильтров и сервера; для Lab2/3 нужна своя обёртка |
| Chroma | простой API, фильтры по metadata | серверный режим и эксплуатация в Kubernetes менее зрелые |
| PostgreSQL + pgvector | SQL и векторы в одной БД | нужен сервер PostgreSQL уже в Lab1 |
| SQLite + перебор (как в old/) | ничего не нужно | нет векторного индекса и фильтров, JSON-векторы разбираются на каждый запрос |

### Retrieval
```text
вопрос ─► "query: " + вопрос ─► embedding ─► Qdrant (cosine, top_k, фильтры по metadata) ─► chunks + score
```
Векторы нормализованы, поэтому score — это косинусная близость. `top_k` задаётся в `retrieval.top_k`. Фильтр по metadata, например `--section concepts/workloads/pods`, применяется внутри Qdrant до отбора top-K. Поиск занимает около 30 мс на вопрос.

### Reranking и фильтрация
```text
вопрос ─► vector search: top-N кандидатов (N = 20)
       ─► similarity threshold (0.78)       — отсекает слабые совпадения и вопросы вне базы
       ─► дедупликация (Jaccard ≥ 0.8)      — почти одинаковые тексты с разных страниц
       ─► min length (50 символов)          — «See X for more information.»
       ─► reranker bge-reranker-v2-m3       — cross-encoder заново оценивает пары (вопрос, chunk)
       ─► порог rerank_score (0.1)
       ─► не больше M chunks со страницы (выкл.)
       ─► top-K (5) ─► LLM
```
Пустой результат означает, что релевантного контекста нет. Генерация в этом случае ответит, что информации недостаточно.

**Зачем reranker.** Embedding-модель (bi-encoder) кодирует вопрос и chunk по отдельности: это быстро, но грубо. Cross-encoder читает вопрос и chunk вместе и точнее оценивает, отвечает ли текст на вопрос. Он медленнее, поэтому применяется только к 20 кандидатам. `BAAI/bge-reranker-v2-m3`: 568M параметров, мультиязычный (ru-вопрос, en-текст), MIT, score 0..1.

| Фильтр | Параметр | Почему такое начальное значение |
|--------|----------|---------------------------------|
| similarity threshold | `filters.score_threshold: 0.78` | у e5 релевантное ≈ 0.82–0.88, вне базы ≈ 0.75 |
| дедупликация | `filters.dedup_threshold: 0.8` | Jaccard по 3-словным шинглам; ловит почти-дубли, разные chunks одной темы не трогает |
| минимальная длина | `filters.min_chars: 50` | 85 chunks короче 50 символов, почти все — «See X for more information.» |
| порог reranker | `reranker.min_score: 0.1` | вне базы ≤ 0.006, релевантное ≥ 0.8 |
| лимит на документ | `filters.max_per_document: 0` | выключен; включается, если контекст забивает одна страница |
| metadata | `filters.metadata: {}`, `--section` | точный фильтр Qdrant по полям payload |

Все пороги начальные, их подбирает эксперимент E7.

Первое сравнение на 9 вопросах, top-3; полное сравнение — в E6:

| Вопрос | Без reranker | С reranker |
|--------|--------------|------------|
| Как ограничить потребление памяти контейнером? | Motivation for memory requests…, Exceed…, If you do not specify… | **Exceed a Container's memory limit** (0.955), **Specify a memory request and a memory limit** (0.918), If you do not specify… |
| Как масштабировать Deployment до трёх реплик? | Scaling a Deployment (tutorial), Updating a Deployment, Proportional scaling | Updating a Deployment (0.988), Proportional scaling, Scaling a Deployment |
| Что такое Pod?, ConfigMap vs Secret, Deployment vs StatefulSet, readiness probe | нужные страницы в top-3 | те же страницы, порядок уточнён |
| Какой порт по умолчанию слушает kubelet? | нерелевантно | в top-3 нерелевантно, но в top-5 есть «API Server Bypass Risks > The kubelet API» с ответом (порт 10250) |
| Как приготовить борщ? / Чемпионат мира 2018 | **пусто** (отсечено порогом) | **пусто**; rerank_score был бы 0.0001 / 0.006 |

Задержка: поиск без reranker ~30 мс, с reranker ~200–300 мс на GPU.

Особенность Qdrant в локальном режиме (qdrant-client 1.19): если удалить коллекцию и сразу создать её с тем же именем, старые точки возвращаются. Поэтому `--rebuild` очищает точки, а не пересоздаёт коллекцию. На этом есть тест.

### Генерация ответа
```text
chunks (top-K) ─┬─ пусто ──────────────────────────────► «В документации недостаточно информации…» (LLM не вызывается)
                └─ [1] heading / url / текст, [2] … ─► LLM (Ollama): system prompt + контекст + вопрос
                                                       ─► ответ со ссылками [n] ─► источники = процитированные chunks
```

LLM получает system prompt (`configs/prompts.yaml`) и сообщение пользователя: пронумерованный контекст с заголовком и URL каждого chunk, затем вопрос.

**Защита от галлюцинаций** работает на трёх уровнях:
1. **Фильтры поиска.** Порог близости и порог reranker отсекают нерелевантный контекст. Если не осталось ничего, LLM не вызывается и система сразу отвечает отказом.
2. **Промпт `strict`.** Отвечать только по контексту, ставить ссылку `[n]` после каждого утверждения, не придумывать команды и значения полей. Если ответа в контексте нет, отвечать ровно фразой из `generation.no_context_answer`.
3. **Детектор отказа.** Ответ с фразой `generation.refusal_marker` помечается как отказ, источники к нему не прикладываются.

Источники — страницы, на которые модель сослалась через `[n]`. Несколько chunks одной страницы дают один источник. Если ссылок нет совсем, источниками считается весь контекст.

**LLM** (локально через Ollama, бесплатно):

| Ключ в config | Модель | Размер | Режим | Назначение |
|---------------|--------|-------:|-------|-----------|
| `qwen3-8b` (основная) | `qwen3:8b` | 5.2 GB | без рассуждений (`think: false`) | быстрая, хороший русский |
| `qwen3-8b-think` | `qwen3:8b` | — | с рассуждениями (`think: true`) | второй режим для E8 |
| `gemma3-12b` | `gemma3:12b` | 8.1 GB | — | вторая модель для E8 |
| `gemma3-12b-judge` | `gemma3:12b` | — | `temperature: 0` | LLM-судья в evaluation |

Каждая модель помещается в 12 GB VRAM. Но `gemma3:12b` вместе с embedding-моделью и reranker заполняет память почти целиком (11.3 GB). В таком прогоне судья тратил ≈23 с на ответ, а без эмбеддера и reranker в памяти — 6–16 с. Вероятная причина — выгрузка части видеопамяти в общую память Windows. Поэтому evaluation выгружает эмбеддер и reranker после поиска, до вызова LLM (`release_gpu_memory`). Итог E8: основная — `qwen3:8b` без рассуждений. `temperature: 0.1` и фиксированный `seed: 42` делают ответы воспроизводимыми для экспериментов.

**Промпты** для E9:

| Вариант | Суть |
|---------|------|
| `strict` (основной) | только контекст, ссылки `[n]`, точная фраза отказа, не выдумывать команды и поля |
| `basic` | одна строка «ответь по контексту», без правил |

Первое наблюдение. На вопросе вне корпуса («Сколько стоит кластер в Google Cloud?», reranker выключен, LLM получает нерелевантный контекст):
- `strict` дал точную фразу отказа: отказ распознан, источников нет;
- `basic` написал «нет информации» своими словами: отказ не распознан, к ответу приложены 4 нерелевантные ссылки.

### Evaluation

**Набор вопросов** — `experiments/eval_set.yaml`, 40 вопросов на русском:

| Тип | Кол-во | Пример |
|-----|-------:|--------|
| фактологические (`factual`) | 10 | Какой тип Service создаётся, если тип не указан явно? |
| поиск конкретики (`specific`) | 8 | Какой командой откатить Deployment на предыдущую ревизию? |
| по нескольким документам (`multi_doc`) | 7 | Чем Job отличается от CronJob? |
| понимание контекста (`context`) | 7 | Что происходит, если readiness probe не проходит? |
| нет в базе (`no_answer`) | 8 | Какое максимальное число узлов поддерживает кластер? (есть только в разделе setup, не вошедшем в корпус) |

У каждого вопроса есть:
- эталонный ответ;
- релевантные документы. `match: any` — достаточно любого из них, `match: all` — нужны все (вопросы по нескольким документам);
- фразы-доказательства (`evidence`) из документации.

Тест `tests/test_eval_set.py` проверяет набор по корпусу: все документы существуют, каждая evidence-фраза есть в релевантных документах, а для `no_answer` фраз из `absent` нет нигде в корпусе. Если документация обновится, тест покажет, какой эталон устарел.

Релевантность размечена **на уровне документов**, а не chunks. Так одна и та же разметка годится для любой стратегии chunking: эксперименты E1–E3 сравнивают разные chunks на одних эталонах.

**Метрики и почему они**

| Метрика | Что показывает | Почему нужна |
|---------|----------------|--------------|
| Hit@K | в top-K есть chunk из релевантного документа | необходимое условие правильного ответа: без нужного документа LLM ответить не сможет |
| Recall@K | доля релевантных документов в top-K | для `multi_doc` важно найти все документы, а не один |
| MRR | 1 / позиция первого релевантного chunk | насколько высоко нужное; определяет, какой K достаточен (E5) и что даёт reranker (E6) |
| Precision@K | доля релевантных среди возвращённых chunks | чистота контекста: шум удлиняет промпт и провоцирует галлюцинации |
| Correctness (LLM-судья, 0/1/2) | ответ совпадает по смыслу с эталоном | итоговое качество ответа |
| Faithfulness (LLM-судья, 0/1/2) | все утверждения ответа подтверждаются контекстом | главный показатель галлюцинаций |
| Верные отказы | доля отказов на вопросах `no_answer` | требование «сообщить, что информации недостаточно» |
| Ложные отказы | доля отказов на вопросах с ответом | обратная сторона строгих порогов и промпта |
| Citation hit | источники ответа включают релевантный документ | ссылки ведут туда, где действительно есть ответ |

Метрики retrieval считаются один раз по списку top-20 для K = 1, 3, 5, 10, 20, по префиксу этого списка. LLM получает первые `retrieval.top_k` chunks.

**LLM-as-a-Judge.** Судья — `gemma3:12b` с `temperature: 0`: другая и более крупная модель, чем генератор `qwen3:8b`, что снижает «самолюбование» модели. Он один для всех экспериментов, поэтому оценки сравнимы.

Судья делает два независимых вызова (`src/evaluation/judge.py`, промпты `judge_correctness` и `judge_faithfulness`):

| Вызов | Видит | Что возвращает | Как получается оценка |
|-------|-------|----------------|-----------------------|
| correctness | вопрос, эталон, ответ | 1–4 ключевых факта эталона со статусом «есть / частично / нет / противоречит» | правилом: противоречие → 0, все факты есть → 2, что-то верно → 1, иначе 0 |
| faithfulness | вопрос, контекст, ответ | утверждения ответа, к каждому — номер подтверждающего фрагмента и статус «подтверждено / не подтверждено / противоречит» | все подтверждены → 2, иначе оценка модели 0/1 по важности неподтверждённого; доля подтверждённых — `claim_support` |

Почему так, а не один вызов с оценкой:
- в одном вызове с длинным контекстом судья отмечал факты эталона как «есть», потому что видел их в контексте, а не в ответе: на калибровке ответ «данные кластера хранит kube-proxy» получил 2. Поэтому correctness оценивается без контекста;
- просьба «поставь оценку» без разбора давала 2 почти всем ответам. Разбор по фактам и правило делают оценку объяснимой: в `report.md` видно, какой факт судья счёл пропущенным или неверным;
- цитата-подтверждение заставляет судью искать утверждение в контексте, а не угадывать. `claim_support` — та же метрика, что faithfulness в RAGAS.

Остальное:
- ответ судьи ограничен JSON-схемой (structured output Ollama), шкала 0/1/2: небольшой модели проще стабильно различать «неверно / частично / верно», чем 10 градаций;
- отказы судья не оценивает. Отказ на `no_answer` — верно, отказ на вопрос с ответом — неверно;
- прогон идёт в три прохода (поиск → генерация → судья), чтобы генератор и судья не вытесняли друг друга из 12 GB видеопамяти на каждом вопросе.

**Проверка самого судьи:**
- калибровка (`src/evaluation/calibration.py`): 9 заготовленных ответов с известной оценкой на реальном контексте: верный, неверное число, не тот компонент, обратный смысл, выдуманная деталь, неполный, уклончивый;
- экспертная оценка (`experiments/manual_review.yaml`): 32 ответа baseline размечены вручную по той же шкале; `src/evaluation/agreement.py` считает совпадение с судьёй (раздел 10).

Почему не RAGAS как библиотека: по умолчанию она рассчитана на OpenAI и тяжёлые зависимости. Свой судья на локальной модели прозрачен и воспроизводим, а faithfulness считает по той же схеме (утверждения → проверка по контексту).

### Наблюдаемость: Langfuse
Метрики evaluation отвечают на вопрос «насколько хорошо», но не «почему именно такой ответ». Поэтому каждый запуск RAG записывается в [Langfuse](https://langfuse.com) — open-source платформу трассировки LLM-приложений. Сервер поднимается локально (`langfuse/docker-compose.yml`, Langfuse v4), данные никуда не уходят.

Что попадает в Langfuse (`src/tracing.py`, `src/evaluation/langfuse_run.py`):

```text
trace rag-ask  (вопрос → ответ, источники, отказ, время поиска и генерации)
├── retrieval        retriever   запрос, итоговые top-K chunks со score, счётчики шагов
│   ├── vector-search            20 кандидатов: заголовок, url, cosine score, начало текста
│   ├── filters                  сколько осталось после порога, дублей и длины
│   └── rerank                   модель reranker, кандидаты с rerank_score
└── ollama-chat      generation  модель и параметры (temperature, num_ctx, seed, think),
                                 system + user промпт с контекстом, ответ, токены, время
```

Прогон evaluation:
- **session** `eval-<имя прогона>` — все вопросы прогона вместе;
- **trace на вопрос**: три прохода (поиск → генерация → судья) попадают в один trace. Внутри — те же шаги, что выше, и два вызова судьи (`judge-correctness`, `judge-faithfulness`) с его разбором фактов и утверждений;
- **scores** trace: `hit@5`, `recall@5`, `precision@5`, `reciprocal_rank`, `refused`, `refusal_correct`, `citation_hit`, `correctness`, `faithfulness`, `claim_support` (с комментарием судьи). Scores session — итоги прогона, те же числа, что в `summary.json`;
- **dataset** `k8s-docs-eval` — вопросы набора с эталонами (повторный прогон обновляет, а не дублирует), прогон — **experiment** с тем же именем. Прогоны экспериментов (например, `E6/с_reranker` и `E6/без_reranker`) сравниваются бок о бок по средним scores и по каждому вопросу.

Зачем:
- разбор ошибки за минуту: на «провальном» вопросе видно, на каком шаге пропал нужный документ (не нашёлся, отсечён порогом, опущен reranker'ом) или модель проигнорировала контекст;
- видна цена каждого шага: время поиска, reranker и LLM, токены промпта и ответа;
- эксперименты сравниваются не только итоговыми числами, но и по конкретным вопросам.

Трассировка не обязательна. Без ключей в `.env`, без запущенного сервера или при `langfuse.enabled: false` Tracer пустой: пайплайн и тесты работают как раньше, при недоступном сервере — одно предупреждение в логе. Тексты chunks в trace обрезаются до `langfuse.preview_chars`; полный контекст есть в промпте generation.

Почему прогон связан с experiment своим циклом, а не `Langfuse.run_experiment`: run_experiment выполняет задачу целиком на каждом вопросе (и параллельно), а наш прогон идёт в три прохода, чтобы генератор и судья не вытесняли друг друга из видеопамяти. Поэтому связь делается тем же способом, что внутри SDK: item run в dataset и атрибуты experiment на spans вопроса.

| Вариант | Почему выбран / не выбран |
|---------|---------------------------|
| **Langfuse** (выбран) | open-source, self-hosted одной командой Docker Compose; traces, sessions, scores, datasets и сравнение experiments в одном UI; SDK на OpenTelemetry |
| LangSmith | облачный сервис LangChain; self-hosted — только в платной версии |
| Arize Phoenix | трассировка есть, но datasets и сравнение прогонов слабее |
| MLflow Tracing | рассчитан на эксперименты ML-моделей; UI для пошаговых traces LLM беднее |
| только логи и `report.md` | нет дерева шагов и времени по шагам; прогоны сравниваются вручную по файлам |

## 3. Используемые технологии

| Компонент | Технология |
|-----------|-----------|
| Язык | Python 3.12+ |
| Сбор данных | GitHub REST API, `requests` с ретраями |
| Конфигурация | YAML (`PyYAML`), `.env` (`python-dotenv`) |
| Embeddings | `sentence-transformers` + PyTorch (CUDA) |
| Vector DB | Qdrant (`qdrant-client`, локальный режим) |
| Reranker | `sentence-transformers` CrossEncoder, `BAAI/bge-reranker-v2-m3` |
| LLM | Ollama (HTTP API `/api/chat`), `qwen3:8b`, `gemma3:12b` |
| Наблюдаемость | Langfuse v4 self-hosted (Docker Compose: web, worker, PostgreSQL, ClickHouse, Redis, MinIO), SDK `langfuse` (OpenTelemetry) |
| Тесты | `pytest` |

## 4. Установка
Нужен Python 3.12+ (проверено на 3.14). `requirements.txt` ставит PyTorch с CUDA 12.8 (~2.5 ГБ). Без GPU убери из него строку `--extra-index-url`: поставится CPU-сборка, индексация будет медленнее.
```bash
cd new/lab1
python -m venv .venv
.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env          # необязательно: GITHUB_TOKEN
```

Для генерации нужна [Ollama](https://ollama.com/download) (проверено на 0.40) и модели:
```bash
ollama pull qwen3:8b
ollama pull gemma3:12b   # LLM-судья в evaluation и вторая модель в E8
```

Langfuse (необязательно; нужен Docker, ≈2 ГБ образов и ≈1.5 ГБ памяти):
```bash
python langfuse/make_env.py                          # случайные пароли → langfuse/.env, ключи API → .env
docker compose -f langfuse/docker-compose.yml up -d  # после скачивания образов готов за ≈30 с
```
UI: http://localhost:3000. Вход: `admin@lab1.local` и пароль `LANGFUSE_INIT_USER_PASSWORD` из `langfuse/.env`. Организация, проект `lab1-rag` и его ключи API создаются при первом запуске сами, регистрация посторонних выключена. Остановить: `docker compose -f langfuse/docker-compose.yml stop` (данные остаются в томах).

## 5. Запуск

### Быстрый старт: от источника до ответа
```bash
python -m src.ingest                                                       # сбор → очистка и chunking → индекс
python -m src.generation "Как ограничить потребление памяти контейнером?"  # вопрос → ответ с источниками
```
`src.ingest` по очереди запускает три шага ниже с параметрами из config. Первый запуск скачивает 452 страницы и строит индекс (≈3 мин вместе с загрузкой модели). Повторный — секунды: каждый шаг инкрементальный. Код выхода: 0 — успех, 1 — ошибка шага, 2 — часть страниц не скачана (индекс построен по остальным).

Шаги по отдельности:

### Сбор данных
```bash
python -m src.grabber             # синхронизировать корпус с источником
python -m src.grabber --dry-run   # только показать, что изменится
python -m src.grabber --limit 10  # скачать не больше 10 документов (отладка)
```
Результат: `data/raw/`, `data/manifest.json`, лог `logs/grabber.log`.
Коды выхода: `0` — успех, `1` — источник недоступен, `2` — часть документов не получена (повторный запуск докачает их).

### Подготовка текста
```bash
python -m src.preprocessing                                     # параметры из config
python -m src.preprocessing --strategy fixed --chunk-size 500 --overlap 100
python -m src.preprocessing --strategy paragraph --no-heading
```
Результат: `data/processed/documents.jsonl`, `data/processed/chunks.jsonl`, лог `logs/preprocessing.log`.

### Индексация
```bash
python -m src.embeddings                          # модель и chunking из config; повторно — только изменённые документы
python -m src.embeddings --model bge-m3           # другая модель из embeddings.models
python -m src.embeddings --strategy fixed --chunk-size 500 --overlap 100
python -m src.embeddings --rebuild                # пересоздать коллекцию
```
Первый запуск скачивает модель с Hugging Face (~1.1 ГБ для e5-base) в кэш `~/.cache/huggingface`.

### Поиск
```bash
python -m src.retrieval "Что такое Pod?"
python -m src.retrieval "Как ограничить память контейнера?" --top-k 10
python -m src.retrieval "Что такое Pod?" --section concepts/workloads/pods
python -m src.retrieval "Что такое Pod?" --no-rerank   # без reranker
```
Вывод показывает, сколько chunks осталось после каждого шага, например `найдено 20 → порог 20 → без дублей 17 → длина 17 → reranker 17 → итог 5`. Первый запуск с reranker скачивает модель (~2.3 ГБ).

### Оценка качества
```bash
python -m src.evaluation --name baseline                       # retrieval + генерация + судья (~6 мин)
python -m src.evaluation --name fast --retrieval-only          # только метрики retrieval (~20 с)
python -m src.evaluation --name no-rerank --no-rerank --no-judge
python -m src.evaluation --name check --only f01,m02,n03      # отдельные вопросы
python -m src.evaluation --rejudge baseline --name rejudged    # только судья на сохранённых ответах (~5 мин)
python -m src.evaluation.calibration                           # калибровка судьи на 9 заготовленных ответах (~1 мин)
python -m src.evaluation.agreement --name baseline             # согласие судьи с экспертной оценкой
```
Результаты: `experiments/results/<name>/report.md` (сводка и разбор каждого вопроса), `summary.json`, `results.jsonl` (вместе с ответами и контекстом LLM, поэтому судью можно перезапустить без поиска и генерации), `agreement.json`; калибровка — `experiments/results/calibration.json`.

### Эксперименты
```bash
python -m src.evaluation.experiments --list          # список экспериментов
python -m src.evaluation.experiments                 # все эксперименты поиска E1–E7 (без LLM, ≈15–40 мин)
python -m src.evaluation.experiments --only E8,E9    # эксперименты с LLM и судьёй (≈30 мин)
```
Недостающие индексы Qdrant строятся автоматически. Одинаковый вариант в разных экспериментах прогоняется один раз. Итог — `experiments/results/<E>/comparison.md`.

### Langfuse: трассировка и сравнение прогонов
Когда Langfuse запущен (раздел 4), трассировка включается сама, команды те же:
```bash
python -m src.generation "Как ограничить потребление памяти контейнером?"   # trace вопроса, ссылка в конце вывода
python -m src.evaluation --name baseline                                     # session, 40 trace, scores, experiment
python -m src.evaluation.experiments --only E6                               # два experiment: с reranker и без
```
Где смотреть (http://localhost:3000, проект `lab1-rag`):
- **Tracing** — каждый вопрос: дерево шагов, время, промпт и ответ LLM, токены, scores;
- **Sessions** — прогон evaluation целиком (`eval-<имя прогона>`);
- **Experiments** — прогоны рядом со средними scores (hit@5, recall@5, reciprocal_rank, correctness, faithfulness…); внутри прогона — результат по каждому вопросу и сравнение с другим прогоном;
- **Datasets → k8s-docs-eval** — вопросы с эталонами и их прогоны;
- **Scores**, **Dashboards** — распределение оценок, задержки и токены.

Как не ждать полный прогон:
- эксперименты с поиском (E1–E7) — с `--retrieval-only`: без LLM, секунды на прогон;
- настройка промптов судьи — сначала калибровка, затем `--rejudge`: генерация не повторяется;
- отладка на нескольких вопросах — `--only`.

### Вопрос → ответ (полный RAG)
```bash
python -m src.generation "Как ограничить потребление памяти контейнером?"
python -m src.generation "Чем Deployment отличается от StatefulSet?" --llm gemma3-12b
python -m src.generation "Что такое Pod?" --prompt basic --show-context
```
Выводит ответ, источники и служебную строку: шаги поиска, время, токены, признак отказа. Если Langfuse запущен, последней строкой выводится ссылка на trace этого вопроса. Первый вопрос после запуска Ollama дольше, потому что модель загружается в видеопамять.
Параметры модели и chunking (`--model`, `--strategy`, …) выбирают коллекцию, поэтому должны совпадать с теми, что использовались при индексации.

## 6. Configuration
Все параметры в `configs/config.yaml`, секреты в `.env`.

| Параметр `grabber.*` | Значение | Назначение |
|----------------------|----------|-----------|
| `repo`, `ref`, `docs_root` | `kubernetes/website`, `main`, `content/en/docs` | откуда брать документы |
| `sections` | `[concepts, tasks, tutorials]` | какие разделы входят в корпус |
| `raw_dir`, `manifest_file` | `data/raw`, `data/manifest.json` | куда сохранять |
| `timeout_s`, `max_retries`, `backoff_s` | `30`, `3`, `1.0` | устойчивость к сетевым ошибкам |
| `max_workers` | `8` | параллельные загрузки |
| `GITHUB_TOKEN` (`.env`) | — | поднимает лимит API с 60 до 5000 запросов/час |

| Параметр `chunking.*` | Значение | Назначение |
|-----------------------|----------|-----------|
| `strategy` | `heading` | `fixed` / `paragraph` / `heading` |
| `chunk_size` | `1000` | максимум символов текста chunk |
| `chunk_overlap` | `0` | перекрытие в символах (только `fixed`) |
| `include_heading` | `true` | добавлять «Title > Section» в начало chunk |

Значения `chunking.*` начальные, итоговые выбираются экспериментами E1–E3. Пути результатов задаются в `preprocessing.*`.

| Параметр | Значение | Назначение |
|----------|----------|-----------|
| `embeddings.model` | `multilingual-e5-base` | ключ активной модели из `embeddings.models` |
| `embeddings.models.<key>` | `name`, `query_prefix`, `passage_prefix`, `max_seq_length` | описание модели; новая модель добавляется только сюда |
| `embeddings.device` | `auto` | `auto` / `cuda` / `cpu` |
| `embeddings.batch_size` | `64` | размер батча при векторизации |
| `vector_store.path` | `data/qdrant` | папка локального Qdrant |
| `vector_store.collection_prefix` | `k8s` | префикс имён коллекций |
| `retrieval.top_k` | `5` | сколько chunks получает LLM (выбирается в E5) |
| `retrieval.candidates` | `20` | top-N из векторного поиска до фильтров и reranker |
| `filters.score_threshold` | `0.78` | минимальная косинусная близость; `0` — выкл |
| `filters.dedup_threshold` | `0.8` | порог почти-дублей; `1.0` — только точные; `0` — выкл |
| `filters.min_chars` | `50` | минимальная длина текста chunk без заголовка |
| `filters.max_per_document` | `0` | лимит chunks с одной страницы; `0` — без лимита |
| `filters.metadata` | `{}` | постоянный фильтр Qdrant по полям payload |
| `reranker.enabled` | `true` | включить cross-encoder |
| `reranker.model` | `BAAI/bge-reranker-v2-m3` | модель reranker |
| `reranker.min_score` | `0.1` | порог rerank_score; `0` — выкл |
| `llm.base_url` | `http://localhost:11434` | адрес Ollama |
| `llm.model` | `qwen3-8b` | ключ активной LLM из `llm.models` |
| `llm.models.<key>` | `name`, `think`, `temperature`, `num_ctx`, `seed` | описание модели и режима |
| `llm.timeout_s` | `180` | таймаут ответа LLM |
| `generation.prompts_file`, `generation.prompt` | `configs/prompts.yaml`, `strict` | варианты промпта и активный |
| `generation.no_context_answer` | «В документации недостаточно информации…» | ответ при пустом контексте; подставляется в промпт |
| `generation.refusal_marker` | «недостаточно информации» | по этой фразе ответ считается отказом |
| `evaluation.eval_set` | `experiments/eval_set.yaml` | набор вопросов |
| `evaluation.experiments_file` | `configs/experiments.yaml` | сетка экспериментов E1–E9 |
| `evaluation.results_dir` | `experiments/results` | куда писать прогоны |
| `evaluation.k_values` | `[1, 3, 5, 10, 20]` | K для метрик retrieval |
| `evaluation.judge_llm` | `gemma3-12b-judge` | LLM-судья (ключ из `llm.models`) |
| `evaluation.judge_prompts` | `judge_correctness`, `judge_faithfulness` | промпты судьи из `configs/prompts.yaml` |
| `evaluation.langfuse_dataset` | `k8s-docs-eval` | dataset вопросов в Langfuse; прогон — experiment |
| `evaluation.log_file` | `logs/evaluation.log` | лог прогонов |
| `langfuse.enabled` | `true` | трассировка в Langfuse; без ключей в `.env` выключается сама |
| `langfuse.base_url` | `http://localhost:3000` | адрес self-hosted Langfuse |
| `langfuse.environment` | `lab1` | окружение в Langfuse (фильтр в UI) |
| `langfuse.sample_rate` | `1.0` | доля трассируемых запросов |
| `langfuse.timeout_s` | `5` | таймаут запросов к Langfuse |
| `langfuse.preview_chars` | `300` | сколько символов chunk записывать в trace |
| `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` (`.env`) | — | ключи API проекта; заполняет `langfuse/make_env.py`, пароли сервера — в `langfuse/.env` |

## 7. API
HTTP API в Lab1 нет: система — набор CLI-модулей и Python-пакет `src`. HTTP API с OpenAPI появляется в Lab2, где эти модули становятся сервисами.

| Команда | Что делает | Коды выхода |
|---------|------------|-------------|
| `python -m src.ingest` | grabber → preprocessing → embeddings | 0 / 1 / 2 (часть страниц не скачана) |
| `python -m src.grabber [--dry-run] [--limit N]` | синхронизация корпуса с GitHub | 0 / 1 источник недоступен / 2 |
| `python -m src.preprocessing [chunking]` | очистка, нормализация, chunks | 0 / 1 нет данных |
| `python -m src.embeddings [--model] [chunking] [--rebuild]` | индекс Qdrant (инкрементально) | 0 / 1 |
| `python -m src.retrieval "вопрос" [--no-rerank] [--section]` | только поиск: chunks, scores, шаги фильтрации | 0 / 1 |
| `python -m src.generation "вопрос" [--llm] [--prompt]` | полный RAG: ответ и источники | 0 / 1 |
| `python -m src.evaluation [--name] [--retrieval-only] [--rejudge]` | оценка на наборе вопросов | 0 / 1 |
| `python -m src.evaluation.experiments [--only E1,…]` | эксперименты E1–E9 | 0 / 1 |

`chunking` — общие флаги `--strategy`, `--chunk-size`, `--overlap`, `--no-heading`.

Из Python:
```python
from src.config import load_config
from src.factory import build_rag

rag, client = build_rag(load_config())          # параметры из configs/config.yaml; переопределения — аргументами
try:
    result = rag.ask("Что такое Pod?")
    print(result.answer.text)                   # ответ со ссылками [n]
    print(result.answer.sources)                # [{"n", "title", "heading", "url", "document_id"}]
    print(result.answer.refused, result.stages) # признак отказа; сколько chunks осталось после каждого шага
    print(result.trace_id)                      # trace в Langfuse; None, если трассировка выключена
finally:
    client.close()                              # Qdrant в локальном режиме держит блокировку папки
```

## 8. Примеры использования

### Ответы полного RAG (`qwen3:8b`, промпт `strict`)

```text
Вопрос: Как ограничить потребление памяти контейнером?

Ответ:
Чтобы ограничить потребление памяти контейнером, укажите `resources.limits.memory` в манифесте
контейнера [2]. Это установит верхнюю границу памяти, которую контейнер может использовать. Если
контейнер превысит этот лимит, ядро может завершить его выполнение из-за нехватки памяти [4]. Также
можно использовать `resources.requests.memory` для указания минимального объема памяти […] [2].

Источники:
- [2] Assign Memory Resources to Containers and Pods > Specify a memory request and a memory limit
      — https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/
- [4] Resource Management for Pods and Containers > Requests and limits
      — https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/

[поиск 0.46 с: 20 → 20 → 17 → 17 → rerank 10 → 5; LLM qwen3:8b: 5.2 с, 1326 + 125 токенов; отказ: нет]
```

| Вопрос | Результат |
|--------|-----------|
| Что такое Pod? | определение со ссылками на Pods и учебник «Viewing Pods and Nodes» |
| Какой порт по умолчанию слушает kubelet? | «10250 [5]»; проверено: в «API Server Bypass Risks» сказано «typically exposed on TCP port 10250» |
| Чем Deployment отличается от StatefulSet? (`gemma3-12b`) | stateless / уникальная идентичность и хранилище / упорядоченный rollout, 3 источника |
| Как приготовить борщ? | отказ; LLM не вызывалась: фильтры отсекли весь контекст |
| Сколько стоит управляемый кластер в Google Cloud? | отказ: reranker отсёк все 19 кандидатов |
| то же с `--no-rerank` | контекст нерелевантный, отказ дала сама модель (2.6 с, 16 токенов ответа) |

Задержка: поиск 0.2–0.6 с, генерация `qwen3:8b` 3–6 с; с `think: true` ~13 с. Первый вызов после запуска Ollama дольше из-за загрузки модели.

### Только поиск

Поиск по русским вопросам. Это проверка работоспособности, а не оценка качества: оценка — в evaluation.

| Вопрос | Top-1 (score) |
|--------|---------------|
| Что такое Pod? | Pods (0.840) |
| Как ограничить потребление памяти контейнером? | Assign Memory Resources to Containers and Pods (0.845) |
| Чем Deployment отличается от StatefulSet? | Workload Management (0.877), затем StatefulSets |
| Как настроить readiness probe? | Configure Liveness, Readiness and Startup Probes > Define readiness probes (0.871) |
| Зачем нужен ConfigMap и чем он отличается от Secret? | ConfigMaps (0.863), затем Secrets (0.860) |
| Как масштабировать Deployment до трёх реплик? | Running Multiple Instances of Your App > Scaling a Deployment (0.859) |
| Как приготовить борщ? (вне базы) | без фильтров: нерелевантный chunk (0.752); с порогом 0.78: пустой результат |

Score у e5 сжат в диапазон 0.7–0.9. Порог `0.2` из old/ пропустил бы всё, поэтому порог и reranker настроены отдельно (раздел 2, «Reranking и фильтрация»).

## 9. Тестирование
```bash
pytest          # 118 тестов, ≈2 с: без сети, GPU, Ollama и Langfuse (всё подменено заглушками);
                # сверка набора вопросов с корпусом пропускается, пока корпус не собран
```
Установка из `requirements.txt` проверена в чистом venv (Python 3.14): `pip check` без ошибок, все тесты проходят.

`tests/test_grabber.py` проверяет grabber без сети, на подставном источнике:
- первый запуск сохраняет документы и metadata;
- повторный ничего не скачивает и не создаёт дублей;
- изменённый документ перекачивается, удалённый удаляется;
- сбой одного файла не останавливает остальные и сохраняет старую версию;
- повреждённый файл отклоняется;
- дубль содержимого пропускается, пропавший локальный файл восстанавливается;
- `--dry-run` ничего не пишет;
- ссылки строятся правильно, битый front matter не ломает разбор.

`tests/test_cleaning.py`:
- каждое правило очистки из таблицы раздела 2;
- защита кода и плейсхолдеров `<pod-name>`;
- HTML-таблицы;
- нормализация unicode, пробелов и переносов.

`tests/test_chunking.py`:
- размеры chunks и отсутствие разрывов слов;
- overlap;
- путь заголовков; блок кода не делится пустой строкой;
- по одной секции на chunk в `heading`; абзацы не режутся в `paragraph`;
- перенос заголовка к своему тексту;
- metadata и уникальные `chunk_id`.

`tests/test_retrieval.py` работает без сети и GPU: вместо модели «мешок слов», Qdrant в памяти. Проверяет:
- префиксы `query:` / `passage:`;
- поиск находит релевантный chunk с metadata;
- повторная индексация ничего не векторизует;
- изменённый документ заменяет все свои chunks, удалённый пропадает из индекса;
- `top_k` и фильтры по metadata;
- детерминированные ID точек и имя коллекции.

`tests/test_filters.py`, вместо reranker — оценка по пересечению слов. Проверяет:
- каждый фильтр (порог, длина без заголовка, почти-дубли, лимит на документ);
- reranker переупорядочивает кандидатов;
- конвейер целиком: N кандидатов, слияние фильтров metadata, счётчики шагов, top-K;
- режим без reranker;
- пустой результат для вопроса вне базы.

`tests/test_generation.py`, вместо LLM — заглушка, вместо HTTP — подставная сессия. Проверяет:
- пустой контекст даёт отказ без вызова LLM;
- формат пронумерованного контекста;
- источники только из ссылок `[n]`, по одному на страницу, номера вне диапазона игнорируются;
- отказ модели распознаётся, источников у него нет;
- запрос к Ollama: `think` передаётся только моделям с рассуждениями, options и разбор токенов;
- ошибки Ollama: модель не скачана, 500, Ollama не запущена, таймаут;
- оба промпта из `configs/prompts.yaml`;
- `RAG.ask` целиком.

`tests/test_eval_set.py` проверяет набор вопросов по корпусу (см. раздел 2, Evaluation).

`tests/test_ingest.py` проверяет порядок шагов `src.ingest` и коды выхода: частичная загрузка не останавливает индексацию, ошибка источника — останавливает.

`tests/test_experiments.py` проверяет сетку `configs/experiments.yaml` (допустимые ключи, существующие модели и стратегии), подстановку параметров baseline и таблицу сравнения.

`tests/test_evaluation.py` проверяет:
- метрики Hit/Recall (any/all)/Precision/RR;
- три прохода прогона на заглушках: метрики только для вопросов с ответом, отказ без вызова LLM, citation hit;
- что судья не оценивает отказы, а некорректный JSON судьи не роняет прогон;
- correctness выводится из статусов фактов (противоречие → 0), faithfulness = 2, если у всех утверждений есть цитата;
- судья вызывается дважды: correctness без контекста, faithfulness без эталона;
- сохранённый прогон перезапускается судьёй без генерации (`--rejudge`);
- согласие с экспертной разметкой и корректность самой разметки;
- сводку по типам и отчёт.

`tests/test_tracing.py`: вместо Langfuse — заглушка клиента, которая повторяет вложенность наблюдений. Проверяет:
- без ключей или при `enabled: false` трассировка выключена, пустой Tracer ничего не делает;
- trace `rag-ask`: шаги retrieval (vector-search → filters → rerank), generation с моделью, параметрами, промптом и токенами; отказ без контекста — без generation;
- прогон evaluation: три прохода вопроса в одном trace, session и имена в ASCII, шаги судьи, scores вопросов и прогона, items dataset и привязка trace к experiment на всех проходах.
- сбой API Langfuse посреди прогона не роняет evaluation: traces пишутся дальше, без experiment.

## 10. Результаты экспериментов

Как воспроизвести: `python -m src.evaluation.experiments` (все эксперименты поиска: первый запуск ≈40 мин, из них ≈25 мин — построение 13 индексов, включая `bge-m3` ≈13 мин; повторно ≈15 мин) или `--only E1,E6`. Сетка вариантов — `configs/experiments.yaml`; таблицы — `experiments/results/<E>/comparison.md`, разбор по вопросам — в папке каждого варианта.

**Как читать.** Метрики считаются на 32 вопросах с ответом и 8 без ответа, поэтому один вопрос — это ≈0.03 в Hit/Recall. Разница меньше 0.05 — это 1–2 вопроса, и её не стоит считать доказанной. Порядок сравнения:
1. Recall@5 — LLM получает 5 chunks;
2. MRR — насколько высоко нужный документ;
3. при равенстве — стоимость: число chunks, время поиска, сложность.

Baseline для всех экспериментов: `heading`, 1000 символов, `multilingual-e5-base`, reranker, cos ≥ 0.78, rerank ≥ 0.1, top-5. В каждом эксперименте меняется один параметр.

### Baseline: полный прогон с генерацией и судьёй

`python -m src.evaluation --name baseline`, генератор `qwen3:8b`, промпт `strict`:

| Retrieval | | Генерация | | Судья (0..1) | |
|---|--:|---|--:|---|--:|
| Hit@5 | 0.969 | верные отказы (no_answer) | 100% | correctness (с ответом) | 0.78 |
| Recall@5 | 0.969 | ложные отказы | 0% | faithfulness (с ответом) | 0.98 |
| MRR | 0.901 | citation hit | 0.94 | claim support | 0.99 |

Единственный промах поиска — s05 (`nodeSelector`): страница `assign-pod-node.md` не попадает даже в top-20, но LLM отвечает верно по упоминаниям в соседних документах.

**Проверка судьи:**
- **калибровка** (`python -m src.evaluation.calibration`): 9 заготовленных ответов с известной оценкой. Все неверные числа, подмена компонента и обратный смысл получают 0;
- **согласие с экспертной разметкой** (`python -m src.evaluation.agreement`): 32 ответа baseline размечены вручную.

| Вариант судьи faithfulness | Калибровка C / F | Согласие C: точно (±1) | Согласие F: точно (±1) | Судья на прогон |
|---|--:|--:|--:|--:|
| цитата из контекста к каждому утверждению | 8/9, 8/9 | 0.75 (1.00) | 0.81 (0.97) | ≈850 с |
| **номер фрагмента к каждому утверждению** (текущий) | 8/9, 7/9 | 0.72–0.75 (1.00) | 0.75–0.78 (0.97) | ≈290 с |

- **Выбор:** номер фрагмента. Он втрое быстрее, а согласие с экспертом ниже на один вопрос. Цена — судья мягче: он не заметил выдуманный второстепенный флаг в калибровке и искажения в m04 и c06. Поэтому faithfulness в экспериментах — оценка сверху.
- **Шум судьи:** на тех же 40 ответах повторный запуск (`--rejudge`) меняет оценку 1–2 вопросов, например correctness 0.766 ↔ 0.781. Это ещё одна причина считать разницу меньше 0.05 незначимой.
- **Стиль судьи:** по correctness он строже эксперта (незначительную неполноту ставит «частично»), по faithfulness — мягче. Поэтому выводы делаются по разнице между вариантами при одном судье, а не по абсолютным значениям.

История настройки судьи (что не сработало):
- одна оценка «поставь 0–2» → 2 почти всем ответам;
- один вызов с контекстом и эталоном → факты эталона «находились» в контексте вместо ответа;
- список неподтверждённых утверждений без привязки к фрагментам → faithfulness совпадал с экспертом в 0.56–0.59 случаев: пересказ на русском принимался за выдумку;
- разбор по утверждениям с поиском подтверждения в контексте (как в RAGAS) → 0.75–0.81.

### E1. Стратегия chunking
- **Что:** как резать документы на chunks.
- **Почему важно:** граница chunk определяет, окажется ли ответ целиком в одном фрагменте и не смешается ли он с соседней темой.
- **Альтернативы:** `fixed` (по символам), `fixed` + overlap 200, `paragraph` (упаковка абзацев), `heading` (по разделам Markdown, длинные разделы — по абзацам). Размер у всех — 1000 символов.
- **Эксперимент:** `--only E1`, 4 индекса, остальное как в baseline.

| Вариант | Hit@1 | Recall@5 | MRR | Recall@5 multi-doc | Chunks |
|---|--:|--:|--:|--:|--:|
| fixed | 0.812 | 0.969 | 0.880 | 1.000 | 4056 |
| fixed + overlap 200 | 0.781 | 0.953 | 0.880 | 0.786 | 4884 |
| paragraph | **0.875** | **0.984** | **0.938** | 0.929 | 4679 |
| heading | 0.844 | 0.969 | 0.901 | 1.000 | 6497 |

- **Результат:** стратегии по смыслу (`paragraph`, `heading`) лучше нарезки по символам по Hit@1 и MRR: chunk не начинается с середины предложения, а путь заголовков в начале chunk помогает поиску. `paragraph` впереди `heading` на 1–2 вопроса.
- **Выбор:** см. E2 — размер проверен для обеих стратегий.

### E2. Размер chunk
- **Что:** максимальный размер chunk в символах для двух лучших стратегий из E1.
- **Почему важно:** маленький chunk точнее по смыслу, но теряет контекст; большой — наоборот. Кроме того, e5 и reranker читают не больше 512 токенов (≈2000 символов английского текста), а LLM получает 5 chunks.
- **Альтернативы:** 500 / 1000 / 1500 / 2000.
- **Эксперимент:** `--only E2`, 8 индексов (4 размера × 2 стратегии).

| Вариант | Hit@1 | Recall@5 | MRR | Recall@5 multi-doc | Chunks | Поиск, мс |
|---|--:|--:|--:|--:|--:|--:|
| heading 500 | 0.688 | 0.938 | 0.823 | 0.857 | 10851 | 183 |
| **heading 1000** | 0.844 | 0.969 | 0.901 | **1.000** | 6497 | 260 |
| heading 1500 | 0.750 | **1.000** | 0.870 | **1.000** | 5299 | 338 |
| heading 2000 | 0.812 | **1.000** | 0.901 | **1.000** | 4813 | 370 |
| paragraph 500 | 0.750 | 0.922 | 0.854 | 0.786 | 9819 | 188 |
| paragraph 1000 | **0.875** | 0.984 | **0.938** | 0.929 | 4679 | 258 |
| paragraph 1500 | 0.781 | 0.953 | 0.883 | 0.786 | 3069 | 343 |
| paragraph 2000 | 0.781 | 0.906 | 0.849 | 0.857 | 2293 | 366 |

- **Результат:**
  - 500 символов хуже у обеих стратегий: chunk без соседних абзацев теряет смысл, а одна страница дробится на много похожих фрагментов;
  - у `heading` с ростом размера Recall растёт до 1.0, MRR держится на 0.87–0.90. Раздел документации — цельная единица, и большой chunk просто вмещает его целиком;
  - `paragraph` лучший на 1000, но при 1500–2000 падает до Recall 0.91: абзацы разных разделов склеиваются в один chunk, и его тема размывается;
  - чем крупнее chunk, тем дольше работает reranker и длиннее промпт LLM.
- **Выбор:** `heading`, 1000 символов. Преимущество `paragraph` 1000 — 1–2 вопроса на одной точке, и при соседних размерах оно исчезает. `heading` стабилен на 1000–2000, лучше находит второй документ в multi-doc вопросах и даёт точный путь раздела для ссылок в ответе. 1500–2000 дают Recall 1.0, но удлиняют контекст LLM в 1.5–2 раза, а часть текста длиннее 512 токенов не попадает в вектор.

### E3. Overlap
- **Что:** перекрытие соседних chunks (`fixed`, 1000 символов).
- **Почему важно:** без перекрытия фраза на границе разрезается; с перекрытием растёт индекс, и в top-K попадают почти одинаковые соседи.
- **Альтернативы:** 0 / 100 / 200 / 300 символов.
- **Эксперимент:** `--only E3`, `fixed` 1000, 4 индекса.

| Overlap | Hit@1 | Recall@5 | MRR | Recall@5 multi-doc | Chunks |
|--:|--:|--:|--:|--:|--:|
| 0 | 0.812 | **0.969** | 0.880 | **1.000** | 4056 |
| 100 | 0.719 | 0.938 | 0.839 | 0.857 | 4409 |
| 200 | 0.781 | 0.953 | 0.880 | 0.786 | 4884 |
| 300 | **0.844** | 0.953 | **0.896** | 0.929 | 5493 |

- **Результат:** перекрытие не дало устойчивого выигрыша. Recall@5 у всех вариантов с overlap ниже, а для multi-doc вопросов он падает до 0.79–0.93: соседние перекрывающиеся chunks одной страницы занимают места в top-5, и второй документ не помещается. Фильтр почти-дублей их не убирает, потому что они совпадают лишь частично.
- **Выбор:** overlap 0. Стратегии `paragraph` и `heading` и так режут по границам абзацев, поэтому overlap используется только в `fixed`.

### E4. Embedding-модель
- **Что:** модель, которая переводит вопрос и chunks в векторы.
- **Почему важно:** вопросы на русском, документы на английском — нужна мультиязычная модель с общим пространством для языков.
- **Альтернативы:** `intfloat/multilingual-e5-base` (278M, 768 dim, 512 токенов) и `BAAI/bge-m3` (568M, 1024 dim, до 8192 токенов). Порог косинуса здесь выключен: он подобран под e5, а у bge-m3 другой диапазон близости.
- **Эксперимент:** `--only E4`, обе модели с reranker и без: reranker маскирует разницу между моделями, поэтому видно и «сырое» качество векторного поиска.

| Вариант | Hit@1 | Hit@5 | Recall@5 | MRR | Recall@5 multi-doc | Индексация |
|---|--:|--:|--:|--:|--:|--:|
| e5-base | 0.812 | 0.969 | 0.938 | 0.878 | 0.857 | ≈60 с |
| bge-m3 | 0.750 | **1.000** | 0.938 | 0.859 | 0.714 | ≈800 с |
| e5-base + reranker | 0.844 | 0.969 | 0.969 | 0.901 | **1.000** | ≈60 с |
| bge-m3 + reranker | **0.875** | **1.000** | **0.984** | **0.932** | 0.929 | ≈800 с |

- **Результат:** без reranker e5-base лучше по Hit@1, MRR и multi-doc. bge-m3 находит s05 в top-20, и reranker поднимает его наверх, поэтому в связке с reranker bge-m3 впереди на 1 вопрос. Цена — индексация в 13 раз дольше (6497 chunks: 13 мин против 1 мин на RTX 4070 Ti), модель вдвое больше, пороги нужно подбирать заново.
- **Выбор:** `multilingual-e5-base`. Выигрыш bge-m3 — один вопрос, а в Lab2/Lab3 сервис эмбеддингов работает в контейнере, где важны размер модели и время индексации. bge-m3 — кандидат для развёртывания на GPU.

### E5. Top-K
- **Что:** сколько chunks передавать LLM.
- **Почему важно:** мало — ответ может не попасть в контекст; много — длиннее промпт, медленнее генерация, больше шума.
- **Альтернативы:** K = 1 / 3 / 5 / 10 / 20 (метрики по одному прогону, по префиксу списка).
- **Эксперимент:** `--only E5`, один прогон с top-20.

| K | Hit@K | Recall@K | Precision@K |
|--:|--:|--:|--:|
| 1 | 0.844 | 0.750 | **0.844** |
| 3 | **0.969** | 0.922 | 0.615 |
| 5 | **0.969** | **0.969** | 0.580 |
| 10 | **0.969** | **0.969** | 0.552 |
| 20 | **0.969** | **0.969** | 0.551 |

- **Результат:** Recall выходит на максимум уже к K = 5; дальше растёт только шум (Precision падает). K = 3 теряет второй документ в multi-doc вопросах.
- **Выбор:** `retrieval.top_k: 5`.

### E6. Reranker
- **Что:** cross-encoder `bge-reranker-v2-m3` пересортировывает 20 кандидатов векторного поиска.
- **Почему важно:** bi-encoder сравнивает векторы вопроса и chunk по отдельности, а cross-encoder читает их вместе: точнее, но медленнее.
- **Альтернативы:** с reranker / без.
- **Эксперимент:** `--only E6`; пороги — как в baseline.

| Вариант | Hit@1 | Recall@5 | MRR | Recall@5 multi-doc | Нет ответа → пустой контекст | Поиск, мс |
|---|--:|--:|--:|--:|--:|--:|
| без reranker | 0.812 | 0.938 | 0.878 | 0.857 | 50% | **34** |
| с reranker | **0.844** | **0.969** | **0.901** | **1.000** | **75%** | 262 |

- **Результат:** reranker поднимает все метрики, особенно multi-doc (второй документ поднимается в top-5), и вместе со своим порогом отсекает больше вопросов вне базы. Цена — ≈230 мс на вопрос, что мало на фоне генерации (2–6 с).
- **Выбор:** reranker включён.

### E7. Пороги отсечения
- **Что:** минимальная косинусная близость (`filters.score_threshold`) и минимальный rerank score (`reranker.min_score`). Если отсечены все chunks, система отказывает без вызова LLM.
- **Почему важно:** слишком низкий порог — LLM получает мусор на вопросах вне базы; слишком высокий — ложные отказы на вопросах с ответом.
- **Альтернативы:** cos 0 / 0.75 / 0.78 / 0.80 / 0.82 (без порога reranker) и rerank 0.01 / 0.1 / 0.3 / 0.5 (без порога косинуса).
- **Эксперимент:** `--only E7`. Каждый порог проверялся отдельно, чтобы видеть его собственный эффект, плюс итоговая комбинация.

| Вариант | Recall@5 | MRR | Нет ответа → пустой контекст | Есть ответ → пустой контекст |
|---|--:|--:|--:|--:|
| без порогов | 0.969 | 0.901 | 0% | 0% |
| cos 0.75 | 0.969 | 0.901 | 12% | 0% |
| cos 0.78 | 0.969 | 0.901 | 50% | 0% |
| cos 0.80 | 0.969 | 0.885 | 50% | 0% |
| cos 0.82 | 0.906 | 0.839 | 88% | 6% (f10, s07) |
| rerank 0.01 | 0.969 | 0.901 | 75% | 0% |
| rerank 0.1 | 0.969 | 0.901 | 75% | 0% |
| rerank 0.3 | 0.969 | 0.901 | 88% | 3% (s05) |
| rerank 0.5 | 0.969 | 0.901 | 100% | 3% (s05) |
| **cos 0.78 + rerank 0.1** | 0.969 | 0.901 | 75% | 0% |

- **Результат:**
  - косинус плохо разделяет «есть ответ / нет ответа»: у e5 вопросы вне базы набирают 0.74–0.83, и уже при 0.82 отсекаются два вопроса с ответом;
  - rerank score разделяет лучше: лучший chunk вопросов вне базы получает ≤ 0.34, вопросов с найденным ответом — ≥ 0.60;
  - порог 0.3–0.5 отсекает больше вопросов вне базы, но отнимает контекст у s05, на который baseline отвечает верно.
- **Выбор:** cos 0.78 + rerank 0.1, без ложных отказов на уровне поиска. Оставшиеся 2 вопроса вне базы (n07, n08 — близкие к теме) отклоняет LLM: в baseline 100% верных отказов. Порог косинуса нужен на случай выключенного reranker (E6: без него отсекается 50%).

### E8. LLM и режим рассуждений
- **Что:** модель, которая пишет ответ по найденному контексту.
- **Почему важно:** от модели зависят точность формулировок, следование правилам промпта (ссылки, отказ) и время ответа.
- **Альтернативы:** локально через Ollama, все помещаются в 12 GB VRAM: `qwen3:8b` без рассуждений, `qwen3:8b` с thinking (рассуждает перед ответом), `gemma3:12b`.
- **Эксперимент:** `--only E8`. Контекст у всех вариантов одинаковый (тот же поиск), судья — `gemma3:12b`.

| Вариант | Верные отказы | Ложные отказы | Citation hit | Correctness | Faithfulness | Claim support | Генерация, с |
|---|--:|--:|--:|--:|--:|--:|--:|
| **qwen3:8b** | 100% | 0% | 0.938 | 0.766 | 0.969 | 0.988 | **1.6** |
| qwen3:8b + thinking | 100% | 0% | **0.969** | **0.797** | **0.984** | **0.996** | 5.1 |
| gemma3:12b | 100% | 0% | **0.969** | 0.734 | **0.984** | 0.988 | 2.4 |

Correctness по типам вопросов:

| Вариант | Факты | Конкретика | Multi-doc | Контекст |
|---|--:|--:|--:|--:|
| qwen3:8b | 0.90 | **0.88** | **0.64** | 0.57 |
| qwen3:8b + thinking | **0.95** | 0.81 | **0.64** | **0.71** |
| gemma3:12b | **0.95** | 0.81 | 0.57 | 0.50 |

- **Результат:**
  - на одинаковом контексте все три модели верно отказывают на вопросах вне базы и почти не выдумывают (faithfulness 0.97–0.98): строгий промпт удерживает их в рамках контекста;
  - разница в correctness — 1–2 вопроса. Оценки отдельных вопросов расходятся на ±1 в 14 из 32 случаев в разные стороны, явного победителя нет;
  - thinking помогает на вопросах «понимание контекста» (0.57 → 0.71), но ответ в 3 раза дольше;
  - `gemma3:12b` крупнее, но не лучше. Она же работает судьёй, и предвзятости в свою пользу не видно: её ответы оценены ниже, чем у qwen3.
- **Выбор:** `qwen3:8b` без thinking — качество в пределах шума, самый быстрый ответ (1.6 с). Thinking — опция для сложных вопросов, когда задержка не важна.

### E9. System prompt
- **Что:** инструкции для LLM.
- **Почему важно:** промпт отвечает за защиту от галлюцинаций (отказ при нехватке данных) и за ссылки на источники.
- **Альтернативы:** `strict` (только контекст, ссылка `[n]` после каждого утверждения, точная фраза отказа, не придумывать значения, кратко) и `basic` (одна фраза «ответь, используя контекст»). Оба — в `configs/prompts.yaml`.
- **Эксперимент:** `--only E9`, модель `qwen3:8b`. Вариант `strict` совпадает с E8 и не прогонялся повторно.

| Промпт | Верные отказы | Correctness | Faithfulness | Ответов со ссылками `[n]` | Длина ответа, символов | Генерация, с |
|---|--:|--:|--:|--:|--:|--:|
| **strict** | **100%** | 0.766 | **0.969** | **32 из 32** | 253 | **1.6** |
| basic | 75% | 0.766 | 0.938 | 2 из 34 | 843 | 4.0 |

- **Результат:**
  - на вопросах с ответом correctness одинаковый: правила не делают ответ умнее;
  - n01–n06 отклонены в обоих вариантах ещё фильтрами поиска, без LLM. Но на n07 (Raspberry Pi) и n08 (максимум узлов), где фильтры пропустили близкий по теме контекст, `basic` пишет развёрнутый ответ вместо отказа. Это именно та галлюцинация, от которой защищает промпт;
  - без требования ссылок ответ нельзя связать с источником: система показывает все 5 chunks. Поэтому citation hit у `basic` формально выше (0.969) и при этом ничего не значит;
  - ответы в 3.3 раза длиннее, генерация в 2.5 раза дольше.
- **Выбор:** `strict`.

### Langfuse: проверка вживую (2026-10-09)
Langfuse v4.55 в Docker Compose, SDK 4.17; RTX 4070 Ti, Ollama на той же машине.

| Что | Результат |
|-----|-----------|
| `python -m src.generation "Как ограничить потребление памяти контейнером?"` | ссылка на trace в выводе; в UI дерево: `rag-ask` 9.2 с → `retrieval` 0.73 с (`vector-search` 0.46, `filters` 0.00, `rerank` 0.27) → `ollama-chat` 8.4 с, `qwen3:8b`, 1326 + 108 токенов, промпт с контекстом и ответ |
| `--name lf-no-rerank --no-rerank --retrieval-only` (52 с) | experiment из 40 trace: hit@5 0.97, recall@5 0.94, RR 0.88 — как E6 «без reranker» |
| `--name lf-baseline` (7 мин: поиск, генерация, судья) | experiment из 40 trace, в каждом — 3 прохода и 2 вызова судьи; средние scores: hit@5 0.97, recall@5 0.97, RR 0.90, correctness 0.81, faithfulness 0.97, claim_support 0.99, citation hit 0.94, refusal_correct 40/40 |
| сравнение в Experiments | два прогона в одной таблице: reranker поднимает recall@5 с 0.94 до 0.97 и RR с 0.88 до 0.90; открыв прогон, видно, на каких вопросах |

Correctness 0.81 против 0.77 в итоговом прогоне раздела 11 при той же конфигурации: генерация и судья на GPU не полностью детерминированы даже с фиксированным seed, разница — 1–2 вопроса (раздел 11, «ограничения оценки»). Метрики поиска совпали точно.

## 11. Выводы

**Итоговая конфигурация** (`configs/config.yaml`):

| Компонент | Выбор | Эксперимент |
|-----------|-------|-------------|
| Chunking | `heading`, 1000 символов, без overlap | E1–E3 |
| Embeddings | `intfloat/multilingual-e5-base` | E4 |
| Vector DB | Qdrant (локальный режим; в Lab2/3 — сервер) | раздел 2 |
| Поиск | 20 кандидатов → фильтры → reranker → top-5 | E5, E6 |
| Пороги | cos ≥ 0.78, rerank ≥ 0.1 | E7 |
| LLM | `qwen3:8b` без thinking | E8 |
| Промпт | `strict` | E9 |

**Качество итоговой системы** на 40 вопросах:
- поиск: Hit@5 0.97, MRR 0.90;
- отказы: 100% верных на вопросах вне базы, 0% ложных;
- ответы: correctness 0.77, faithfulness 0.97 по оценке судьи;
- время: поиск ≈0.3 с, ответ ≈1.6 с на RTX 4070 Ti.

**Что показали эксперименты:**
1. Больше всего на качество влияют поиск и промпт, а не размер LLM:
   - reranker поднял Recall@5 для multi-doc вопросов с 0.86 до 1.0;
   - слишком мелкие chunks (500) снизили MRR на 0.08;
   - строгий промпт дал 100% отказов против 75%.

   Три LLM при одинаковом контексте различаются на 1–2 вопроса.
2. Защита от галлюцинаций работает в два слоя. Пороги поиска отсекают 6 из 8 вопросов вне базы ещё до LLM. Оставшиеся близкие к теме вопросы отклоняет LLM по правилу промпта. Пороги выше 0.3 по reranker начинают отнимать контекст у вопросов с ответом.
3. Слабые места:
   - вопросы на сравнение нескольких документов и на понимание контекста (correctness 0.57–0.64): ответ обычно верен, но раскрывает одну сторону сравнения;
   - промах поиска s05: термин `nodeSelector` есть в вопросе, но e5 не находит нужную страницу. Лексический поиск (BM25) или гибридный поиск закрыли бы такие случаи.
4. Ограничения оценки:
   - 40 вопросов: разница меньше 0.05 — это 1–2 вопроса, поэтому при близких результатах выбор делался по стоимости и устойчивости, а не по третьему знаку;
   - судья — тоже LLM: с экспертной разметкой он совпадает в 72–78% случаев и в ≥97% — в пределах ±1. Поэтому сравнивались варианты при одном судье, а не абсолютные значения.

**Что дальше:** в Lab2 модули `grabber`, `preprocessing`, `embeddings`, `retrieval`, `reranking`, `generation` становятся отдельными сервисами с той же конфигурацией.
