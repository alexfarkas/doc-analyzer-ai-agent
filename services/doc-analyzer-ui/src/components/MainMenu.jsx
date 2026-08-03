import React from 'react';

export default function MainMenu({
  rolesConfig,
  selectedRoleApi,
  selectedAgentsCount,
  selectedAgents,
  agentStatuses = {},
  onRoleChange,
  onAgentsCountChange,
  onAgentModelChange,
  onAgentAssignmentChange,
  onAnalyze,
  isAnalyzing,
  hasResources
}) {
  const currentRole = rolesConfig.find(r => r.api_param === selectedRoleApi);
  const availableModels = currentRole?.models || [];
  const availableAssignments = currentRole?.assignments || [];
  const maxAgents = currentRole?.max_agents || 1;

  if (rolesConfig.length === 0) {
    return (
      <section className="card p-4 animate-pulse">
        <div className="h-20 bg-gray-100 rounded w-full"></div>
      </section>
    );
  }

  return (
    <section className="card p-4">
      <div className="flex flex-wrap items-start gap-x-6 gap-y-4">
        <div className="flex flex-col gap-3 shrink-0">
          <div className="flex items-center gap-2">
            <label htmlFor="role-select" className="label-text">Роль:</label>
            <select
              id="role-select"
              value={selectedRoleApi}
              onChange={(e) => onRoleChange(e.target.value)}
              disabled={isAnalyzing}
              className="input-base"
            >
              {rolesConfig.map(role => (
                <option key={role.api_param} value={role.api_param}>
                  {role.ui_title}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label htmlFor="agents-count" className="label-text">Агенты:</label>
            <select
              id="agents-count"
              value={selectedAgentsCount}
              onChange={(e) => onAgentsCountChange(Number(e.target.value))}
              disabled={isAnalyzing}
              className="input-base w-16"
            >
              {Array.from({ length: maxAgents }, (_, i) => i + 1).map(n => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex flex-wrap gap-3 flex-1">
          {Array.from({ length: selectedAgentsCount }, (_, idx) => {
            const agent = selectedAgents[idx] || {
              model: availableModels[0]?.name || '',
              assignment: availableAssignments[0]?.api_param || ''
            };

            const agentId = idx + 1;
            const agentStatus = agentStatuses[agentId] || 'idle';

            return (
              <div
                key={idx}
                className={`agent-card-base ${
                  agentStatus === 'loading' ? 'agent-card-loading' : 
                  agentStatus === 'done' ? 'agent-card-done' : 'agent-card-idle'
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-gray-500">Агент {idx + 1}</span>

                  {agentStatus === 'loading' && (
                    <span className="flex items-center gap-1">
                      <span className="spinner-indigo" style={{ width: '0.75rem', height: '0.75rem' }}/>
                      <span className="text-xs font-medium text-accent-primary">Работает</span>
                    </span>
                  )}
                  {agentStatus === 'done' && (
                    <span className="flex items-center gap-1">
                      <svg className="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className="text-xs font-medium text-green-600">Готов</span>
                    </span>
                  )}
                </div>

                <select
                  value={agent.model}
                  onChange={(e) => onAgentModelChange(idx, e.target.value)}
                  disabled={isAnalyzing || availableModels.length === 0}
                  className="input-base min-w-[140px] py-1.5"
                >
                  {availableModels.map(model => (
                    <option key={`${model.provider}-${model.name}`} value={model.name}>
                      {model.name}
                    </option>
                  ))}
                </select>

                <select
                  value={agent.assignment}
                  onChange={(e) => onAgentAssignmentChange(idx, e.target.value)}
                  disabled={isAnalyzing || availableAssignments.length === 0}
                  className="input-base min-w-[140px] py-1.5"
                >
                  {availableAssignments.map(assgn => (
                    <option key={assgn.api_param} value={assgn.api_param}>
                      {assgn.ui_title}
                    </option>
                  ))}
                </select>
              </div>
            );
          })}
        </div>

        <button
          onClick={onAnalyze}
          disabled={isAnalyzing || !hasResources}
          className="btn-primary ml-auto shrink-0 h-fit mt-0.5"
        >
          {isAnalyzing ? (
            <>
              <span className="spinner-white"/>
              Анализ...
            </>
          ) : (
            <>🔍 Анализ</>
          )}
        </button>
      </div>
    </section>
  );
}