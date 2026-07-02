import React from 'react';

// 🔹 Форматирование числа с пробелами как разделителем разрядов (1 000, 25 500)
const formatNumber = (num) => {
  if (num == null) return '—';
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
};

// 🔹 Форматирование времени: секунды с 2 знаками ИЛИ "x мин y с"
const formatTime = (seconds) => {
  if (seconds == null || seconds === undefined) return '—';
  const totalSeconds = Number(seconds);
  if (isNaN(totalSeconds)) return '—';

  const mins = Math.floor(totalSeconds / 60);
  const secs = totalSeconds % 60;

  if (mins > 0) {
    return `${mins} мин ${Math.round(secs)} с`;
  }
  return `${totalSeconds.toFixed(2)} с`;
};

export default function StatisticsSummary({ elapsed, totalTokens, inputTokens, outputTokens }) {
  const hasTokens = totalTokens !== undefined && totalTokens !== null;

  return (
    <section className="bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2 text-sm text-gray-700">

        {/* 🔹 Блок "Потрачено токенов" — слева */}
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
          <span className="font-medium text-gray-500">Потрачено токенов:</span>
          <span className="font-mono text-gray-900">
            {hasTokens ? formatNumber(totalTokens) : '—'}
          </span>

          {hasTokens && (
            <span className="flex items-center gap-1 text-gray-600">
              (<span className="flex items-center gap-1">
                <span className="text-green-600" title="Входные токены">↑</span>
                <span className="font-mono">{formatNumber(inputTokens)}</span>
              </span>
              <span className="text-gray-400">/</span>
              <span className="flex items-center gap-1">
                <span className="text-blue-600" title="Выходные токены">↓</span>
                <span className="font-mono">{formatNumber(outputTokens)}</span>
              </span>)
            </span>
          )}
        </div>

        {/* 🔹 Блок "Первая генерация" — справа */}
        <div className="flex items-center gap-2">
          <span className="font-medium text-gray-500">Первая генерация:</span>
          <span className="font-mono text-gray-900">{formatTime(elapsed)}</span>
        </div>
      </div>
    </section>
  );
}