import { useMemo, useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function AnalysisResult({ content, isLoading, activeTab = 0, onTabChange }) {
  const [iterationSelections, setIterationSelections] = useState({});
  const [compareState, setCompareState] = useState(null);

  const parsedContent = useMemo(() => {
    if (!content) return [];
    const arr = Array.isArray(content) ? content : [content];
    return arr.map(item => {
      if (item.answer_seq && Array.isArray(item.answer_seq.answers)) {
        const answers = item.answer_seq.answers
          .filter(a => a && typeof a === 'object' && typeof a.answer === 'string')
          .map(a => ({
            answer: a.answer,
            author: a.author || '',
            status: a.status || '',
            init_status: a.init_status || '',
          }));
        return {
          answer_seq: { answers },
          score: typeof item.score === 'number' ? item.score : undefined,
        };
      }

      return {
        answer_seq: { answers: [] },
        score: typeof item.score === 'number' ? item.score : undefined,
      };
    });
  }, [content]);

  const safeActiveTab = Math.min(activeTab, Math.max(0, parsedContent.length - 1));

  useEffect(() => {
    setCompareState(null);
  }, [activeTab, content]);

  const getAnswers = (tabIndex) => {
    return parsedContent[tabIndex]?.answer_seq?.answers || [];
  };

  const getSelectedIteration = (tabIndex) => {
    const answers = getAnswers(tabIndex);
    if (answers.length === 0) return 0;
    return iterationSelections[tabIndex] ?? (answers.length - 1);
  };

  const getDisplayText = (tabIndex, iterationIndex) => {
    const answers = getAnswers(tabIndex);
    if (answers.length === 0) return '';
    if (iterationIndex !== undefined && iterationIndex < answers.length) {
      return answers[iterationIndex]?.answer ?? '';
    }
    return answers[answers.length - 1]?.answer ?? '';
  };

  const getIterationLabel = (tabIndex, iterationIndex) => {
    const answers = getAnswers(tabIndex);
    const item = answers[iterationIndex];
    if (!item) return '';

    if (item.status === 'final') {
      return item.author
        ? `✨ Финальный результат (${item.author})`
        : '✨ Финальный результат';
    }

    const authorLabel = item.author || 'Промежуточный';
    return `📝 ${authorLabel}: ${iterationIndex + 1} из ${answers.length}`;
  };

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

  const formatScore = (score) => {
    if (score == null) return '';
    if (Number.isInteger(score)) return score.toString();
    return parseFloat(score.toFixed(2)).toString();
  };

  const getTabTitle = (item, index) => {
    const base = `Ответ ${index + 1}`;
    return item.score != null ? `${base} (Оценка: ${formatScore(item.score)})` : base;
  };

  const MarkdownContent = ({ text }) => {
    if (!text || text.trim() === '') {
      return (
        <div className="flex h-full items-center justify-center text-gray-400 text-sm italic py-8">
          Нет содержимого для отображения
        </div>
      );
    }

    return (
      <div className="prose prose-sm max-w-none">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({ children }) => <h1 className="text-2xl font-bold text-gray-900 mt-6 mb-3 border-b border-gray-200 pb-2">{children}</h1>,
            h2: ({ children }) => <h2 className="text-xl font-semibold text-gray-800 mt-5 mb-2">{children}</h2>,
            h3: ({ children }) => <h3 className="text-lg font-medium text-gray-800 mt-4 mb-2">{children}</h3>,
            h4: ({ children }) => <h4 className="text-base font-medium text-gray-700 mt-3 mb-1">{children}</h4>,
            p: ({ children }) => <p className="mb-3 text-sm leading-relaxed text-gray-900">{children}</p>,
            ul: ({ children }) => <ul className="list-disc pl-6 mb-3 space-y-1 text-gray-900">{children}</ul>,
            ol: ({ children }) => <ol className="list-decimal pl-6 mb-3 space-y-1 text-gray-900">{children}</ol>,
            li: ({ children }) => <li className="text-sm leading-relaxed text-gray-900">{children}</li>,
            strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
            em: ({ children }) => <em className="italic text-gray-900">{children}</em>,
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
            thead: ({ children }) => <thead className="bg-gray-50">{children}</thead>,
            tbody: ({ children }) => <tbody className="bg-white divide-y divide-gray-200">{children}</tbody>,
            tr: ({ children }) => <tr>{children}</tr>,
            th: ({ children }) => <th className="px-3 py-2 text-left font-semibold text-gray-700 whitespace-nowrap">{children}</th>,
            td: ({ children }) => <td className="px-3 py-2 text-gray-900 whitespace-normal">{children}</td>,
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
      </div>
    );
  };

  const showTabs = parsedContent.length > 1;

  const answers = getAnswers(safeActiveTab);
  const totalButtons = answers.length;
  const hasIterations = totalButtons > 1;

  const handleIterationSelect = (iterationIndex, side = 'left') => {
    if (compareState) {
      setCompareState(prev => ({
        ...prev,
        [side === 'left' ? 'leftIteration' : 'rightIteration']: iterationIndex,
      }));
    } else {
      setIterationSelections(prev => ({
        ...prev,
        [safeActiveTab]: iterationIndex,
      }));
    }
  };

  const handleToggleCompare = () => {
    if (compareState) {
      setIterationSelections(prev => ({
        ...prev,
        [safeActiveTab]: compareState.leftIteration,
      }));
      setCompareState(null);
    } else {
      const currentAnswers = getAnswers(safeActiveTab);
      let finalIndex = currentAnswers.length - 1;
      for (let i = currentAnswers.length - 1; i >= 0; i--) {
        if (currentAnswers[i].status === 'final') {
          finalIndex = i;
          break;
        }
      }

      setCompareState({
        leftIteration: getSelectedIteration(safeActiveTab),
        rightIteration: finalIndex,
      });
    }
  };

  const IterationPanel = ({ side, iterationIndex }) => {
    return (
      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex items-center gap-1 px-3 py-2 border-b border-gray-200 bg-amber-50/50 overflow-x-auto">
          {answers.map((answerItem, i) => {
            const isFinal = answerItem.status === 'final';
            const isThisSelected = iterationIndex === i;

            return (
              <button
                key={i}
                type="button"
                onClick={() => handleIterationSelect(i, side)}
                title={isFinal ? 'Финальный результат' : `Промежуточный результат ${i + 1}`}
                className={`
                  min-w-[32px] h-8 px-2 text-xs font-semibold rounded transition-all shrink-0
                  ${isThisSelected
                    ? isFinal
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'bg-yellow-500 text-white shadow-sm'
                    : isFinal
                      ? 'bg-white text-indigo-600 border border-indigo-200 hover:bg-indigo-50'
                      : 'bg-white text-yellow-600 border border-yellow-200 hover:bg-yellow-50'
                  }
                `}
              >
                {i + 1}
              </button>
            );
          })}

          <span className="ml-3 text-xs text-gray-500 whitespace-nowrap">
            {getIterationLabel(safeActiveTab, iterationIndex)}
          </span>
        </div>

        <div className={`flex-1 overflow-auto text-gray-900 ${side === 'left' ? 'pr-2' : 'pl-2'}`}>
          <MarkdownContent text={getDisplayText(safeActiveTab, iterationIndex)} />
        </div>
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col">
      {showTabs && (
        <div className="flex items-center gap-1 px-2 py-2 border-b border-gray-200 bg-gray-50 overflow-x-auto" style={{ minHeight: '40px' }}>
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

      {!showTabs && parsedContent[safeActiveTab]?.score != null && (
        <div className="flex items-center px-2 py-2 border-b border-gray-200 bg-gray-50" style={{ minHeight: '40px' }}>
          <span className="px-3 py-1.5 text-sm font-medium text-indigo-700 whitespace-nowrap">
            Оценка: {formatScore(parsedContent[safeActiveTab].score)}
          </span>
        </div>
      )}

      {hasIterations && (
        <div className="flex items-center gap-2 px-3 py-2 border-b border-gray-200 bg-amber-50/50 overflow-x-auto">
          {!compareState && (
            <>
              {answers.map((answerItem, i) => {
                const isFinal = answerItem.status === 'final';
                const isSelected = getSelectedIteration(safeActiveTab) === i;

                return (
                  <button
                    key={i}
                    type="button"
                    onClick={() => handleIterationSelect(i, 'left')}
                    title={isFinal ? 'Финальный результат' : `Промежуточный результат ${i + 1}`}
                    className={`
                      min-w-[32px] h-8 px-2 text-xs font-semibold rounded transition-all shrink-0
                      ${isSelected
                        ? isFinal
                          ? 'bg-indigo-600 text-white shadow-sm'
                          : 'bg-yellow-500 text-white shadow-sm'
                        : isFinal
                          ? 'bg-white text-indigo-600 border border-indigo-200 hover:bg-indigo-50'
                          : 'bg-white text-yellow-600 border border-yellow-200 hover:bg-yellow-50'
                      }
                    `}
                  >
                    {i + 1}
                  </button>
                );
              })}

              <span className="ml-3 text-xs text-gray-500 whitespace-nowrap">
                {getIterationLabel(safeActiveTab, getSelectedIteration(safeActiveTab))}
              </span>
            </>
          )}

          <button
            type="button"
            onClick={handleToggleCompare}
            title={compareState ? 'Выйти из режима сравнения' : 'Сравнить версии'}
            className={`
              ml-auto px-3 h-8 text-xs font-semibold rounded transition-all shrink-0 whitespace-nowrap
              ${compareState
                ? 'bg-indigo-600 text-white shadow-inner border border-indigo-700'
                : 'bg-white text-indigo-600 border border-indigo-200 hover:bg-indigo-50'
              }
            `}
          >
            {compareState ? '✓ Сравнить' : 'Сравнить'}
          </button>
        </div>
      )}

      <div className="flex-1 overflow-hidden flex">
        {compareState ? (
          <>
            <IterationPanel
              side="left"
              iterationIndex={compareState.leftIteration}
            />
            <div className="w-px bg-gray-200" />
            <IterationPanel
              side="right"
              iterationIndex={compareState.rightIteration}
            />
          </>
        ) : (
          <div className="flex-1 overflow-auto pr-2 text-gray-900">
            {parsedContent[safeActiveTab] ? (
              <MarkdownContent text={getDisplayText(safeActiveTab, getSelectedIteration(safeActiveTab))} />
            ) : (
              <div className="flex h-full items-center justify-center text-gray-400 text-sm">
                Нет данных для отображения
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}