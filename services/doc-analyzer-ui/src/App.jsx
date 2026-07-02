import { useState, useEffect, useCallback, useRef } from 'react';
import MainMenu from './components/MainMenu';
import ResourcesUpload from './components/ResourcesUpload';
import StatisticsSummary from './components/StatisticsSummary';
import AnalysisResult from './components/AnalysisResult';
import JudgementResult from './components/JudgementResult';

const STORAGE_KEY = 'doc_analyzer_selection_v3';

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
    outputTokens: null
  });

  const [judgementKey, setJudgementKey] = useState(0);

  // 🔹 НОВОЕ: Объект статусов агентов { [agentId]: 'idle' | 'loading' | 'done' }
  const [agentStatuses, setAgentStatuses] = useState({});

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

  const handleStatsUpdate = useCallback((usage) => {
    if (!usage) return;
    setStats(prev => ({
      ...prev,
      totalTokens: usage.total_tokens,
      inputTokens: usage.input_tokens,
      outputTokens: usage.output_tokens
    }));
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
    setStats({ elapsed: null, totalTokens: null, inputTokens: null, outputTokens: null });
    setJudgementKey(prev => prev + 1);

    // 🔹 Инициализируем статусы всех агентов как 'idle'
    // agentId начинается с 1, индекс в selectedAgents = agentId - 1
    const initialStatuses = {};
    for (let i = 0; i < selectedAgentsCount; i++) {
      initialStatuses[i + 1] = 'idle';
    }
    setAgentStatuses(initialStatuses);

    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch('/api/doc/analyze/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          resources: resources.map(r => r.path),
          role: selectedRoleApi,
          agents: selectedAgents.map(a => ({
            model: a.model,
            assignment: a.assignment
          }))
        }),
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
                  // 🔹 Обновляем статус конкретного агента по его id
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

                  const normalizedResult = resultArray.map(item => {
                    if (typeof item === 'string') return { answer: item, score: undefined, judgement: undefined };
                    return {
                      answer: item.answer ?? '',
                      score: item.score,
                      judgement: item.judgement
                    };
                  });

                  setAnalysisResult(normalizedResult);

                  if (data.token_usage) {
                    setStats({
                      elapsed: data.elapsed,
                      totalTokens: data.token_usage.total_tokens || 0,
                      inputTokens: data.token_usage.input_tokens || 0,
                      outputTokens: data.token_usage.output_tokens || 0
                    });
                  } else if (data.elapsed != null) {
                    setStats(prev => ({ ...prev, elapsed: data.elapsed }));
                  }
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
      // Сбрасываем статусы всех агентов в исходное состояние
      // после завершения анализа (успешного или с ошибкой)
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
        />

        <section className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-100 min-h-[400px]">
            <AnalysisResult
              content={analysisResult}
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
    </div>
  );
}

export default App;