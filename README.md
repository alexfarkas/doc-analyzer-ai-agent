# AI Documents Analyzer

Монорепозиторий платформы для анализа документов с помощью LLM-агентов.
Система состоит из backend-сервиса на FastAPI и frontend-приложения на React, работает с файлами и URL, поддерживает потоковую выдачу результатов, учет токенов и стоимости.

## Состав проекта

- `services/doc-analyzer-backend` — API, оркестрация LLM-агентов, загрузка/предпросмотр документов, RAG, учет токенов/стоимости.
- `services/doc-analyzer-ui` — web-интерфейс для настройки агентов, запуска анализа и просмотра результатов.
- `shared/*` — общие пакеты (`agent-enums`, `db-repository`, `rag-client`).
- `infrastructure/*` — SQL-инициализация и конфиги observability (Loki/Promtail/Grafana).

## Основные возможности

- Загрузка файлов через UI и добавление URL-источников.
- Анализ документов в одиночном режиме или в режиме "совета" агентов.
- Выбор роли, модели и назначения для каждого агента.
- Стриминг анализа и чата через SSE.
- Отображение времени выполнения, токенов и стоимости.
- Очистка накопленной статистики токенов/стоимости через API.

## Технологический стек

**Backend**
- Python 3.14, FastAPI, Uvicorn
- LangChain, LangGraph, OpenAI/Ollama
- SQLAlchemy, PostgreSQL
- ChromaDB и эмбеддинги для RAG
- PyMuPDF, pypdf, pdfplumber, python-docx, python-pptx, openpyxl, unstructured
- Tesseract OCR, OpenCV, Pillow

**Frontend**
- React 19, Vite
- Tailwind CSS
- Nginx (runtime, проксирование `/api/*` на backend)

## Быстрый старт

### Требования

- Docker + Docker Compose
- Make

### Запуск

```bash
make up
```

После запуска доступны:

- Frontend: `http://localhost`
- Backend API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- ChromaDB: `http://localhost:8001`

### Полезные команды

```bash
make help
make dev
make up-all
make down
make logs
make test
make test-coverage
make lint
make format
```

## Структура репозитория

```text
doc-analyzer-ai-agent/
├── docker-compose.yml                          # Оркестрация сервисов и профилей
├── Makefile                                    # Команды запуска, тестов, линтинга, сборки
├── .env                                        # Переменные окружения
│
├── services/
│   ├── doc-analyzer-backend/                   # FastAPI backend
│   │   ├── Dockerfile                          # Multi-stage build
│   │   ├── requirements.txt
│   │   ├── src/
│   │   │   └── doc_analyzer_backend/
│   │   │       ├── main.py                     # Точка входа (uvicorn)
│   │   │       │                               
│   │   │       ├── api/                        # HTTP-слой
│   │   │       │   ├── api.py                  # Инициализация FastAPI, lifespan, middleware
│   │   │       │   ├── routers/                # Группы endpoint'ов
│   │   │       │   ├── models/                 # Pydantic request/response модели
│   │   │       │   ├── dependencies/           # DI-функции (agent, council, app_state, session)
│   │   │       │   ├── exceptions/             # Кастомные исключения и обработчики
│   │   │       │   └── utils/                  # SSE-утилиты, сборка API-ответов
│   │   │       │                               
│   │   │       ├── agent/                      # Ядро LLM-логики
│   │   │       │   ├── agent.py                # Основной агент
│   │   │       │   ├── core/                   # Граф выполнения и менеджмент моделей
│   │   │       │   ├── context/                # Хранилища промптов/диалогов/RAG-контекста
│   │   │       │   ├── agent_ai_invocation/    # Сценарии вызовов LLM
│   │   │       │   ├── council/                # Мультиагентный режим
│   │   │       │   ├── runners/                # Оркестрация стадий/очередей
│   │   │       │   ├── models/                 # Внутренние DTO для анализа/токенов/назначений
│   │   │       │   ├── messages_data/          # Формирование сообщений и progress-событий
│   │   │       │   └── consumption_counters/   # Подсчет токенов и стоимости
│   │   │       │
│   │   │       ├── components/                 # Работа с источниками данных
│   │   │       │   ├── uploader/               # Прием файлов и контента по URL
│   │   │       │   ├── preview_reader/         # Предпросмотр и разбор содержимого
│   │   │       │   └── file_manager/           # Листинг, сортировка, пагинация
│   │   │       │
│   │   │       ├── tools/                      # Инструменты агента
│   │   │       ├── llm/                        # Фабрика LLM-провайдеров и mock
│   │   │       ├── config/                     # Конфиги приложения
│   │   │       ├── data/                       # AppState и aggregate-утилиты
│   │   │       ├── session/                    # Управление пользовательской сессией
│   │   │       ├── decorators/                 # Вспомогательные декораторы
│   │   │       ├── utils/                      # Общие утилиты
│   │   │       ├── local_prompts/              # Локальные шаблоны промптов
│   │   │       ├── documents/                  # Runtime-хранилище загруженных документов
│   │   │       └── logs/                       # Runtime-логи backend
│   │   │
│   │   └── tests/                              # Автотесты
│   │                                           
│   └── doc-analyzer-ui/                        # React frontend
│       ├── Dockerfile                          # Multi-stage build (node -> nginx)
│       ├── nginx.conf                          # SPA fallback, проксирование API, настройки SSE
│       ├── package.json                        
│       └── src/                                
│           ├── main.jsx                        # Инициализация React
│           ├── App.jsx                         # Корневой компонент и orchestration API-вызовов
│           ├── components/                     
│           │   ├── MainMenu.jsx                # Выбор роли/агентов/моделей/назначений
│           │   ├── ResourcesUpload.jsx         # Загрузка файлов и добавление URL
│           │   ├── AnalysisResult.jsx          # Вкладки ответов, markdown-рендер, версии
│           │   ├── JudgementResult.jsx         # Уточнение и чат со стримингом
│           │   └── StatisticsSummary.jsx       # Токены, стоимость, лимиты, время
│           ├── assets/
│           └── *.css
│
├── shared/
│   ├── agent-enums/
│   │   └── agent_enums/                        # Role, Assignment, AnswerStatus, PromptType и др.
│   ├── db-repository/                          
│   │   └── db_repository/                      # PromptRepository и SQLAlchemy-модели
│   └── rag-client/                             
│       └── rag_client/                         # ChromaDB client/factory, embedders, config
│
└── infrastructure/
    ├── postgres/
    │   └── init/
    └── observability/
        ├── loki/
        ├── promtail/
        └── grafana/
            └── provisioning/
```

