import React from 'react';
import { Menu, Shield, Activity, Bell, Terminal } from 'lucide-react';
import DemoDisclaimerBanner from './DemoDisclaimerBanner';

export default function Header({ onMenuClick }) {
  return (
    <header className="h-16 bg-navy-900/90 backdrop-blur-md border-b border-navy-750 px-4 md:px-8 flex items-center justify-between sticky top-0 z-30">
      {/* Left: Mobile hamburger + Project branding badge */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onMenuClick}
          className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-navy-800 md:hidden"
          aria-label="Toggle navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-cyan-400 hidden sm:block" />
          <h1 className="text-xs sm:text-sm font-semibold tracking-wide text-slate-200">
            Automated Blockchain Intelligence & VASP Attribution Engine
          </h1>
        </div>
      </div>

      {/* Right: Disclaimer badge + System metrics */}
      <div className="flex items-center space-x-3 sm:space-x-4">
        <DemoDisclaimerBanner compact={true} />

        <div className="hidden lg:flex items-center space-x-2 text-xs font-mono text-slate-400 bg-navy-950/80 px-3 py-1.5 rounded-md border border-navy-750">
          <Activity className="w-3.5 h-3.5 text-cyan-400" />
          <span>ETH ADAPTER:</span>
          <span className="text-emerald-400 font-semibold">ACTIVE (DEMO)</span>
        </div>

        <div className="flex items-center pl-2 border-l border-navy-750">
          <div className="w-8 h-8 rounded-full bg-cyan-600/20 border border-cyan-500/30 flex items-center justify-center text-cyan-300 text-xs font-bold font-mono">
            LE
          </div>
        </div>
      </div>
    </header>
  );
}
