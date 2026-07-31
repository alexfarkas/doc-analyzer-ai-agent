# AGENT.md — Doc Analyzer Backend

Этот документ описывает проект `services/doc-analyzer-backend` для разработчиков и AI-агентов, которые вносят изменения в backend.

## 1) Назначение сервиса

`doc-analyzer-backend` — это FastAPI-сервис для AI-анализа документов.

Ключевые задачи:
- принимать файлы и URL как источники данных;
- запускать анализ в режиме одного агента или мультиагентного совета;
- поддерживать уточнение ответов и чат (в том числе streaming/SSE);
- считать токены и стоимость;
- (опционально) использовать RAG через ChromaDB;
- отдавать UI-конфиг ролей/моделей/назначений.

---

## 2) Технологический стек

- Python 3.14
- FastAPI + Uvicorn
- LangChain / LangGraph
- PostgreSQL (через shared-пакет `db-repository`)
- ChromaDB (через shared-пакет `rag-client`)
- OCR и парсинг документов: Tesseract, PyMuPDF, pypdf, pdfplumber, python-docx, python-pptx, openpyxl, unstructured
- Pydantic Settings для конфигурации
- Структурированное логирование

---

## 3) Точка входа и жизненный цикл

- `src/doc_analyzer_backend/main.py` — запуск Uvicorn.
- `src/doc_analyzer_backend/api/api.py` — создание `FastAPI` приложения и `lifespan`.

Что происходит в `lifespan`:
1. Инициализация логирования.
2. Инициализация `PromptRepository` (если включены DB-промпты).
3. Инициализация `ChromaDBClientFactory` (если включен RAG).
4. Создание `app.state.agent` (одиночный агент).
5. Создание `app.state.council` (мультиагентный режим).

---

## 4) Архитектура по слоям

## API-слой (`src/doc_analyzer_backend/api`)
- `api.py` — сборка приложения, middleware, router registration.
- `routers/*` — endpoint-ы, сгруппированные по доменам.
- `models/*` — Pydantic request/response схемы.
- `dependencies/dependencies.py` — DI (agent, council, app_state, session).
- `exceptions/*` — доменные ошибки и handlers.
- `utils/*` — сборка ответов, SSE-утилиты.

## Домен агента (`src/doc_analyzer_backend/agent`)
- `agent.py` — одиночный агент (analyze/clarify/chat/chat_stream).
- `council/council.py` — мультиагентный оркестратор.
- `council/stages/*` — этапы EXEC/CORRECTOR/JUDGE.
- `agent_ai_invocation/*` — сценарии вызовов LLM.
- `core/*` — граф выполнения, управление LLM-моделью.
- `context/*` — история диалога, промпты, RAG-контекст.
- `consumption_counters/*` — токены/стоимость.
- `runners/*` — запуск стадий/очередей.
- `models/*` — внутренние DTO.

## Источники данных (`src/doc_analyzer_backend/components`)
- `uploader/*` — загрузка файлов и контента по URL.
- `preview_reader/*` — предпросмотр и разбор файлов.
- `file_manager/*` — листинг, сортировка, пагинация.

## Инструменты LLM (`src/doc_analyzer_backend/tools`)
- `tools.py` — регистрация инструментов:
  - `read_document_file`
  - `read_web_page_from_url`
  - динамический RAG-tool `retrieve_document_from_vector_storage`

## Конфигурация (`src/doc_analyzer_backend/config`)
- `llm_config.py`, `rag_config.py`, `db_config.py`, `app_config.py`, `service_config.py`, `logger_config.py`, `pricing_config.py`.

## Состояние приложения (`src/doc_analyzer_backend/data`)
- `app_state_manager.py` — агрегированная статистика токенов/стоимости и доступ к ней через API.

---

## 5) Роли в мультиагентном режиме (Council)

Назначения агента (через `agent_enums.Assignment`):
- `EXEC` — базовый анализ.
- `CORRECTOR` — корректировка ответа.
- `JUDGE` — оценка и judgement.
- `POST_CORRECTOR` — пост-правка (если используется в сценарии).

`Council.create_council(...)` распределяет агентов по этим группам, затем `Council.analyze_doc(...)` запускает стадии последовательно и агрегирует consumption data.

---

## 6) API (группами)

Важно:
- Backend endpoint-ы объявлены без префикса (`/doc/analyze`).
- Во frontend через Nginx они вызываются как `/api/...`.

### 6.1 Системные

