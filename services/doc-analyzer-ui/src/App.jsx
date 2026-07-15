import { useState, useEffect, useCallback, useRef } from 'react';
import MainMenu from './components/MainMenu';
import ResourcesUpload from './components/ResourcesUpload';
import StatisticsSummary from './components/StatisticsSummary';
import AnalysisResult from './components/AnalysisResult';
import JudgementResult from './components/JudgementResult';

const STORAGE_KEY = 'doc_analyzer_selection_v3';
const LIMIT_STORAGE_KEY = 'doc_analyzer_limit';
const LIMIT_SETTINGS_KEY = 'doc_analyzer_limit_settings';

function App() {
  const [rolesConfig, setRolesConfig] = useState([]);
  const [selectedRoleApi, setSelectedRoleApi] = useState('');
  const [selectedAgentsCount, setSelectedAgentsCount] = useState(1);
  const [selectedAgents, setSelectedAgents] = useState([]);

  const [resources, setResources] = useState([]);
  const [analysisResult, setAnalysisResult] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({
    elapsed: null,
    totalTokens: null,
    inputTokens: null,
    outputTokens: null,
    totalTokensAll: null,
    inputTokensAll: null,
    outputTokensAll: null,
    // 🔹 НОВОЕ: данные о стоимости
    cost: null,
    totalCost: null,
    currency: null,
  });

  const [judgementKey, setJudgementKey] = useState(0);
  const [agentStatuses, setAgentStatuses] = useState({});
  const [showReloadConfirm, setShowReloadConfirm] = useState(false);

  const [limit, setLimit] = useState(() => {
    try {
      const saved = localStorage.getItem(LIMIT_STORAGE_KEY);
      if (saved !== null && saved !== '' && /^\d+$/.test(saved)) {
        return saved;
      }
      return '';
    } catch {
      return '';
    }
  });

  const [limitSettings, setLimitSettings] = useState(() => {
    try {
      const saved = localStorage.getItem(LIMIT_SETTINGS_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed && (parsed.limit_threshold_mode === 'abs_value' || parsed.limit_threshold_mode === 'percent')) {
          return parsed;
        }
      }
      return null;
    } catch {
      return null;
    }
  });

  const abortControllerRef = useRef(null);

  const initAgent = (availableModels, availableAssignments) => ({
    model: availableModels[0]?.name || '',
    assignment: availableAssignments[0]?.api_param || 'exec'
  });

  useEffect(() => {
    fetch('/api/config')
      .then(res => res.json())
      .then(data => {
        const roles = data.roles || [];
        setRolesConfig(roles);

        if (data.limit_settings) {
          setLimitSettings(data.limit_settings);
        }

        if (roles.length === 0) return;

        const saved = localStorage.getItem(STORAGE_KEY);
        let restored = false;

        if (saved) {
          try {
            const parsed = JSON.parse(saved);
            const role = roles.find(r => r.api_param === parsed.roleApi);

            if (role &&
                role.ui_title === parsed.uiTitle &&
                JSON.stringify(role.models) === JSON.stringify(parsed.modelsSnapshot) &&
                JSON.stringify(role.assignments) === JSON.stringify(parsed.assignmentsSnapshot) &&
                role.max_agents === parsed.maxAgents &&
                parsed.agentsCount <= role.max_agents) {

              setSelectedRoleApi(parsed.roleApi);
              setSelectedAgentsCount(parsed.agentsCount);
              setSelectedAgents(parsed.agents || [initAgent(role.models, role.assignments)]);
              restored = true;
            }
          } catch (e) { console.warn('Failed to parse saved selection', e); }
        }

        if (!restored) {
          const firstRole = roles[0];
          setSelectedRoleApi(firstRole.api_param);
          setSelectedAgentsCount(1);
          setSelectedAgents([initAgent(firstRole.models, firstRole.assignments)]);
        }
      })
      .catch(err => console.error('Failed to fetch /api/config:', err));
  }, []);

  useEffect(() => {
    fetch('/api/tokens/total')
      .then(async (res) => {
        if (!res.ok) {
          console.warn(`Failed to fetch /api/tokens/total: ${res.status}`);
          return null;
        }
        return res.json();
      })
      .then((data) => {
        setStats((prev) => {
          const updated = { ...prev };

          if (data?.total_token_usage) {
            const usage = data.total_token_usage;
            updated.totalTokensAll = usage.total_tokens ?? null;
            updated.inputTokensAll = usage.input_tokens ?? null;
            updated.outputTokensAll = usage.output_tokens ?? null;
          }

          // 🔹 НОВОЕ: загрузка стоимости
          if (data?.currency) {
            updated.currency = data.currency;
            if (data.total_cost !== undefined && data.total_cost !== null) {
              updated.totalCost = data.total_cost;
            }
          }

          return updated;
        });
      })
      .catch((err) => {
        console.warn('Failed to fetch /api/tokens/total:', err);
      });
  }, []);

  useEffect(() => {
    if (selectedRoleApi && rolesConfig.length > 0) {
      const role = rolesConfig.find(r => r.api_param === selectedRoleApi);
      if (role) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({
          roleApi: selectedRoleApi,
          uiTitle: role.ui_title,
          modelsSnapshot: role.models,
          assignmentsSnapshot: role.assignments,
          maxAgents: role.max_agents,
          agentsCount: selectedAgentsCount,
          agents: selectedAgents
        }));
      }
    }
  }, [selectedRoleApi, selectedAgentsCount, selectedAgents, rolesConfig]);

  useEffect(() => {
    try {
      if (limit !== '') {
        localStorage.setItem(LIMIT_STORAGE_KEY, limit);
      } else {
        localStorage.removeItem(LIMIT_STORAGE_KEY);
      }
    } catch {
      // Игнорируем ошибки localStorage
    }
  }, [limit]);

  useEffect(() => {
    try {
      if (limitSettings) {
        localStorage.setItem(LIMIT_SETTINGS_KEY, JSON.stringify(limitSettings));
      } else {
        localStorage.removeItem(LIMIT_SETTINGS_KEY);
      }
    } catch {
      // Игнорируем ошибки localStorage
    }
  }, [limitSettings]);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (analysisResult.length === 0) return;

      if (e.key === 'F5') {
        e.preventDefault();
        setShowReloadConfirm(true);
        return;
      }

      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'r') {
        e.preventDefault();
        setShowReloadConfirm(true);
        return;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [analysisResult]);

  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (analysisResult.length > 0) {
        e.preventDefault();
        e.returnValue = 'Вы уверены, что хотите обновить страницу? Данные анализа документов будут утеряны.';
        return e.returnValue;
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [analysisResult]);

  const handleConfirmReload = useCallback(() => {
    window.location.reload();
  }, []);

  const handleCancelReload = useCallback(() => {
    setShowReloadConfirm(false);
  }, []);

  const handleRoleChange = (newRoleApi) => {
    setSelectedRoleApi(newRoleApi);
    const newRole = rolesConfig.find(r => r.api_param === newRoleApi);
    if (newRole) {
      setSelectedAgentsCount(1);
      setSelectedAgents([initAgent(newRole.models, newRole.assignments)]);
    }
  };

  const handleAgentsCountChange = (newCount) => {
    setSelectedAgentsCount(newCount);
    setSelectedAgents(prev => {
      const newAgents = [...prev];
      const currentRole = rolesConfig.find(r => r.api_param === selectedRoleApi);
      while (newAgents.length < newCount) {
        newAgents.push(initAgent(currentRole?.models || [], currentRole?.assignments || []));
      }
      return newAgents.slice(0, newCount);
    });
  };

  const handleAgentModelChange = (agentIndex, newModel) => {
    setSelectedAgents(prev => {
      const updated = [...prev];
      updated[agentIndex] = { ...updated[agentIndex], model: newModel };
      return updated;
    });
  };

  const handleAgentAssignmentChange = (agentIndex, newAssignmentApiParam) => {
    setSelectedAgents(prev => {
      const updated = [...prev];
      updated[agentIndex] = { ...updated[agentIndex], assignment: newAssignmentApiParam };
      return updated;
    });
  };

  const handleFileAdded = useCallback((filePath, fileName) => {
    setResources(prev => [...prev, { id: crypto.randomUUID(), type: 'file', path: filePath, name: fileName }]);
  }, []);

  const handleUrlAdded = useCallback((url) => {
    setResources(prev => [...prev, { id: crypto.randomUUID(), type: 'url', path: url, name: url }]);
  }, []);

  const handleResourceRemoved = useCallback((id) => {
    setResources(prev => prev.filter(r => r.id !== id));
  }, []);

  const handleAnalysisResultUpdate = useCallback((agentIndex, updatedData) => {
    setAnalysisResult(prev => {
      if (!prev[agentIndex]) return prev;
      const newArr = [...prev];
      newArr[agentIndex] = {
        ...newArr[agentIndex],
        ...updatedData
      };
      return newArr;
    });
  }, []);

  // 🔹 ИЗМЕНЕНО: расширенная сигнатура с cost, totalCost, currency
  const handleStatsUpdate = useCallback((
    usage,
    totalUsage,
    cost = null,
    totalCost = null,
    currency = null
  ) => {
    setStats(prev => {
      const updated = { ...prev };

      if (usage) {
        updated.totalTokens = usage.total_tokens;
        updated.inputTokens = usage.input_tokens;
        updated.outputTokens = usage.output_tokens;
      }

      if (totalUsage) {
        updated.totalTokensAll = totalUsage.total_tokens;
        updated.inputTokensAll = totalUsage.input_tokens;
        updated.outputTokensAll = totalUsage.output_tokens;
      }

      // 🔹 НОВОЕ: обновление стоимости (только если есть currency)
      if (currency) {
        updated.currency = currency;
        if (cost !== null && cost !== undefined) {
          updated.cost = cost;
        }
        if (totalCost !== null && totalCost !== undefined) {
          updated.totalCost = totalCost;
        }
      }

      return updated;
    });
  }, []);

  const handleLimitChange = useCallback((newLimit) => {
    setLimit(newLimit);
  }, []);

  const handleClearTokens = useCallback(async () => {
    try {
      const response = await fetch('/api/tokens/clear', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || errData.message || 'Ошибка очистки данных');
      }

      const data = await response.json();

      if (data.status === 'success') {
        setStats(prev => ({
          ...prev,
          totalTokensAll: null,
          inputTokensAll: null,
          outputTokensAll: null,
          // 🔹 НОВОЕ: обнуляем данные о стоимости
          totalCost: null,
          currency: prev.currency, // currency сохраняем (это системная настройка)
        }));
        return { success: true };
      } else {
        return {
          success: false,
          error: data.message || 'Не удалось очистить данные'
        };
      }
    } catch (err) {
      return {
        success: false,
        error: err.message || 'Ошибка соединения с сервером'
      };
    }
  }, []);

  const handleAnalyze = async () => {
    if (resources.length === 0) {
      setError('Добавьте хотя бы один файл или URL для анализа');
      return;
    }

    setIsLoading(true);
    setError('');
    setAnalysisResult([]);
    setActiveTab(0);

    setStats(prev => ({
      ...prev,
      elapsed: null,
      totalTokens: null,
      inputTokens: null,
      outputTokens: null,
      cost: null,
    }));

    setJudgementKey(prev => prev + 1);

    const initialStatuses = {};
    for (let i = 0; i < selectedAgentsCount; i++) {
      initialStatuses[i + 1] = 'idle';
    }
    setAgentStatuses(initialStatuses);

    abortControllerRef.current = new AbortController();

    try {
      const requestBody = {
        resources: resources.map(r => r.path),
        role: selectedRoleApi,
        agents: selectedAgents.map(a => ({
          model: a.model,
          assignment: a.assignment
        }))
      };

      if (limit !== '') {
        requestBody.limit = parseInt(limit, 10);
      }

      const response = await fetch('/api/doc/analyze/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || errData.message || 'Ошибка анализа документов');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split('\n');
        buffer = lines.pop();

        let currentEvent = null;

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            currentEvent = line.slice(7).trim();
          } else if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);

            try {
              const data = JSON.parse(dataStr);

              switch (currentEvent) {
                case 'agent_start':
                  setAgentStatuses(prev => ({
                    ...prev,
                    [data.agentId]: 'loading'
                  }));
                  break;

                case 'agent_end':
                  setAgentStatuses(prev => ({
                    ...prev,
                    [data.agentId]: 'done'
                  }));
                  break;

                case 'complete':
                  const resultArray = Array.isArray(data.result) ? data.result : [data.result];
                  const roleApiParam = data.role || '';

                  const normalizedResult = resultArray.map(item => {
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
                        score: item.score,
                        judgement: item.judgement,
                        role: roleApiParam,
                      };
                    }

                    return {
                      answer_seq: { answers: [] },
                      score: item.score,
                      judgement: item.judgement,
                      role: roleApiParam,
                    };
                  });

                  setAnalysisResult(normalizedResult);

                  setStats(prev => {
                    const updated = { ...prev };

                    if (data.token_usage) {
                      updated.elapsed = data.elapsed;
                      updated.totalTokens = data.token_usage.total_tokens || 0;
                      updated.inputTokens = data.token_usage.input_tokens || 0;
                      updated.outputTokens = data.token_usage.output_tokens || 0;
                    } else if (data.elapsed != null) {
                      updated.elapsed = data.elapsed;
                    }

                    if (data.total_token_usage) {
                      updated.totalTokensAll = data.total_token_usage.total_tokens || 0;
                      updated.inputTokensAll = data.total_token_usage.input_tokens || 0;
                      updated.outputTokensAll = data.total_token_usage.output_tokens || 0;
                    }

                    // 🔹 НОВОЕ: обработка данных о стоимости
                    if (data.currency) {
                      updated.currency = data.currency;
                      if (data.cost !== undefined && data.cost !== null) {
                        updated.cost = data.cost;
                      }
                      if (data.total_cost !== undefined && data.total_cost !== null) {
                        updated.totalCost = data.total_cost;
                      }
                    }

                    return updated;
                  });
                  break;

                case 'error':
                  throw new Error(data.message || 'Ошибка анализа');
              }
            } catch (e) {
              if (e.message !== 'Ошибка анализа') {
                console.warn('Failed to parse SSE data:', e);
              } else {
                throw e;
              }
            }

            currentEvent = null;
          }
        }
      }

    } catch (err) {
      if (err.name !== 'AbortError') {
        setError(err.message);
      }
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
      setAgentStatuses({});
    }
  };

  const currentRole = rolesConfig.find(r => r.api_param === selectedRoleApi);
  const availableModels = currentRole?.models || [];

  return (
    <div className="min-h-screen bg-white text-gray-900 font-sans">
      <header className="bg-white border-b border-gray-200 py-4 px-8 sticky top-0 z-50 shadow-sm">
        <h1 className="text-2xl font-bold text-gray-800">🤖 AI Documents Analyzer</h1>
      </header>

      <main className="max-w-7xl mx-auto p-6 space-y-6">

        <MainMenu
          rolesConfig={rolesConfig}
          selectedRoleApi={selectedRoleApi}
          selectedAgentsCount={selectedAgentsCount}
          selectedAgents={selectedAgents}
          agentStatuses={agentStatuses}
          onRoleChange={handleRoleChange}
          onAgentsCountChange={handleAgentsCountChange}
          onAgentModelChange={handleAgentModelChange}
          onAgentAssignmentChange={handleAgentAssignmentChange}
          onAnalyze={handleAnalyze}
          isAnalyzing={isLoading}
          hasResources={resources.length > 0}
        />

        <section className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <ResourcesUpload
            resources={resources}
            onFileAdded={handleFileAdded}
            onUrlAdded={handleUrlAdded}
            onResourceRemoved={handleResourceRemoved}
            isDisabled={isLoading}
          />
        </section>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm flex items-center gap-2">
            <span>⚠️</span> {error}
          </div>
        )}

        <StatisticsSummary
          elapsed={stats.elapsed}
          totalTokens={stats.totalTokens}
          inputTokens={stats.inputTokens}
          outputTokens={stats.outputTokens}
          totalTokensAll={stats.totalTokensAll}
          inputTokensAll={stats.inputTokensAll}
          outputTokensAll={stats.outputTokensAll}
          cost={stats.cost}
          totalCost={stats.totalCost}
          currency={stats.currency}
          limit={limit}
          limitSettings={limitSettings}
          onLimitChange={handleLimitChange}
          onClearTokens={handleClearTokens}
          isAnalyzing={isLoading}
        />

        <section className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-100 min-h-[400px]">
            <AnalysisResult
              content={analysisResult}
              rolesConfig={rolesConfig}
              isLoading={isLoading}
              activeTab={activeTab}
              onTabChange={setActiveTab}
            />
          </div>
        </section>

        <JudgementResult
          key={judgementKey}
          content={analysisResult}
          activeTab={activeTab}
          agents={selectedAgents}
          availableModels={availableModels}
          onAnalysisResultUpdate={handleAnalysisResultUpdate}
          onStatsUpdate={handleStatsUpdate}
        />
      </main>

      {showReloadConfirm && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="bg-white border border-gray-200 rounded-lg shadow-2xl p-5 max-w-md mx-4">
            <div className="flex items-start gap-3 mb-4">
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  className="w-5 h-5 text-amber-600"
                >
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                  <line x1="12" y1="9" x2="12" y2="13" />
                  <line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-base font-semibold text-gray-900 mb-1">
                  Подтверждение обновления
                </h3>
                <p className="text-sm text-gray-600 leading-relaxed">
                  Вы уверены, что хотите обновить страницу? Данные анализа документов будут утеряны.
                </p>
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-gray-100">
              <button
                type="button"
                onClick={handleCancelReload}
                className="px-4 py-1.5 text-sm font-medium text-gray-700
                         bg-white border border-gray-300 rounded
                         hover:bg-gray-50 transition"
              >
                Отмена
              </button>
              <button
                type="button"
                onClick={handleConfirmReload}
                className="px-4 py-1.5 text-sm font-medium text-white
                         bg-amber-600 border border-amber-600 rounded
                         hover:bg-amber-700 transition"
              >
                Обновить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;