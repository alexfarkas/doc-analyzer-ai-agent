# AI Documents Analyzer

Backend на FastAPI платформы для анализа документов с помощью LLM-агентов.

## Технологический стек

- Python 3.14, FastAPI, Uvicorn
- LangChain, LangGraph, OpenAI/Ollama
- SQLAlchemy, PostgreSQL
- ChromaDB и эмбеддинги для RAG
- PyMuPDF, pypdf, pdfplumber, python-docx, python-pptx, openpyxl, unstructured
- Tesseract OCR, OpenCV, Pillow

## Структура репозитория

```text
doc-analyzer-backend/
├── Dockerfile                          # Multi-stage build
├── requirements.txt
├── src/
│   └── doc_analyzer_backend/
│       ├── main.py                     # Точка входа (uvicorn)
│       │                               
│       ├── api/                        # HTTP-слой
│       │   ├── api.py                  # Инициализация FastAPI, lifespan, middleware
│       │   ├── routers/                # Группы endpoint'ов
│       │   ├── models/                 # Pydantic request/response модели
│       │   ├── dependencies/           # DI-функции (agent, council, app_state, session)
│       │   ├── exceptions/             # Кастомные исключения и обработчики
│       │   └── utils/                  # SSE-утилиты, сборка API-ответов
│       │                               
│       ├── agent/                      # Ядро LLM-логики
│       │   ├── agent.py                # Основной агент
│       │   ├── core/                   # Граф выполнения и менеджмент моделей
│       │   ├── context/                # Хранилища промптов/диалогов/RAG-контекста
│       │   ├── agent_ai_invocation/    # Сценарии вызовов LLM
│       │   ├── council/                # Мультиагентный режим
│       │   ├── runners/                # Оркестрация стадий/очередей
│       │   ├── models/                 # Внутренние DTO для анализа/токенов/назначений
│       │   ├── messages_data/          # Формирование сообщений и progress-событий
│       │   └── consumption_counters/   # Подсчет токенов и стоимости
│       │
│       ├── components/                 # Работа с источниками данных
│       │   ├── uploader/               # Прием файлов и контента по URL
│       │   ├── preview_reader/         # Предпросмотр и разбор содержимого
│       │   └── file_manager/           # Листинг, сортировка, пагинация
│       │
│       ├── tools/                      # Инструменты агента
│       ├── llm/                        # Фабрика LLM-провайдеров и mock
│       ├── config/                     # Конфиги приложения
│       ├── data/                       # AppState и aggregate-утилиты
│       ├── session/                    # Управление пользовательской сессией
│       ├── decorators/                 # Вспомогательные декораторы
│       ├── utils/                      # Общие утилиты
│       ├── local_prompts/              # Локальные шаблоны промптов
│       ├── documents/                  # Runtime-хранилище загруженных документов
│       └── logs/                       # Runtime-логи backend
│
└── tests/                              # Автотесты
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

## Примечания по эксплуатации

- В backend-образе устанавливаются системные зависимости для OCR и обработки документов (в т.ч. `tesseract-ocr`, `poppler-utils`, `libmagic1`).
- Shared-пакеты из `shared/*` собираются в wheel и устанавливаются в backend-образ на этапе Docker-сборки.