| Метод | Endpoint | Назначение |
|---|---|---|
| GET | `/health` | Проверка готовности сервиса |
| GET | `/status` | Состояние модели/инструментов/RAG |
| GET | `/config` | Конфигурация для UI |

### 6.2 Сессии

| Метод | Endpoint | Назначение |
|---|---|---|
| GET | `/sessions/current` | Получить текущую сессию |
| DELETE | `/sessions/current` | Удалить текущую сессию |

### 6.3 Источники данных

| Метод | Endpoint | Назначение |
|---|---|---|
| POST | `/upload/file` | Загрузка файла |
| POST | `/upload/from-url` | Загрузка/извлечение контента по URL |
| GET | `/files/list` | Список файлов (сортировка/фильтрация/пагинация) |
| GET | `/files/preview` | Предпросмотр файла |

### 6.4 Анализ и чат

| Метод | Endpoint | Назначение |
|---|---|---|
| POST | `/doc/analyze` | Анализ документов (обычный JSON-ответ) |
| POST | `/doc/analyze/stream` | Анализ документов со streaming (SSE) |
| POST | `/doc/clarify` | Уточнение/доработка ответа |
| POST | `/doc/chat` | Чат с агентом |
| POST | `/doc/chat/stream` | Потоковый чат (SSE) |
| POST | `/doc/history` | История сообщений |

### 6.5 Токены и стоимость

| Метод | Endpoint | Назначение |
|---|---|---|
| GET | `/tokens/total` | Суммарные токены/стоимость |
| POST | `/tokens/clear` | Сброс статистики токенов/стоимости |

---

## 7) Поток выполнения анализа (упрощенно)

1. UI отправляет `POST /doc/analyze/stream` с:
   - `resources`
   - `role`
   - `agents[]` (model + assignment)
   - опционально `limit`
2. Роутер вызывает `run_doc_analysis(...)`.
3. Если агент один — используется `Agent.analyze_doc(...)`.
4. Если агентов несколько — создается `Council`, запускаются стадии.
5. Прогресс и результаты публикуются через SSE-события:
   - `agent_start`
   - `agent_end`
   - `complete`
   - `error`
6. Токены/стоимость агрегируются и возвращаются в ответе.

---

## 8) Конфигурация (ключевые переменные окружения)

- `LLM_PROVIDER`, `LLM_MODEL`, `LLM_BASE_URL`, `LLM_API_KEY`
- `DB_URL`, `DB_ECHO`, флаги DB-prompts
- `RAG_USE_VECTOR_DB`, `RAG_HOST`, `RAG_PORT`, `RAG_COLLECTION`
- `RAG_EMBEDDING_PROVIDER`, `RAG_EMBEDDING_MODEL`, `RAG_BASE_URL`
- `LOG_PATH`, `LOG_LEVEL`, `LOG_WRITE_TO_FILE`
- `APP_DOCS_DIR` (каталог документов)

---

## 9) Локальная разработка и проверка

Из корня монорепо:
- `make dev` — запуск core-сервисов с пересборкой.
- `make test` — backend тесты.
- `make test-coverage` — тесты с coverage.
- `make lint` — `ruff` + `mypy`.
- `make format` — автоформатирование backend.

Документация API:
- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

---

## 10) Практические правила внесения изменений

1. **Сначала слой домена, потом API**: если меняется бизнес-логика, правки в `agent/*` и только затем в `api/*`.
2. **Не ломать SSE-контракт**: UI ожидает конкретные `event` и форму `data`.
3. **Сохранять совместимость схем**: изменения `api/models/*` делать аккуратно и согласованно с UI.
4. **Токены/стоимость обновлять централизованно**: использовать существующие счетчики и `app_state_manager`.
5. **RAG делать опциональным**: код должен работать при выключенном `RAG_USE_VECTOR_DB`.
6. **Следовать текущему стилю**: типизация, логирование, pydantic-модели, явные названия стадий.

---

## 11) Что важно проверить после изменений

- `/health` и `/config` отвечают корректно.
- `POST /doc/analyze/stream` отдает валидный поток SSE.
- `POST /doc/chat/stream` завершает поток маркером `[DONE]`.
- `GET /tokens/total` и `POST /tokens/clear` корректно отражают state.
- Тесты и линтеры проходят.

---

## 12) Зависимости от shared-пакетов

Backend использует:
- `shared/agent-enums` — роли, назначения, статусы;
- `shared/db-repository` — репозиторий промптов;
- `shared/rag-client` — клиент и фабрика ChromaDB.

Эти пакеты собираются в Docker-образе backend как wheel и устанавливаются на этапе build.
