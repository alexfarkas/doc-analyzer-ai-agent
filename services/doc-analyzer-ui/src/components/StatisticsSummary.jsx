// src/components/StatisticsSummary.jsx
import React, { useState, useMemo } from 'react';

const MAX_PYTHON_INT = '9223372036854775807';

const formatNumber = (num) => {
  if (num == null || num === undefined) return '—';
  const numValue = Number(num);
  if (isNaN(numValue)) return '—';
  return numValue.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
};

const formatCost = (num) => {
  if (num == null || num === undefined || num === '') return '—';
  const numValue = Number(num);
  if (isNaN(numValue)) return '—';
  return numValue
    .toFixed(2)
    .replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
    .replace('.', ',');
};

const formatTime = (seconds) => {
  if (seconds == null || seconds === undefined || Number(seconds) === 0) {
    return '—';
  }

  const totalSeconds = Number(seconds);
  if (isNaN(totalSeconds) || totalSeconds <= 0) return '—';

  const mins = Math.floor(totalSeconds / 60);
  const secs = totalSeconds % 60;

  if (mins > 0) {
    return `${mins} мин ${Math.round(secs)} с`;
  }
  return `${totalSeconds.toFixed(2)} с`;
};

export default function StatisticsSummary({
  elapsed,
  totalTokens,
  inputTokens,
  outputTokens,
  totalTokensAll,
  inputTokensAll,
  outputTokensAll,
  cost,
  totalCost,
  currency,
  limit,
  limitSettings,
  onLimitChange,
  onClearTokens,
  isAnalyzing = false
}) {
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const [isClearing, setIsClearing] = useState(false);
  const [clearError, setClearError] = useState('');

  const hasSpentTokens = Number(totalTokens) > 0;
  const hasTotalTokens = Number(totalTokensAll) > 0;
  const hasCost = Number(cost) > 0;
  const hasTotalCost = Number(totalCost) > 0;
  const hasCostData = hasTotalTokens || hasTotalCost;

  const totalTokensColorClass = useMemo(() => {
    if (!hasTotalTokens) return 'text-gray-900';
    if (!limit || limit === '' || limit === null || limit === undefined) return 'text-gray-900';

    let limitValue = typeof limit === 'string' ? parseInt(limit, 10) : limit;
    if (isNaN(limitValue) || !isFinite(limitValue) || limitValue <= 0) return 'text-gray-900';

    let totalTokensValue = typeof totalTokensAll === 'string' ? parseInt(totalTokensAll, 10) : totalTokensAll;
    if (isNaN(totalTokensValue) || !isFinite(totalTokensValue)) return 'text-gray-900';

    if (totalTokensValue >= limitValue) return 'text-red-600';
    if (!limitSettings || limitSettings === null || limitSettings === undefined) return 'text-gray-900';

    const diff = limitValue - totalTokensValue;

    if (limitSettings.limit_threshold_mode === 'abs_value') {
      let threshold = typeof limitSettings.limit_warning_threshold === 'string'
        ? parseInt(limitSettings.limit_warning_threshold, 10)
        : limitSettings.limit_warning_threshold;
      if (!isNaN(threshold) && isFinite(threshold) && threshold > 0 && diff <= threshold) {
        return 'text-yellow-600';
      }
      return 'text-gray-900';
    }

    if (limitSettings.limit_threshold_mode === 'percent') {
      let thresholdPc = typeof limitSettings.limit_warning_threshold_pc === 'string'
        ? parseInt(limitSettings.limit_warning_threshold_pc, 10)
        : limitSettings.limit_warning_threshold_pc;
      if (!isNaN(thresholdPc) && isFinite(thresholdPc) && thresholdPc > 0 && limitValue > 0) {
        const currentPc = (diff * 100) / limitValue;
        if (!isNaN(currentPc) && isFinite(currentPc) && currentPc <= thresholdPc) {
          return 'text-yellow-600';
        }
      }
      return 'text-gray-900';
    }

    return 'text-gray-900';
  }, [hasTotalTokens, limit, totalTokensAll, limitSettings]);

  const handleLimitChange = (e) => {
    const value = e.target.value;
    if (value === '') { onLimitChange(''); return; }
    if (!/^\d+$/.test(value)) return;
    try {
      if (BigInt(value) > BigInt(MAX_PYTHON_INT)) return;
    } catch { return; }
    onLimitChange(value);
  };

  const handleLimitPaste = (e) => {
    e.preventDefault();
    const pastedText = (e.clipboardData || window.clipboardData).getData('text');
    if (pastedText === '') { onLimitChange(''); return; }
    if (!/^\d+$/.test(pastedText)) return;
    try {
      if (BigInt(pastedText) > BigInt(MAX_PYTHON_INT)) return;
    } catch { return; }
    onLimitChange(pastedText);
  };

  const handleLimitKeyDown = (e) => {
    const allowedKeys = ['Backspace', 'Delete', 'Tab', 'Escape', 'Enter', 'Home', 'End', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'];
    if (allowedKeys.includes(e.key) || e.ctrlKey || e.metaKey) return;
    if (!/^\d$/.test(e.key)) e.preventDefault();
  };

  const handleClearClick = () => {
    setClearError('');
    setShowClearConfirm(true);
  };

  const handleConfirmClear = async () => {
    setIsClearing(true);
    setClearError('');
    try {
      const result = await onClearTokens?.();
      if (result?.success) {
        setShowClearConfirm(false);
      } else {
        setClearError(result?.error || 'Не удалось очистить данные');
      }
    } catch (err) {
      setClearError(err.message || 'Неизвестная ошибка');
    } finally {
      setIsClearing(false);
    }
  };

  const handleCancelClear = () => {
    if (isClearing) return;
    setClearError('');
    setShowClearConfirm(false);
  };

  return (
    <section className="card p-4 relative">
      <div className="space-y-2 text-sm text-gray-700">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
          <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
            <span className="label-text">Потрачено токенов:</span>
            <span className="text-mono text-gray-900">
              {hasSpentTokens ? formatNumber(totalTokens) : '—'}
            </span>

            {hasSpentTokens ? (
              <span className="flex items-center gap-1 text-gray-600">
                (<span className="flex items-center gap-1">
                  <span className="text-green-600" title="Входные токены">↑</span>
                  <span className="text-mono">{formatNumber(inputTokens)}</span>
                </span>
                <span className="text-gray-400">/</span>
                <span className="flex items-center gap-1">
                  <span className="text-blue-600" title="Выходные токены">↓</span>
                  <span className="text-mono">{formatNumber(outputTokens)}</span>
                </span>)
              </span>
            ) : (
              <span className="text-gray-400 text-mono text-xs ml-1">(— / —)</span>
            )}

            {hasCost && (
              <span className="text-mono text-gray-700">
                [{formatCost(cost)} {currency}]
              </span>
            )}
          </div>

          <div className="flex items-center gap-2 ml-auto">
            <span className="label-text">Первая генерация:</span>
            <span className="text-mono text-gray-900">{formatTime(elapsed)}</span>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-x-2 gap-y-2">
          <div className="flex flex-wrap items-center gap-x-2 gap-y-1">
            <span className="label-text">Всего токенов:</span>
            <span
              className={`text-mono transition-colors duration-300 ${totalTokensColorClass}`}
              title={hasTotalTokens ? `Точное значение: ${totalTokensAll}` : undefined}
            >
              {hasTotalTokens ? formatNumber(totalTokensAll) : '—'}
            </span>

            {hasTotalTokens ? (
              <span className="flex items-center gap-1 text-gray-600">
                (<span className="flex items-center gap-1">
                  <span className="text-green-600" title="Входные токены">↑</span>
                  <span className="text-mono">{formatNumber(inputTokensAll)}</span>
                </span>
                <span className="text-gray-400">/</span>
                <span className="flex items-center gap-1">
                  <span className="text-blue-600" title="Выходные токены">↓</span>
                  <span className="text-mono">{formatNumber(outputTokensAll)}</span>
                </span>)
              </span>
            ) : (
              <span className="text-gray-400 text-mono text-xs ml-1">(— / —)</span>
            )}

            {hasTotalCost && (
              <span className="text-mono text-gray-700">
                [{formatCost(totalCost)} {currency}]
              </span>
            )}
          </div>

          {hasCostData && (
            <button
              type="button"
              onClick={handleClearClick}
              title="Очистить накопленные данные о токенах и стоимости"
              className="flex items-center justify-center w-7 h-7 rounded-md
                       text-gray-400 hover:text-red-600 hover:bg-red-50
                       transition-all duration-150 ml-1"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4">
                <path d="M3 6h18" />
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6" />
                <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                <line x1="10" y1="11" x2="10" y2="17" />
                <line x1="14" y1="11" x2="14" y2="17" />
              </svg>
            </button>
          )}

          <div className="flex items-center gap-2 ml-8">
            <span className="label-text">Лимит:</span>
            <input
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              value={limit ?? ''}
              onChange={handleLimitChange}
              onPaste={handleLimitPaste}
              onKeyDown={handleLimitKeyDown}
              disabled={isAnalyzing}
              className="input-base input-mono w-28 py-1"
            />
          </div>
        </div>
      </div>

      {showClearConfirm && (
        <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/80 backdrop-blur-sm rounded-lg">
          <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-4 max-w-sm mx-4">
            <p className="text-sm text-gray-700 mb-4">
              Вы уверены, что хотите очистить накопленные данные о количестве токенов и стоимости?
            </p>

            {clearError && (
              <div className="mb-3 px-3 py-2 bg-red-50 border border-red-200 rounded text-xs text-red-700 flex items-center gap-2">
                <span>⚠️</span>
                <span>{clearError}</span>
              </div>
            )}

            <div className="flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={handleCancelClear}
                disabled={isClearing}
                className="px-3 py-1.5 text-sm font-medium text-gray-700
                         bg-white border border-gray-300 rounded
                         hover:bg-gray-50 transition
                         disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Отмена
              </button>
              <button
                type="button"
                onClick={handleConfirmClear}
                disabled={isClearing}
                className="px-3 py-1.5 text-sm font-medium text-white
                         bg-red-600 border border-red-600 rounded
                         hover:bg-red-700 transition
                         disabled:opacity-70 disabled:cursor-not-allowed
                         flex items-center gap-2"
              >
                {isClearing ? (
                  <>
                    <span className="spinner-white" style={{ width: '0.75rem', height: '0.75rem' }}/>
                    Очистка...
                  </>
                ) : (
                  'Очистить'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}