import { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';

export default function AnalysisResult({ content, isLoading, activeTab = 0, onTabChange }) {
  const parsedContent = useMemo(() => {
    if (!content) return [];
    const arr = Array.isArray(content) ? content : [content];
    return arr.map(item => {
      if (typeof item === 'string') return { answer: item, score: undefined };
      return { answer: item.answer ?? '', score: item.score };
    });
  }, [content]);

  // 🔹 Защита от выхода индекса за пределы массива
  const safeActiveTab = Math.min(activeTab, Math.max(0, parsedContent.length - 1));

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center gap-2 text-gray-500 text-sm">
        <span className="w-5 h-5 border-2 border-gray-300 border-t-indigo-600 rounded-full animate-spin"/>
        Анализ документа...
      </div>
    );
  }

  if (!content || parsedContent.length === 0) {
    return (
      <div className="flex h-full items-center justify-center text-gray-400 text-sm select-none">
        Результат анализа появится здесь
      </div>
    );
  }

  const getTabTitle = (item, index) => {
    const base = `Ответ ${index + 1}`;
    return item.score != null ? `${base} (Оценка: ${item.score})` : base;
  };

  const MarkdownContent = ({ text }) => (
    <ReactMarkdown
      components={{
        h1: ({ children }) => <h1 className="text-2xl font-bold text-gray-900 mt-6 mb-3 border-b border-gray-200 pb-2">{children}</h1>,
        h2: ({ children }) => <h2 className="text-xl font-semibold text-gray-800 mt-5 mb-2">{children}</h2>,
        h3: ({ children }) => <h3 className="text-lg font-medium text-gray-800 mt-4 mb-2">{children}</h3>,
        h4: ({ children }) => <h4 className="text-base font-medium text-gray-700 mt-3 mb-1">{children}</h4>,
        p: ({ children }) => <p className="mb-3 text-sm leading-relaxed">{children}</p>,
        ul: ({ children }) => <ul className="list-disc pl-6 mb-3 space-y-1">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal pl-6 mb-3 space-y-1">{children}</ol>,
        li: ({ children }) => <li className="text-sm leading-relaxed">{children}</li>,
        code: ({ children, className }) => {
          const isInline = !className?.includes('language-');
          return isInline ? (
            <code className="bg-gray-100 text-indigo-600 px-1.5 py-0.5 rounded text-xs font-mono">{children}</code>
          ) : (
            <code className={className}>{children}</code>
          );
        },
        pre: ({ children }) => (
          <pre className="bg-gray-900 text-gray-100 p-3 rounded-lg overflow-x-auto text-xs font-mono my-3 leading-relaxed">
            {children}
          </pre>
        ),
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-indigo-300 bg-indigo-50 pl-4 py-2 my-3 rounded-r text-sm text-indigo-800 italic">
            {children}
          </blockquote>
        ),
        table: ({ children }) => (
          <div className="overflow-x-auto my-3 rounded-lg border border-gray-200">
            <table className="min-w-full divide-y divide-gray-200 text-sm">{children}</table>
          </div>
        ),
        th: ({ children }) => (
          <th className="px-3 py-2 text-left font-semibold text-gray-700 bg-gray-50 whitespace-nowrap">{children}</th>
        ),
        td: ({ children }) => (
          <td className="px-3 py-2 text-gray-900 border-t border-gray-100 whitespace-nowrap">{children}</td>
        ),
        a: ({ children, href }) => (
          <a href={href} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-800 underline break-all">
            {children}
          </a>
        ),
        hr: () => <hr className="my-4 border-gray-200" />,
        img: ({ src, alt }) => (
          <img src={src} alt={alt} className="max-w-full h-auto rounded-lg my-3 border border-gray-200" loading="lazy" />
        ),
      }}
    >
      {text}
    </ReactMarkdown>
  );

  // 🔹 Вкладки показываются ТОЛЬКО если элементов > 1
  const showTabs = parsedContent.length > 1;

  return (
    <div className="h-full flex flex-col">
      {showTabs && (
        <div className="flex items-center gap-1 px-2 py-2 border-b border-gray-200 bg-gray-50 overflow-x-auto" style={{ height: '40px' }}>
          {parsedContent.map((item, index) => (
            <button
              key={index}
              type="button"
              onClick={() => onTabChange?.(index)}
              className={`
                px-3 py-1.5 text-sm font-medium rounded-t transition-all whitespace-nowrap shrink-0
                ${activeTab === index
                  ? 'bg-white text-indigo-700 border-b-2 border-indigo-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }
              `}
            >
              {getTabTitle(item, index)}
            </button>
          ))}
        </div>
      )}

      <div className="flex-1 overflow-auto pr-2 text-gray-900">
        {/* 🔹 ИСПРАВЛЕНИЕ: рендерим компонент, даже если answer пустой строкой */}
        {parsedContent[safeActiveTab] ? (
          <MarkdownContent text={parsedContent[safeActiveTab].answer ?? ''} />
        ) : (
          <div className="flex h-full items-center justify-center text-gray-400 text-sm">
            Нет данных для отображения
          </div>
        )}
      </div>
    </div>
  );
}