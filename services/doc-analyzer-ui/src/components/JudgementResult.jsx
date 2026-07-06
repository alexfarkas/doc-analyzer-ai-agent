import { useState, useMemo, useCallback, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

const streamChatResponse = async (
  userMessage,
  agentIndex,
  agents,
  model,
  onToken,
  onComplete,
  onError,
  onUsage
) => {
  try {
    const response = await fetch('/api/doc/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_message: userMessage,
        agent_index: agentIndex,
        agents: agents,
        model: model
      })
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || 'Ошибка стриминга');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6).trim();

          if (dataStr === '[DONE]') {
            onComplete?.();
            return;
          }

          try {
            const data = JSON.parse(dataStr);

            if (data.type === 'usage') {
              onUsage?.(
                {
                  input_tokens: data.input_tokens,
                  output_tokens: data.output_tokens,
                  total_tokens: data.total_tokens
                },
                data.total_token_usage
              );
            } else if (data.token_usage) {
              onUsage?.(
                {
                  input_tokens: data.token_usage.input_tokens,
                  output_tokens: data.token_usage.output_tokens,
                  total_tokens: data.token_usage.total_tokens
                },
                data.total_token_usage
              );
            } else if (data.token) {
              const unescaped = data.token
                .replace(/\\n/g, '\n')
                .replace(/\\r/g, '\r');
              onToken?.(unescaped);
            } else if (data.error) {
              throw new Error(data.error);
            }
          } catch (e) {
            console.warn('Failed to parse SSE chunk:', dataStr, e);
          }
        }
      }
    }

    onComplete?.();
  } catch (err) {
    console.error('Chat stream error:', err);
    onError?.(err);
  }
};

