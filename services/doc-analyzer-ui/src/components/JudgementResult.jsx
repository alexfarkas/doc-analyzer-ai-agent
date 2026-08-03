// src/components/JudgementResult.jsx
import { useState, useMemo, useCallback, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { apiFetch, apiStream } from '../utils/api';

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
    const response = await apiStream('/doc/chat/stream', {
      method: 'POST',
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
            if (data.type === 'usage' || data.token_usage) {
              const usage = data.type === 'usage' ? data : data.token_usage;
              onUsage?.(
                {
                  input_tokens: usage.input_tokens,
                  output_tokens: usage.output_tokens,
                  total_tokens: usage.total_tokens
                },
                data.total_token_usage
              );
            } else if (data.token) {
              const unescaped = data.token.replace(/\\n/g, '\n').replace(/\\r/g, '\r');
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
        if (prev && availableModels.some(m => m.name === prev)) return prev;
        return availableModels[0].name;
      });
    }
  }, [availableModels]);

  useEffect(() => {
    if (activeTab != null && chatHistories[activeTab] === undefined) {
      setChatHistories(prev => ({ ...prev, [activeTab]: { messages: [], input: '' } }));
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
      requestAnimationFrame(() => { container.scrollTop = container.scrollHeight; });
    }
  }, [chatHistories[activeTab]?.messages?.length, activeTab]);

  useEffect(() => {
    isAtBottomRef.current = true;
    setShowScrollButton(false);
    const container = chatContainerRef.current;
    if (container) container.scrollTop = container.scrollHeight;
  }, [activeTab]);

  const handleClarifySubmit = useCallback(async () => {
    const userMessage = clarificationInputs[activeTab]?.trim();
    if (!userMessage || !currentAgentData) return;

    const targetAgentIndex = activeTab;
    const currentAnswers = currentAgentData?.answer_seq?.answers || [];
    const targetAiAnswer = currentAnswers.length > 0 ? currentAnswers[currentAnswers.length - 1].answer : '';

    setIsLoading(prev => ({ ...prev, clarify: true }));

    try {
      const data = await apiFetch('/doc/clarify', {
        method: 'POST',
        body: JSON.stringify({
          agent_index: targetAgentIndex,
          ai_answer: targetAiAnswer,
          user_message: userMessage,
          agents: agents.map(a => ({ model: a.model, assignment: a.assignment })),
          model: selectedModel
        })
      });

      if (onAnalysisResultUpdate && data.result) {
        const resultData = Array.isArray(data.result) ? data.result[0] : data.result;
        if (resultData?.answer_seq && Array.isArray(resultData.answer_seq.answers)) {
          const answers = resultData.answer_seq.answers
            .filter(a => a && typeof a === 'object' && typeof a.answer === 'string')
            .map(a => ({ answer: a.answer, author: a.author || '', status: a.status || '', init_status: a.init_status || '' }));

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
            { role: 'user', content: userMessage, timestamp: Date.now() },
            { role: 'assistant', content: '', timestamp: Date.now(), streaming: true }
          ],
          input: ''
        }
      };
    });

    const agentsPayload = agents.map(a => ({ model: a.model, assignment: a.assignment }));

    await streamChatResponse(
      userMessage, targetAgentIndex, agentsPayload, selectedModel,
      (token) => {
        setChatHistories(prev => {
          const history = prev[targetAgentIndex];
          if (!history) return prev;
          const messages = [...history.messages];
          const lastMsg = messages[messages.length - 1];
          if (lastMsg?.role === 'assistant' && lastMsg.streaming) {
            messages[messages.length - 1] = { ...lastMsg, content: lastMsg.content + token };
          }
          if (isAtBottomRef.current) {
            requestAnimationFrame(() => {
              const container = chatContainerRef.current;
              if (container) container.scrollTop = container.scrollHeight;
            });
          }
          return { ...prev, [targetAgentIndex]: { ...history, messages } };
        });
      },
      () => {
        setChatHistories(prev => {
          const history = prev[targetAgentIndex];
          if (!history) return prev;
          const messages = [...history.messages];
          const lastMsg = messages[messages.length - 1];
          if (lastMsg?.role === 'assistant' && lastMsg.streaming) {
            messages[messages.length - 1] = { ...lastMsg, streaming: false };
          }
          return { ...prev, [targetAgentIndex]: { ...history, messages } };
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
              messages: [...history.messages, { role: 'assistant', content: `❌ Ошибка: ${err.message}`, timestamp: Date.now(), isError: true }]
            }
          };
        });
      },
      (usage, totalUsage) => {
        if (onStatsUpdate) onStatsUpdate(usage, totalUsage);
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

  const tabs = ['Оценка', 'Уточнение', 'Чат'];

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center gap-1">
          {tabs.map((tabName, index) => (
            <button
              key={index}
              type="button"
              onClick={() => setJudgementTab(index)}
              className={`tab-base ${judgementTab === index ? 'tab-active' : 'tab-inactive'}`}
            >
              {tabName}
            </button>
          ))}
        </div>
        {availableModels.length > 0 && (
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            disabled={isLoading.clarify || isLoading.chat}
            className="input-base min-w-[140px] py-1 text-xs"
          >
            {availableModels.map(model => (
              <option key={`${model.provider}-${model.name}`} value={model.name}>{model.name}</option>
            ))}
          </select>
        )}
      </div>

      <div className="p-4">
        {judgementTab === 0 && (
          <div className="text-gray-900 leading-relaxed text-sm">
            {currentAgentData?.judgement != null ? (
              <ReactMarkdown>{String(currentAgentData.judgement)}</ReactMarkdown>
            ) : (
              <p className="text-gray-400 text-sm">Оценка отсутствует</p>
            )}
          </div>
        )}

        {judgementTab === 1 && (
          <div className="space-y-3">
            <textarea
              value={clarificationInputs[activeTab] || ''}
              onChange={(e) => setClarificationInputs(prev => ({ ...prev, [activeTab]: e.target.value }))}
              onKeyDown={(e) => handleKeyDown(e, 'clarify')}
              placeholder="Введите уточняющий вопрос или комментарий..."
              disabled={isLoading.clarify}
              className="input-base w-full min-h-[80px] resize-y"
            />
            <div className="flex items-center justify-between">
              <span className="text-hint">Ctrl+Enter для отправки</span>
              <button
                type="button"
                onClick={handleClarifySubmit}
                disabled={isLoading.clarify || !(clarificationInputs[activeTab]?.trim())}
                className="btn-primary"
              >
                {isLoading.clarify ? (
                  <><span className="spinner-white"/> Отправка...</>
                ) : 'Отправить'}
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
                  <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[85%] px-3 py-2 rounded-lg text-sm leading-relaxed prose prose-sm
                      ${msg.role === 'user' ? 'bg-gray-200 text-gray-900 rounded-br-none' : msg.isError ? 'bg-red-50 text-red-900 rounded-bl-none border border-red-200' : 'bg-indigo-50 text-gray-900 rounded-bl-none border border-indigo-100'}`}>
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
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
                <button onClick={scrollToBottom} className="absolute bottom-3 left-1/2 -translate-x-1/2 w-8 h-8 bg-white border border-gray-200 text-gray-600 rounded-full shadow-lg flex items-center justify-center hover:bg-gray-50 hover:text-indigo-600 hover:border-indigo-200 transition-all z-10" aria-label="Прокрутить вниз">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4"><path fillRule="evenodd" d="M10 3a1 1 0 011 1v10.586l3.293-3.293a1 1 0 111.414 1.414l-5 5a1 1 0 01-1.414 0l-5-5a1 1 0 111.414-1.414L9 14.586V4a1 1 0 011-1z" clipRule="evenodd" /></svg>
                </button>
              )}
            </div>
            <textarea
              value={chatHistories[activeTab]?.input || ''}
              onChange={(e) => setChatHistories(prev => ({ ...prev, [activeTab]: { ...(prev[activeTab] || { messages: [] }), input: e.target.value } }))}
              onKeyDown={(e) => handleKeyDown(e, 'chat')}
              placeholder="Введите сообщение..."
              disabled={isLoading.chat}
              className="input-base w-full min-h-[80px] resize-y"
            />
            <div className="flex items-center justify-between">
              <span className="text-hint">Ctrl+Enter для отправки</span>
              <button
                type="button"
                onClick={handleChatSubmit}
                disabled={isLoading.chat || !(chatHistories[activeTab]?.input?.trim())}
                className="btn-primary"
              >
                {isLoading.chat ? (
                  <><span className="spinner-white"/> Отправка...</>
                ) : 'Отправить'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}