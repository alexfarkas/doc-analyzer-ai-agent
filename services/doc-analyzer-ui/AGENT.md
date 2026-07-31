# AGENT.md — Doc Analyzer UI

Этот документ описывает проект `services/doc-analyzer-ui` для разработчиков и AI-агентов, которые вносят изменения во frontend.

## 1) Назначение проекта

`doc-analyzer-ui` — клиентское React-приложение для управления анализом документов и взаимодействия с backend-сервисом `doc-analyzer-backend`.

Основные задачи UI:
- конфигурировать запуск анализа (роль, число агентов, модель, assignment);
- загружать источники данных (файлы/URL);
- запускать анализ и отображать прогресс агентов в реальном времени;
- показывать результаты, версии ответов и оценку;
- поддерживать уточнение и чат с агентом (включая streaming);
- отображать метрики: токены, стоимость, время, лимиты.

---

## 2) Технологический стек

- React 19
- Vite 8
- Tailwind CSS 4
- `react-markdown` + `remark-gfm`
- Fetch API
- SSE (Server-Sent Events)
- Nginx (runtime в Docker, прокси `/api/*` на backend)

Скрипты (`package.json`):
- `npm run dev`
- `npm run build`
- `npm run preview`
- `npm run lint`

---

## 3) Структура проекта

```text
services/doc-analyzer-ui/
├── Dockerfile
├── nginx.conf
├── package.json
├── vite.config.js
├── index.html
├── public/
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── App.css
    ├── index.css
    ├── assets/
    └── components/
        ├── MainMenu.jsx
        ├── ResourcesUpload.jsx
        ├── AnalysisResult.jsx
        ├── JudgementResult.jsx
        └── StatisticsSummary.jsx
```

---

## 4) Архитектура UI и ответственность компонентов

## `src/App.jsx` (оркестратор приложения)
Хранит основной state и связывает все части интерфейса:
- конфигурация ролей: `rolesConfig`
- выбранная роль: `selectedRoleApi`
- число агентов: `selectedAgentsCount`
- конфигурация агентов: `selectedAgents[]`
- ресурсы для анализа: `resources[]`
- результаты: `analysisResult[]`
- активная вкладка результата: `activeTab`
- статус выполнения: `isLoading`
- ошибки: `error`
- метрики: `stats` (`elapsed`, tokens, cost, currency)
- статусы агентов: `agentStatuses`
- лимиты: `limit`, `limitSettings`

Отвечает за:
- загрузку `/api/config`;
- загрузку агрегированной статистики `/api/tokens/total`;
- сохранение/восстановление состояния из `localStorage`;
- запуск анализа через `/api/doc/analyze/stream`;
- обработку SSE-событий (`agent_start`, `agent_end`, `complete`, `error`);
- подтверждение перезагрузки страницы при наличии результатов.

## `src/components/MainMenu.jsx`
- выбор роли;
- выбор количества агентов (до `max_agents` роли);
- выбор модели и assignment для каждого агента;
- индикация статуса агента (`idle` / `loading` / `done`);
- кнопка запуска анализа.

## `src/components/ResourcesUpload.jsx`
- загрузка файлов в `/api/upload/file`;
- добавление URL (валидация на клиенте);
- drag-and-drop;
- список выбранных ресурсов и удаление из списка;
- отображение состояния загрузки файлов.

## `src/components/AnalysisResult.jsx`
- рендер ответа в markdown;
- вкладки по результатам агентов;
- поддержка итераций ответов;
- режим сравнения двух итераций;
- отображение score в заголовках вкладок.

## `src/components/JudgementResult.jsx`
Три режима:
1. Оценка (`judgement`)  
2. Уточнение (`/api/doc/clarify`)  
3. Чат (`/api/doc/chat/stream`)  

Особенности:
- выбор модели для уточнения/чата;
- потоковое добавление токенов в чат;
- обработка `[DONE]` в SSE-потоке чата;
- независимая история чата по каждой вкладке агента;
- обновление метрик токенов через `onStatsUpdate`.