export default function JudgementResult({
  content,
  activeTab,
  agents,
  availableModels,
  onAnalysisResultUpdate,
  onStatsUpdate
}) {
  const [judgementTab, setJudgementTab] = useState(0);
  const [clarificationInputs, setClarificationInputs] = useState({});
  const [chatHistories, setChatHistories] = useState({});
  const [isLoading, setIsLoading] = useState({ clarify: false, chat: false });
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [selectedModel, setSelectedModel] = useState('');

  const chatContainerRef = useRef(null);
  const isAtBottomRef = useRef(true);

  const currentAgentData = useMemo(() => {
    if (!content) return null;
    const arr = Array.isArray(content) ? content : [content];
    return arr[activeTab];
  }, [content, activeTab]);

  useEffect(() => {
    if (availableModels.length > 0) {
      setSelectedModel(prev => {
        if (prev && availableModels.some(m => m.name === prev)) {
          return prev;
        }
        return availableModels[0].name;
      });
    }
  }, [availableModels]);

  useEffect(() => {
    if (activeTab != null && chatHistories[activeTab] === undefined) {
      setChatHistories(prev => ({
        ...prev,
        [activeTab]: { messages: [], input: '' }
      }));
    }
  }, [activeTab, chatHistories]);

  const handleChatScroll = useCallback((e) => {
    const el = e.target;
    const threshold = 15;
    const isAtBottom = el.scrollHeight - el.scrollTop - el.clientHeight < threshold;
    isAtBottomRef.current = isAtBottom;
    setShowScrollButton(!isAtBottom);
  }, []);

  const scrollToBottom = useCallback(() => {
    const container = chatContainerRef.current;
    if (container) {
      container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
      setShowScrollButton(false);
      isAtBottomRef.current = true;
    }
  }, []);

  useEffect(() => {
    const container = chatContainerRef.current;
    const messages = chatHistories[activeTab]?.messages || [];

    if (container && messages.length > 0 && isAtBottomRef.current) {
      requestAnimationFrame(() => {
        container.scrollTop = container.scrollHeight;
      });
    }
  }, [chatHistories[activeTab]?.messages?.length, activeTab]);

  useEffect(() => {
    isAtBottomRef.current = true;
    setShowScrollButton(false);
    const container = chatContainerRef.current;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, [activeTab]);

  const handleClarifySubmit = useCallback(async () => {
    const userMessage = clarificationInputs[activeTab]?.trim();
    if (!userMessage || !currentAgentData) return;

    const targetAgentIndex = activeTab;

    const currentAnswers = currentAgentData?.answer_seq?.answers || [];
    const targetAiAnswer = currentAnswers.length > 0
      ? currentAnswers[currentAnswers.length - 1].answer
      : '';

    setIsLoading(prev => ({ ...prev, clarify: true }));

    try {
      const response = await fetch('/api/doc/clarify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_index: targetAgentIndex,
          ai_answer: targetAiAnswer,
          user_message: userMessage,
          agents: agents.map(a => ({
            model: a.model,
            assignment: a.assignment
          })),
          model: selectedModel
        })
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Ошибка уточнения');
      }

      const data = await response.json();

      if (onAnalysisResultUpdate && data.result) {
        const resultData = Array.isArray(data.result) ? data.result[0] : data.result;

        if (resultData?.answer_seq && Array.isArray(resultData.answer_seq.answers)) {
          const answers = resultData.answer_seq.answers
            .filter(a => a && typeof a === 'object' && typeof a.answer === 'string')
            .map(a => ({
              answer: a.answer,
              author: a.author || '',
              status: a.status || '',
              init_status: a.init_status || '',
            }));

          onAnalysisResultUpdate(targetAgentIndex, {
            answer_seq: { answers },
            score: resultData.score,
            judgement: resultData.judgement,
          });
        }
      }

      if (onStatsUpdate) {
        onStatsUpdate(data.token_usage, data.total_token_usage);
      }

    } catch (err) {
      console.error('Clarify error:', err);
    } finally {
      setIsLoading(prev => ({ ...prev, clarify: false }));
    }
  }, [activeTab, currentAgentData, clarificationInputs, agents, selectedModel, onAnalysisResultUpdate, onStatsUpdate]);

  const handleChatSubmit = useCallback(async () => {
    const chatState = chatHistories[activeTab];
    const userMessage = chatState?.input?.trim();
    if (!userMessage) return;

    const targetAgentIndex = activeTab;

    setIsLoading(prev => ({ ...prev, chat: true }));

    setChatHistories(prev => {
      const currentHistory = prev[targetAgentIndex]?.messages || [];
      return {
        ...prev,
        [targetAgentIndex]: {
          messages: [
            ...currentHistory,
            { role: 'user', content: userMessage, timestamp: Date.now() }
          ],
          input: ''
        }
      };
    });

    setChatHistories(prev => {
      const currentHistory = prev[targetAgentIndex]?.messages || [];
      return {
        ...prev,
        [targetAgentIndex]: {
          messages: [
            ...currentHistory,
            { role: 'assistant', content: '', timestamp: Date.now(), streaming: true }
          ],
          input: ''
        }
      };
    });

    const agentsPayload = agents.map(a => ({
      model: a.model,
      assignment: a.assignment
    }));

    await streamChatResponse(
      userMessage,
      targetAgentIndex,
      agentsPayload,
      selectedModel,
      (token) => {
        setChatHistories(prev => {
          const history = prev[targetAgentIndex];
          if (!history) return prev;

          const messages = [...history.messages];
          const lastMsg = messages[messages.length - 1];

          if (lastMsg?.role === 'assistant' && lastMsg.streaming) {
            messages[messages.length - 1] = {
              ...lastMsg,
              content: lastMsg.content + token
            };
          }

          if (isAtBottomRef.current) {
            requestAnimationFrame(() => {
              const container = chatContainerRef.current;
              if (container) {
                container.scrollTop = container.scrollHeight;
              }
            });
          }

          return {
            ...prev,
            [targetAgentIndex]: { ...history, messages }
          };
        });
      },
      () => {
        setChatHistories(prev => {
          const history = prev[targetAgentIndex];
          if (!history) return prev;

          const messages = [...history.messages];
          const lastMsg = messages[messages.length - 1];

          if (lastMsg?.role === 'assistant' && lastMsg.streaming) {
            messages[messages.length - 1] = {
              ...lastMsg,
              streaming: false
            };
          }

          return {
            ...prev,
            [targetAgentIndex]: { ...history, messages }
          };
        });
      },
      (err) => {
        console.error('Stream error:', err);
        setChatHistories(prev => {
          const history = prev[targetAgentIndex];
          if (!history) return prev;

          return {
            ...prev,
            [targetAgentIndex]: {
              ...history,
              messages: [
                ...history.messages,
                {
                  role: 'assistant',
                  content: `❌ Ошибка: ${err.message}`,
                  timestamp: Date.now(),
                  isError: true
                }
              ]
            }
          };
        });
      },
      (usage, totalUsage) => {
        if (onStatsUpdate) {
          onStatsUpdate(usage, totalUsage);
        }
      }
    );

    setIsLoading(prev => ({ ...prev, chat: false }));
  }, [activeTab, chatHistories, agents, selectedModel, onStatsUpdate]);

  const handleKeyDown = useCallback((e, type) => {
    if (e.ctrlKey && e.key === 'Enter') {
      e.preventDefault();
      if (type === 'clarify') handleClarifySubmit();
      else if (type === 'chat') handleChatSubmit();
    }
  }, [handleClarifySubmit, handleChatSubmit]);

  const handleClarificationChange = useCallback((e) => {
    setClarificationInputs(prev => ({
      ...prev,
      [activeTab]: e.target.value
    }));
  }, [activeTab]);

  const handleChatInputChange = useCallback((e) => {
    setChatHistories(prev => ({
      ...prev,
      [activeTab]: {
        ...(prev[activeTab] || { messages: [] }),
        input: e.target.value
      }
    }));
  }, [activeTab]);

  const handleModelChange = useCallback((e) => {
    setSelectedModel(e.target.value);
  }, []);

  const tabs = ['Оценка', 'Уточнение', 'Чат'];

  return (
    <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
      <div className="flex items-center justify-between px-2 py-2 border-b border-gray-200 bg-gray-50">
        <div className="flex items-center gap-1">
          {tabs.map((tabName, index) => (
            <button
              key={index}
              type="button"
              onClick={() => setJudgementTab(index)}
              className={`
                px-3 py-1.5 text-sm font-medium rounded-t transition-all whitespace-nowrap
                ${judgementTab === index
                  ? 'bg-white text-indigo-700 border-b-2 border-indigo-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }
              `}
            >
              {tabName}
            </button>
          ))}
        </div>

        {availableModels.length > 0 && (
          <select
            value={selectedModel}
            onChange={handleModelChange}
            disabled={isLoading.clarify || isLoading.chat}
            className="px-2 py-1 bg-white border border-gray-300 rounded
                     focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                     transition text-gray-900 text-xs disabled:opacity-60 min-w-[140px]"
          >
            {availableModels.map(model => (
              <option key={`${model.provider}-${model.name}`} value={model.name}>
                {model.name}
              </option>
            ))}
          </select>
        )}
      </div>

      <div className="p-4">
        {judgementTab === 0 && (
          <div className="text-gray-900 leading-relaxed text-sm">
            {currentAgentData?.judgement != null ? (
              <ReactMarkdown
                components={{
                  p: ({ children }) => <p className="mb-2 text-sm leading-relaxed">{children}</p>,
                  ul: ({ children }) => <ul className="list-disc pl-5 mb-2 space-y-1">{children}</ul>,
                  ol: ({ children }) => <ol className="list-decimal pl-5 mb-2 space-y-1">{children}</ol>,
                  li: ({ children }) => <li className="text-sm leading-relaxed">{children}</li>,
                  code: ({ children, className }) => {
                    const isInline = !className?.includes('language-');
                    return isInline ? (
                      <code className="bg-gray-100 text-indigo-600 px-1 py-0.5 rounded text-xs font-mono">{children}</code>
                    ) : (
                      <code className={className}>{children}</code>
                    );
                  },
                  pre: ({ children }) => (
                    <pre className="bg-gray-900 text-gray-100 p-2 rounded-lg overflow-x-auto text-xs font-mono my-2">
                      {children}
                    </pre>
                  ),
                  blockquote: ({ children }) => (
                    <blockquote className="border-l-3 border-indigo-300 bg-indigo-50 pl-3 py-1 my-2 rounded-r text-sm text-indigo-800 italic">
                      {children}
                    </blockquote>
                  ),
                }}
              >
                {String(currentAgentData.judgement)}
              </ReactMarkdown>
            ) : (
              <p className="text-gray-400 text-sm">Оценка отсутствует</p>
            )}
          </div>
        )}

        {judgementTab === 1 && (
          <div className="space-y-3">
            <textarea
              value={clarificationInputs[activeTab] || ''}
              onChange={handleClarificationChange}
              onKeyDown={(e) => handleKeyDown(e, 'clarify')}
              placeholder="Введите уточняющий вопрос или комментарий..."
              disabled={isLoading.clarify}
              className="w-full min-h-[80px] px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg
                       focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                       transition text-gray-900 text-sm resize-y disabled:opacity-60"
            />
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">Ctrl+Enter для отправки</span>
              <button
                type="button"
                onClick={handleClarifySubmit}
                disabled={isLoading.clarify || !(clarificationInputs[activeTab]?.trim())}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400
                         disabled:cursor-not-allowed rounded-lg font-medium text-white
                         transition-all text-sm flex items-center gap-2"
              >
                {isLoading.clarify ? (
                  <>
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"/>
                    Отправка...
                  </>
                ) : (
                  'Отправить'
                )}
              </button>
            </div>
          </div>
        )}

        {judgementTab === 2 && (
          <div className="space-y-3">
            <div className="relative">
              <div
                ref={chatContainerRef}
                onScroll={handleChatScroll}
                className="space-y-2 max-h-[200px] overflow-y-auto pr-1"
              >
                {(chatHistories[activeTab]?.messages || []).map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`
                        max-w-[85%] px-3 py-2 rounded-lg text-sm leading-relaxed prose prose-sm
                        ${msg.role === 'user' 
                          ? 'bg-gray-200 text-gray-900 rounded-br-none' 
                          : msg.isError
                            ? 'bg-red-50 text-red-900 rounded-bl-none border border-red-200'
                            : 'bg-indigo-50 text-gray-900 rounded-bl-none border border-indigo-100'
                        }
                      `}
                    >
                      <ReactMarkdown
                        components={{
                          h1: ({ children }) => <h1 className="text-base font-bold text-gray-900 mt-2 mb-1 first:mt-0">{children}</h1>,
                          h2: ({ children }) => <h2 className="text-sm font-semibold text-gray-800 mt-2 mb-1 first:mt-0">{children}</h2>,
                          h3: ({ children }) => <h3 className="text-sm font-medium text-gray-800 mt-1.5 mb-0.5 first:mt-0">{children}</h3>,
                          h4: ({ children }) => <h4 className="text-sm font-medium text-gray-700 mt-1.5 mb-0.5 first:mt-0">{children}</h4>,
                          p: ({ children }) => <p className="mb-1 last:mb-0 leading-relaxed">{children}</p>,
                          ul: ({ children }) => <ul className="list-disc pl-4 mb-1 space-y-0.5 last:mb-0">{children}</ul>,
                          ol: ({ children }) => <ol className="list-decimal pl-4 mb-1 space-y-0.5 last:mb-0">{children}</ol>,
                          li: ({ children }) => <li className="text-sm leading-relaxed">{children}</li>,
                          code: ({ children, className }) => {
                            const isInline = !className?.includes('language-');
                            return isInline ? (
                              <code className="bg-black/10 text-indigo-700 px-1 py-0.5 rounded text-xs font-mono">{children}</code>
                            ) : (
                              <code className={className}>{children}</code>
                            );
                          },
                          pre: ({ children }) => (
                            <pre className="bg-gray-900 text-gray-100 p-2 rounded-lg overflow-x-auto text-xs font-mono my-1.5 leading-relaxed max-w-full">
                              {children}
                            </pre>
                          ),
                          blockquote: ({ children }) => (
                            <blockquote className="border-l-2 border-indigo-300 bg-indigo-100/50 pl-2 py-1 my-1 rounded-r text-xs text-indigo-800 italic">
                              {children}
                            </blockquote>
                          ),
                          table: ({ children }) => (
                            <div className="overflow-x-auto my-1.5 rounded border border-gray-200">
                              <table className="min-w-full divide-y divide-gray-200 text-xs">{children}</table>
                            </div>
                          ),
                          th: ({ children }) => <th className="px-2 py-1 text-left font-semibold text-gray-700 bg-gray-100">{children}</th>,
                          td: ({ children }) => <td className="px-2 py-1 text-gray-900 border-t border-gray-100">{children}</td>,
                          a: ({ children, href }) => (
                            <a href={href} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-800 underline break-all text-xs">
                              {children}
                            </a>
                          ),
                          hr: () => <hr className="my-1.5 border-gray-300" />,
                          img: ({ src, alt }) => (
                            <img src={src} alt={alt} className="max-w-full h-auto rounded my-1.5 border border-gray-200" loading="lazy" />
                          ),
                        }}
                      >
                        {msg.content}
                      </ReactMarkdown>

                      {msg.streaming && (
                        <span className="inline-flex items-center gap-1 ml-1 text-indigo-600">
                          <span className="w-1.5 h-1.5 bg-indigo-600 rounded-full animate-bounce [animation-delay:-0.3s]"/>
                          <span className="w-1.5 h-1.5 bg-indigo-600 rounded-full animate-bounce [animation-delay:-0.15s]"/>
                          <span className="w-1.5 h-1.5 bg-indigo-600 rounded-full animate-bounce"/>
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {showScrollButton && (
                <button
                  onClick={scrollToBottom}
                  className="absolute bottom-3 left-1/2 -translate-x-1/2 w-8 h-8 bg-white border border-gray-200 text-gray-600 rounded-full shadow-lg flex items-center justify-center hover:bg-gray-50 hover:text-indigo-600 hover:border-indigo-200 transition-all z-10"
                  aria-label="Прокрутить вниз"
                  title="Прокрутить вниз"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
                    <path fillRule="evenodd" d="M10 3a1 1 0 011 1v10.586l3.293-3.293a1 1 0 111.414 1.414l-5 5a1 1 0 01-1.414 0l-5-5a1 1 0 111.414-1.414L9 14.586V4a1 1 0 011-1z" clipRule="evenodd" />
                  </svg>
                </button>
              )}
            </div>

            <textarea
              value={chatHistories[activeTab]?.input || ''}
              onChange={handleChatInputChange}
              onKeyDown={(e) => handleKeyDown(e, 'chat')}
              placeholder="Введите сообщение..."
              disabled={isLoading.chat}
              className="w-full min-h-[80px] px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg
                       focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                       transition text-gray-900 text-sm resize-y disabled:opacity-60"
            />
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">Ctrl+Enter для отправки</span>
              <button
                type="button"
                onClick={handleChatSubmit}
                disabled={isLoading.chat || !(chatHistories[activeTab]?.input?.trim())}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400
                         disabled:cursor-not-allowed rounded-lg font-medium text-white
                         transition-all text-sm flex items-center gap-2"
              >
                {isLoading.chat ? (
                  <>
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"/>
                    Отправка...
                  </>
                ) : (
                  'Отправить'
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}