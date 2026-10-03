import React from 'react';

export default function RiskBadge({ level = 'LOW', score = null, size = 'sm' }) {
  const normLevel = (level || 'LOW').toUpperCase();

  const configs = {
    LOW: {
      bg: 'bg-emerald-500/15',
      text: 'text-emerald-400',
      border: 'border-emerald-500/30',
      dot: 'bg-emerald-400',
      label: 'LOW RISK'
    },
    MEDIUM: {
      bg: 'bg-amber-500/15',
      text: 'text-amber-400',
      border: 'border-amber-500/30',
      dot: 'bg-amber-400',
      label: 'MEDIUM RISK'
    },
    HIGH: {
      bg: 'bg-rose-500/15',
      text: 'text-rose-400',
      border: 'border-rose-500/30',
      dot: 'bg-rose-400',
      label: 'HIGH RISK'
    },
    CRITICAL: {
      bg: 'bg-red-600/20',
      text: 'text-red-400',
      border: 'border-red-500/40',
      dot: 'bg-red-500 animate-pulse',
      label: 'CRITICAL RISK'
    }
  };

  const current = configs[normLevel] || configs.LOW;

  const sizeStyles = {
    xs: 'text-[10px] px-2 py-0.5',
    sm: 'text-xs px-2.5 py-1',
    md: 'text-sm px-3 py-1.5'
  };

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-semibold border ${current.bg} ${current.text} ${current.border} ${sizeStyles[size] || sizeStyles.sm} tracking-wide`}>
      <span className={`w-1.5 h-1.5 rounded-full ${current.dot}`}></span>
      <span>{current.label}</span>
      {score !== null && (
        <span className="ml-1 pl-1 border-l border-current/20 font-mono text-[11px] opacity-90">
          {score}
        </span>
      )}
    </span>
  );
}
