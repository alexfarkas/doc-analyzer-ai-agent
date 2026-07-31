# AI Documents Analyzer

Frontend на React платформы для анализа документов с помощью LLM-агентов.

## Технологический стек

- React 19, Vite
- Tailwind CSS
- Nginx (runtime, проксирование `/api/*` на backend)

## Структура репозитория

```text
doc-analyzer-ui/
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

## Примечания по эксплуатации

- Для стриминговых endpoint'ов в `nginx.conf` отключена буферизация (`proxy_buffering off`), чтобы SSE работал корректно.
