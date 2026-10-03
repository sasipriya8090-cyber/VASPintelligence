import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { Shield, Building2, Wallet, AlertCircle } from 'lucide-react';
import RiskBadge from './RiskBadge';

function CustomNode({ data, selected }) {
  const isVASP = data.isVASP;
  const isTarget = data.isTarget;

  return (
    <div
      className={`min-w-[220px] rounded-xl border bg-navy-900/95 backdrop-blur-md p-3.5 shadow-2xl transition-all ${
        selected ? 'ring-2 ring-cyan-400 border-cyan-400 shadow-cyan-500/20' : 'border-navy-700 hover:border-navy-600'
      } ${isTarget ? 'border-amber-500/60 bg-gradient-to-b from-navy-900 to-amber-950/20' : ''}`}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="w-2.5 h-2.5 !bg-cyan-400 !border-2 !border-navy-900"
      />

      {/* Node Header */}
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2">
          <div
            className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs ${
              isVASP
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : isTarget
                ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                : 'bg-navy-800 text-slate-400 border border-navy-700'
            }`}
          >
            {isVASP ? (
              <Building2 className="w-3.5 h-3.5" />
            ) : isTarget ? (
              <AlertCircle className="w-3.5 h-3.5" />
            ) : (
              <Wallet className="w-3.5 h-3.5" />
            )}
          </div>
          <div>
            <div className="text-xs font-bold text-slate-100 truncate max-w-[130px]">
              {data.label}
            </div>
            <div className="text-[10px] text-slate-400 truncate max-w-[130px]">
              {data.role || 'Entity'}
            </div>
          </div>
        </div>
      </div>

      {/* Address & Risk Badge */}
      <div className="pt-2 border-t border-navy-800 flex items-center justify-between text-xs">
        <div className="font-mono text-[11px] text-slate-400 bg-navy-950 px-2 py-0.5 rounded border border-navy-800">
          {data.sublabel}
        </div>
        <RiskBadge level={data.riskLevel} score={data.riskScore} size="xs" />
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="w-2.5 h-2.5 !bg-cyan-400 !border-2 !border-navy-900"
      />
    </div>
  );
}

export default memo(CustomNode);
