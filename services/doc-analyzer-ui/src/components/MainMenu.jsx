import React from 'react';

export default function MainMenu({
  rolesConfig,
  selectedRoleApi,
  selectedAgentsCount,
  selectedAgents,
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
  const availableAssignments = currentRole?.assignments || []; // 🔹 Динамические assignments
  const maxAgents = currentRole?.max_agents || 1;

  if (rolesConfig.length === 0) {
    return (
      <section className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm animate-pulse">
        <div className="h-20 bg-gray-100 rounded w-full"></div>
      </section>
    );
  }

  return (
    <section className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
      <div className="flex flex-wrap items-start gap-x-6 gap-y-4">

        {/* 🔹 ЛЕВАЯ КОЛОНКА: Роль и Агенты */}
        <div className="flex flex-col gap-3 shrink-0">
          <div className="flex items-center gap-2">
            <label htmlFor="role-select" className="text-sm font-medium text-gray-500 whitespace-nowrap">Роль:</label>
            <select
              id="role-select"
              value={selectedRoleApi}
              onChange={(e) => onRoleChange(e.target.value)}
              disabled={isAnalyzing}
              className="px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg
                       focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                       transition text-gray-900 text-sm disabled:opacity-60"
            >
              {rolesConfig.map(role => (
                <option key={role.api_param} value={role.api_param}>
                  {role.ui_title}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <label htmlFor="agents-count" className="text-sm font-medium text-gray-500 whitespace-nowrap">Агенты:</label>
            <select
              id="agents-count"
              value={selectedAgentsCount}
              onChange={(e) => onAgentsCountChange(Number(e.target.value))}
              disabled={isAnalyzing}
              className="px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg
                       focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                       transition text-gray-900 text-sm disabled:opacity-60 w-16"
            >
              {Array.from({ length: maxAgents }, (_, i) => i + 1).map(n => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>
        </div>

        {/* 🔹 ПРАВАЯ ЧАСТЬ: Мини-блоки агентов + Кнопка */}
        <div className="flex flex-wrap gap-3 flex-1">
          {Array.from({ length: selectedAgentsCount }, (_, idx) => {
            const agent = selectedAgents[idx] || {
              model: availableModels[0]?.name || '',
              assignment: availableAssignments[0]?.api_param || ''
            };

            return (
              <div key={idx} className="flex flex-col gap-1 p-2 bg-gray-50 rounded-lg border border-gray-200">
                <span className="text-xs font-medium text-gray-500">Агент {idx + 1}</span>

                {/* Дропдаун модели */}
                <select
                  value={agent.model}
                  onChange={(e) => onAgentModelChange(idx, e.target.value)}
                  disabled={isAnalyzing || availableModels.length === 0}
                  className="px-2 py-1.5 bg-white border border-gray-300 rounded
                           focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                           transition text-gray-900 text-xs disabled:opacity-60 min-w-[140px]"
                >
                  {availableModels.map(model => (
                    <option key={`${model.provider}-${model.name}`} value={model.name}>
                      {model.name}
                    </option>
                  ))}
                </select>

                {/* 🔹 Дропдаун назначения (динамический из assignments) */}
                <select
                  value={agent.assignment}
                  onChange={(e) => onAgentAssignmentChange(idx, e.target.value)}
                  disabled={isAnalyzing || availableAssignments.length === 0}
                  className="px-2 py-1.5 bg-white border border-gray-300 rounded
                           focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
                           transition text-gray-900 text-xs disabled:opacity-60 min-w-[140px]"
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

        {/* 🔹 Кнопка "Анализ" (прижата вправо) */}
        <button
          onClick={onAnalyze}
          disabled={isAnalyzing || !hasResources}
          className="ml-auto shrink-0 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400
                   disabled:cursor-not-allowed rounded-lg font-medium text-white
                   transition-all shadow-sm flex items-center gap-2 whitespace-nowrap h-fit mt-0.5"
        >
          {isAnalyzing ? (
            <>
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"/>
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