## API

### Системные endpoint'ы

| Метод | Backend endpoint | Через UI/Nginx | Назначение |
|---|---|---|---|
| GET | `/health` | `/health` и `/api/health` | Проверка готовности сервиса |
| GET | `/status` | `/api/status` | Текущая модель, инструменты, состояние RAG |
| GET | `/config` | `/api/config` | Конфиг для UI: роли, модели, лимиты |

### Сессия пользователя

| Метод | Backend endpoint | Через UI/Nginx | Назначение |
|---|---|---|---|
| GET | `/sessions/current` | `/api/sessions/current` | Получить текущую сессию |
| DELETE | `/sessions/current` | `/api/sessions/current` | Удалить текущую сессию |

### Источники данных (файлы и URL)

| Метод | Backend endpoint | Через UI/Nginx | Назначение |
|---|---|---|---|
| POST | `/upload/file` | `/api/upload/file` | Загрузка файла |
| POST | `/upload/from-url` | `/api/upload/from-url` | Загрузка/получение контента по URL |
| GET | `/files/list` | `/api/files/list` | Список файлов (сортировка, фильтры, пагинация) |
| GET | `/files/preview` | `/api/files/preview` | Предпросмотр содержимого файла |

### Анализ документов и чат

| Метод | Backend endpoint | Через UI/Nginx | Назначение |
|---|---|---|---|
| POST | `/doc/analyze` | `/api/doc/analyze` | Анализ документов (JSON-ответ) |
| POST | `/doc/analyze/stream` | `/api/doc/analyze/stream` | Анализ документов со стримингом (SSE) |
| POST | `/doc/clarify` | `/api/doc/clarify` | Уточнение ответа агента |
| POST | `/doc/chat` | `/api/doc/chat` | Нестриминговый чат |
| POST | `/doc/chat/stream` | `/api/doc/chat/stream` | Стриминговый чат (SSE) |
| POST | `/doc/history` | `/api/doc/history` | История взаимодействий |

### Токены и стоимость

| Метод | Backend endpoint | Через UI/Nginx | Назначение |
|---|---|---|---|
| GET | `/tokens/total` | `/api/tokens/total` | Суммарные токены и стоимость |
| POST | `/tokens/clear` | `/api/tokens/clear` | Очистка статистики токенов/стоимости |

## Observability и инструменты администрирования

Профили `docker compose`:

- `observability`: Loki + Promtail + Grafana
- `admin`: pgAdmin

Запуск:

```bash
make up-observability
make up-admin
```

## Примечания по эксплуатации

- В backend-образе устанавливаются системные зависимости для OCR и обработки документов (в т.ч. `tesseract-ocr`, `poppler-utils`, `libmagic1`).
- Для стриминговых endpoint'ов в `nginx.conf` отключена буферизация (`proxy_buffering off`), чтобы SSE работал корректно.
- Shared-пакеты из `shared/*` собираются в wheel и устанавливаются в backend-образ на этапе Docker-сборки.
