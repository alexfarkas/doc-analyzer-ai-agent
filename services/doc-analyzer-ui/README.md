# AI Documents Analyzer

Frontend на React платформы для анализа документов с помощью LLM-агентов.

## Содержание
- [Технологический стек](#технологический-стек)
- [Локальный запуск (без Docker)](#локальный-запуск-без-docker)
- [Структура репозитория](#структура-репозитория)
- [Поддерживаемые форматы файлов](#поддерживаемые-форматы-файлов)
- [Примечания по эксплуатации](#примечания-по-эксплуатации)

## Технологический стек

**Frontend**
- React 19 + Vite
- Tailwind CSS 4
- Nginx (runtime + reverse proxy `/api/*` -> backend)

## Локальный запуск (без Docker)

```bash
cd services/doc-analyzer-ui
npm ci
npm run dev
```

Vite dev server проксирует `/api` на `http://localhost:8000`.

## Структура репозитория

```text                                           
doc-analyzer-ui/                        # React frontend
├── Dockerfile                          # Multi-stage build (node -> nginx)
├── nginx.conf                          # SPA fallback, проксирование API, настройки SSE
├── package.json                        
└── src/                                
    ├── main.jsx                        # Инициализация React
    ├── App.jsx                         # Корневой компонент и orchestration API-вызовов
    ├── components/                     
    │   ├── MainMenu.jsx                # Выбор роли/агентов/моделей/назначений
    │   ├── ResourcesUpload.jsx         # Загрузка файлов и добавление URL
    │   ├── AnalysisResult.jsx          # Вкладки ответов, markdown-рендер, версии
    │   ├── JudgementResult.jsx         # Уточнение и чат со стримингом
    │   └── StatisticsSummary.jsx       # Токены, стоимость, лимиты, время
    ├── assets/
    └── *.css
```

## Поддерживаемые форматы файлов

Поддерживаются следующие форматы файлов в качестве источника данных:

`.txt`, `.md`, `.csv`, `.json`, `.yaml`, `.yml`, `.html`, `.xml`, `.docx`, `.xlsx`, `.pptx`, `.pdf`, `.jpg`, `.jpeg`, `.png`, `.gif`, `.tiff`, `.bmp`, `.py`, `.js`, `.ts`, `.java`, `.kt`, `.scala`, `.cs`, `.cpp`, `.go`, `.php`, `.swift`, `.r`, `.pl`, `.sql`, `.sh`, `.zsh`, `.bash`.

## Примечания по эксплуатации

- Для SSE в `services/doc-analyzer-ui/nginx.conf` отключена буферизация (`proxy_buffering off`).
