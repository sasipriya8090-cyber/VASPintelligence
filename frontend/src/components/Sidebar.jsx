import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Search,
  ArrowLeftRight,
  GitFork,
  FileText,
  Shield,
  Fingerprint,
  Database
} from 'lucide-react';

export default function Sidebar({ isOpen, setIsOpen }) {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Investigation', path: '/investigation', icon: Search },
    { name: 'Transactions', path: '/transactions', icon: ArrowLeftRight },
    { name: 'Wallet Graph', path: '/graph', icon: GitFork },
    { name: 'Reports', path: '/reports', icon: FileText },
  ];

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-40 w-64 bg-navy-900 border-r border-navy-750 flex flex-col transition-transform duration-300 ease-in-out md:translate-x-0 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      {/* Brand Header */}
      <div className="h-16 flex items-center px-5 border-b border-navy-750/80 bg-navy-950/40">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 text-white font-bold ring-1 ring-white/20">
            <Fingerprint className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-sm tracking-wider text-white uppercase block leading-tight">
              VASP<span className="text-cyan-400">intel</span>
            </span>
            <span className="text-[10px] text-slate-400 font-mono tracking-widest block uppercase">
              Attribution Engine
            </span>
          </div>
        </div>
      </div>

      {/* Nav List */}
      <div className="flex-1 py-6 px-3 space-y-1.5 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
          Core Intelligence
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              onClick={() => setIsOpen(false)}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/10 text-cyan-300 border-l-2 border-cyan-400 pl-[12px] shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-navy-800/60'
                }`
              }
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </div>

      {/* Environment / Engine Status Footer */}
      <div className="p-4 border-t border-navy-750/80 bg-navy-950/50">
        <div className="rounded-lg bg-navy-850 p-3 border border-navy-750">
          <div className="flex items-center justify-between text-xs mb-1.5">
            <span className="text-slate-400 text-[11px]">Engine Status</span>
            <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
              Online
            </span>
          </div>
          <div className="text-[11px] text-slate-300 font-mono truncate">
            Phase 1 • DEMO Mode
          </div>
          <div className="mt-2 pt-2 border-t border-navy-750 text-[10px] text-slate-400 flex items-center justify-between">
            <span>FastAPI + SQLite</span>
            <span className="text-cyan-400 font-mono">v1.0.0</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
