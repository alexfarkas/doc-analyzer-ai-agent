// src/App.jsx
import { useState, useEffect, useCallback } from 'react';
import MainMenu from './components/MainMenu';
import ResourcesUpload from './components/ResourcesUpload';
import AnalysisResult from './components/AnalysisResult';
import JudgementResult from './components/JudgementResult';
import StatisticsSummary from './components/StatisticsSummary';
import { apiFetch, apiStream } from './utils/api';
import './App.css';

export default function App() {
  const [rolesConfig, setRolesConfig] = useState([]);
  const [limitSettings, setLimitSettings] = useState(null);
  const [isSessionInitialized, setIsSessionInitialized] = useState(false);

  const [selectedRoleApi, setSelectedRoleApi] = useState('');
  const [selectedAgentsCount, setSelectedAgentsCount] = useState(1);
  const [selectedAgents, setSelectedAgents] = useState([]);
  const [resources, setResources] = useState([]);
  const [limit, setLimit] = useState(() => localStorage.getItem('doc_analyzer_limit') || '');

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysisResult, setAnalysisResult] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const [agentStatuses, setAgentStatuses] = useState({});

  const [stats, setStats] = useState({
    elapsed: 0,
    inputTokens: 0,
    outputTokens: 0,
    totalTokens: 0,
    inputTokensAll: 0,
    outputTokensAll: 0,
    totalTokensAll: 0,
    cost: 0,
    totalCost: 0,
    currency: 'RUB',
  });

  useEffect(() => {
    const initApp = async () => {
      try {
        await apiFetch('/sessions/current');
        setIsSessionInitialized(true);

        const config = await apiFetch('/config');
        setRolesConfig(config.roles);
        setLimitSettings(config.limit_settings);

        if (config.roles.length > 0) {
          const defaultRole = config.roles[0].api_param;
          setSelectedRoleApi(defaultRole);
          setSelectedAgentsCount(1);
          setSelectedAgents([{
            model: config.roles[0].models[0]?.name || '',
            assignment: config.roles[0].assignments[0]?.api_param || ''
          }]);
        }

        await loadTotalStats();
      } catch (err) {
        console.error('Init error:', err);
        setError('Не удалось инициализировать приложение. Проверьте подключение к бэкенду.');
      }
    };
    initApp();
  }, []);

  const loadTotalStats = useCallback(async () => {
    try {
      const data = await apiFetch('/tokens/total');
      setStats(prev => ({
        ...prev,
        inputTokensAll: data.total_token_usage?.input_tokens || 0,
        outputTokensAll: data.total_token_usage?.output_tokens || 0,
        totalTokensAll: data.total_token_usage?.total_tokens || 0,
        totalCost: data.total_cost || 0,
      }));
    } catch (err) {
      console.error('Failed to load total stats:', err);
    }
  }, []);

  const handleRoleChange = (roleApi) => {
    setSelectedRoleApi(roleApi);
    setSelectedAgentsCount(1);
    const role = rolesConfig.find(r => r.api_param === roleApi);
    if (role) {
      setSelectedAgents([{
        model: role.models[0]?.name || '',
        assignment: role.assignments[0]?.api_param || ''
      }]);
    }
    setAnalysisResult([]);
    setActiveTab(0);
  };

  const handleAgentsCountChange = (count) => {
    setSelectedAgentsCount(count);
    const role = rolesConfig.find(r => r.api_param === selectedRoleApi);
    const newAgents = Array.from({ length: count }, (_, i) => {
      return selectedAgents[i] || {
        model: role?.models[0]?.name || '',
        assignment: role?.assignments[0]?.api_param || ''
      };
    });
    setSelectedAgents(newAgents);
  };

  const handleAgentModelChange = (index, model) => {
    const newAgents = [...selectedAgents];
    newAgents[index] = { ...newAgents[index], model };
    setSelectedAgents(newAgents);
  };

  const handleAgentAssignmentChange = (index, assignment) => {
    const newAgents = [...selectedAgents];
    newAgents[index] = { ...newAgents[index], assignment };
    setSelectedAgents(newAgents);
  };

  const handleResourceAdded = (id, name, type) => {
    setResources(prev => [...prev, { id, name, type }]);
  };

  const handleResourceRemoved = (id) => {
    setResources(prev => prev.filter(r => r.id !== id));
  };

  const handleLimitChange = (value) => {
    setLimit(value);
    localStorage.setItem('doc_analyzer_limit', value);
  };

  const handleClearTokens = async () => {
    try {
      await apiFetch('/tokens/clear', { method: 'POST' });
      setStats(prev => ({
        ...prev,
        inputTokens: 0, outputTokens: 0, totalTokens: 0,
        inputTokensAll: 0, outputTokensAll: 0, totalTokensAll: 0,
        cost: 0, totalCost: 0,
      }));
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message };
    }
  };

  const handleAnalyze = async () => {
    if (resources.length === 0) return;
    setIsLoading(true);
    setError(null);
    setAnalysisResult([]);
    setActiveTab(0);
    setAgentStatuses({});

    setStats(prev => ({ ...prev, inputTokens: 0, outputTokens: 0, totalTokens: 0, cost: 0, elapsed: 0 }));

    const payload = {
      resources: resources.map(r => r.id),
      role: selectedRoleApi,
      agents: selectedAgents,
      limit: limit ? parseInt(limit, 10) : null,
    };

    try {
      const response = await apiStream('/doc/analyze/stream', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let currentEvent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            currentEvent = line.slice(7).trim();
          } else if (line.startsWith('data: ')) {
            const dataStr = line.slice(6).trim();
            if (!dataStr) continue;

            try {
              const data = JSON.parse(dataStr);

              if (currentEvent === 'agent_start') {
                setAgentStatuses(prev => ({ ...prev, [data.agentId]: 'loading' }));
              } else if (currentEvent === 'agent_end') {
                setAgentStatuses(prev => ({ ...prev, [data.agentId]: 'done' }));
              } else if (currentEvent === 'complete') {
                if (data.result) setAnalysisResult(data.result);

                if (data.total_token_usage) {
                  setStats(prev => ({
                    ...prev,
                    inputTokensAll: data.total_token_usage.input_tokens || 0,
                    outputTokensAll: data.total_token_usage.output_tokens || 0,
                    totalTokensAll: data.total_token_usage.total_tokens || 0,
                  }));
                }
                if (data.total_cost !== undefined) {
                  setStats(prev => ({ ...prev, totalCost: data.total_cost }));
                }
                if (data.token_usage) {
                  setStats(prev => ({
                    ...prev,
                    inputTokens: data.token_usage.input_tokens || 0,
                    outputTokens: data.token_usage.output_tokens || 0,
                    totalTokens: data.token_usage.total_tokens || 0,
                  }));
                }
                if (data.cost !== undefined) {
                  setStats(prev => ({ ...prev, cost: data.cost }));
                }
                if (data.elapsed !== undefined) {
                  setStats(prev => ({ ...prev, elapsed: data.elapsed }));
                }
              } else if (currentEvent === 'error') {
                throw new Error(data.message || 'Ошибка анализа');
              }
            } catch (e) {
              console.warn('SSE parse error:', e, dataStr);
            }
          }
        }
      }
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalysisResultUpdate = useCallback((agentIndex, newData) => {
    setAnalysisResult(prev => {
      const next = [...prev];
      next[agentIndex] = { ...next[agentIndex], ...newData };
      return next;
    });
  }, []);

  const handleStatsUpdate = useCallback((usage, totalUsage) => {
    setStats(prev => ({
      ...prev,
      inputTokens: usage?.input_tokens || 0,
      outputTokens: usage?.output_tokens || 0,
      totalTokens: usage?.total_tokens || 0,
      inputTokensAll: totalUsage?.input_tokens || prev.inputTokensAll,
      outputTokensAll: totalUsage?.output_tokens || prev.outputTokensAll,
      totalTokensAll: totalUsage?.total_tokens || prev.totalTokensAll,
    }));
  }, []);

  if (!isSessionInitialized) {
    return (
      <div className="flex h-screen items-center justify-center text-gray-500">
        <span className="spinner-indigo mr-2"/>
        Инициализация сессии...
      </div>
    );
  }

  const currentRole = rolesConfig.find(r => r.api_param === selectedRoleApi);

  return (
    <div className="app-root">
      <header className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
        <h1 className="app-title">Doc Analyzer AI</h1>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

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

        <ResourcesUpload
          resources={resources}
          onFileAdded={(id, name) => handleResourceAdded(id, name, 'file')}
          onUrlAdded={(url) => handleResourceAdded(url, url, 'url')}
          onResourceRemoved={handleResourceRemoved}
          isDisabled={isLoading}
        />

        <StatisticsSummary
          elapsed={stats.elapsed}
          inputTokens={stats.inputTokens}
          outputTokens={stats.outputTokens}
          totalTokens={stats.totalTokens}
          inputTokensAll={stats.inputTokensAll}
          outputTokensAll={stats.outputTokensAll}
          totalTokensAll={stats.totalTokensAll}
          cost={stats.cost}
          totalCost={stats.totalCost}
          currency={stats.currency}
          limit={limit}
          limitSettings={limitSettings}
          onLimitChange={handleLimitChange}
          onClearTokens={handleClearTokens}
          isAnalyzing={isLoading}
        />

        <div className="card min-h-[500px] flex flex-col">
          <AnalysisResult
            content={analysisResult}
            rolesConfig={rolesConfig}
            isLoading={isLoading}
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />
        </div>

        {analysisResult && analysisResult.length > 0 && (
          <JudgementResult
            content={analysisResult}
            activeTab={activeTab}
            agents={selectedAgents}
            availableModels={currentRole?.models || []}
            onAnalysisResultUpdate={handleAnalysisResultUpdate}
            onStatsUpdate={handleStatsUpdate}
          />
        )}
      </main>
    </div>
  );
}