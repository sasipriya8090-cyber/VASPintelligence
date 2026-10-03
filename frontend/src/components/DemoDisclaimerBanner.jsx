import React from 'react';
import { AlertTriangle, ShieldAlert } from 'lucide-react';

export default function DemoDisclaimerBanner({ compact = false }) {
  if (compact) {
    return (
      <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-medium tracking-wide">
        <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0 text-amber-400" />
        <span>DEMO DATA — NOT LIVE BLOCKCHAIN DATA</span>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-amber-500/15 via-amber-500/10 to-transparent border-l-4 border-amber-500 border-y border-r border-amber-500/20 px-4 py-3 rounded-r-lg mb-6 flex items-center justify-between shadow-lg shadow-black/20">
      <div className="flex items-center space-x-3">
        <div className="p-2 rounded-lg bg-amber-500/20 text-amber-400">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="font-semibold text-amber-300 text-sm tracking-wide">
              DEMO DATA — NOT LIVE BLOCKCHAIN DATA
            </span>
            <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-amber-500/25 text-amber-200">
              Phase 1 MVP
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Synthetic transactions, heuristic indicators, and mock VASP entity attributions for testing and prototype validation only.
          </p>
        </div>
      </div>
      <div className="hidden md:flex text-[11px] text-amber-400/80 font-mono bg-navy-900/60 px-2 py-1 rounded border border-amber-500/20">
        ENVIRONMENT: DEMO
      </div>
    </div>
  );
}