## `src/components/StatisticsSummary.jsx`
- отображение потраченных и общих токенов;
- отображение стоимости (если backend вернул `currency`);
- отображение времени первой генерации;
- ввод лимита токенов (проверка на uint64/int64-совместимый диапазон);
- подсветка лимитов по порогам (`abs_value`/`percent`);
- очистка агрегированной статистики через `/api/tokens/clear`.

---

## 5) Контракт с backend API (через `/api/*`)

## Конфигурация и состояние
- `GET /api/config`
- `GET /api/tokens/total`
- `POST /api/tokens/clear`

## Источники данных
- `POST /api/upload/file`
- `POST /api/upload/from-url`
- `GET /api/files/list`
- `GET /api/files/preview`

## Анализ
- `POST /api/doc/analyze/stream` (основной путь в UI)

Ожидаемые SSE-события:
- `event: agent_start` (`agentId`)
- `event: agent_end` (`agentId`)
- `event: complete` (result + token_usage + total_token_usage + cost fields)
- `event: error` (message)

## Уточнение и чат
- `POST /api/doc/clarify`
- `POST /api/doc/chat/stream`

Для `chat/stream` UI обрабатывает строки формата `data: ...`, включая:
- `{"token": "..."}`
- usage payload (`token_usage` или `type === "usage"`)
- `data: [DONE]`

---

## 6) Runtime и доставка

## Docker
`Dockerfile` использует multi-stage:
1. `node:20-alpine` — сборка Vite-проекта;
2. `nginx:1.25-alpine` — раздача статики.

Build-аргумент:
- `VITE_API_BASE_URL` (по умолчанию `http://localhost:8000`).

## Nginx (`nginx.conf`)
- прокси `/api/` на `doc-analyzer-backend:8000`;
- отключена буферизация для SSE (`proxy_buffering off`);
- проксируются `/health`, `/docs`, `/redoc`, `/openapi.json`;
- SPA fallback через `try_files ... /index.html`.

---

## 7) Локальное состояние (localStorage)

Ключи:
- `doc_analyzer_selection_v3` — роль/агенты/снимок конфигурации;
- `doc_analyzer_limit` — лимит токенов;
- `doc_analyzer_limit_settings` — режим/порог предупреждения.

При изменении конфигурации ролей на backend UI валидирует snapshot и при несовместимости сбрасывает выбор на дефолтный.

---

## 8) Правила внесения изменений

1. Не ломать SSE-контракт, который ожидает `App.jsx` и `JudgementResult.jsx`.
2. Не менять структуру объектов `analysisResult` без синхронизации с `AnalysisResult`/`JudgementResult`.
3. Избегать дублирования состояния: источник истины — `App.jsx`, дочерние компоненты максимально презентационные.
4. Любые новые API-вызовы делать с явной обработкой `!response.ok`.
5. Новые поля статистики добавлять согласованно в:
   - `stats` в `App.jsx`
   - `StatisticsSummary.jsx`
   - обработчики `handleStatsUpdate` и SSE `complete`.
6. Сохранять русскоязычные пользовательские тексты и текущий UX-паттерн.
7. Для markdown-рендеринга использовать существующие безопасные компоненты (`react-markdown`) без прямого HTML-вставления.

---

## 9) Что проверять после изменений

- `npm run build` проходит без ошибок;
- `npm run lint` проходит;
- загрузка файлов/URL работает;
- анализ через `/api/doc/analyze/stream` корректно отображает прогресс;
- вкладки, версии и сравнение в `AnalysisResult` работают;
- уточнение и чат в `JudgementResult` работают и завершают поток на `[DONE]`;
- счетчики токенов/стоимости обновляются корректно;
- лимит и выбранные настройки восстанавливаются из localStorage;
- страница корректно работает на desktop и mobile.

---

## 10) Частые точки расширения

- Добавление новых панелей/виджетов: обычно через `App.jsx` + отдельный компонент в `src/components`.
- Новые метрики: `stats` + `StatisticsSummary.jsx`.
- Новые события streaming: обработка в парсере SSE в `App.jsx` и/или `JudgementResult.jsx`.
- Новые поля конфигурации ролей: учесть в механизме snapshot-валидации сохраненного выбора.
