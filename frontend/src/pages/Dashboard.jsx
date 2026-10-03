import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  Briefcase,
  Building2,
  Clock,
  ArrowUpRight,
  Search,
  ExternalLink,
  RefreshCw,
  AlertTriangle,
  ChevronRight,
  ShieldCheck,
  Activity
} from 'lucide-react';
import api from '../services/api';
import RiskBadge from '../components/RiskBadge';
import DemoDisclaimerBanner from '../components/DemoDisclaimerBanner';

export default function Dashboard() {
  const navigate = useNavigate();
  const [investigations, setInvestigations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quickAddress, setQuickAddress] = useState('');

  const fetchCases = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getInvestigations();
      setInvestigations(data || []);
    } catch (err) {
      console.error('Failed to load investigations:', err);
      setError(err.message || 'Failed to fetch investigation records');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, []);

  const handleQuickAnalyze = (e) => {
    e.preventDefault();
    if (!quickAddress.trim()) return;
    navigate(`/investigation?address=${encodeURIComponent(quickAddress.trim())}`);
  };

  // Compute stats
  const totalCases = investigations.length;
  const highRiskCases = investigations.filter(
    (inv) => inv.case?.risk_level === 'HIGH' || inv.case?.risk_level === 'CRITICAL'
  ).length;
  const vaspMatches = 8; // Synthetic Phase 1 demo directory matches
  const recentInvestigationsCount = investigations.length;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <DemoDisclaimerBanner />

      {/* Hero Section */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-gradient-to-br from-navy-900 via-navy-850 to-navy-900 border border-navy-750 p-6 rounded-2xl shadow-xl">
        <div className="space-y-1.5">
          <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
            CYBER FORENSICS & FINANCIAL SURVEILLANCE
          </div>
          <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
            Automated Blockchain Intelligence & VASP Attribution Engine
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 max-w-2xl leading-relaxed">
            Automated transaction path tracing, risk classification, and exchange attribution for financial investigators and compliance authorities.
          </p>
        </div>

        {/* Quick Launch Input */}
        <form onSubmit={handleQuickAnalyze} className="flex items-center gap-2 max-w-md w-full">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="0x... Enter Subject Wallet Address"
              value={quickAddress}
              onChange={(e) => setQuickAddress(e.target.value)}
              className="w-full bg-navy-950 border border-navy-700 rounded-lg pl-9 pr-3 py-2 text-xs font-mono text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold tracking-wide transition shadow-lg shadow-cyan-600/20 whitespace-nowrap"
          >
            Analyze
          </button>
        </form>
      </div>

      {/* 4 Required Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Total Cases */}
        <div className="bg-navy-900 border border-navy-750 p-5 rounded-xl hover:border-navy-600 transition shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Total Cases
            </span>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
              <Briefcase className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">
              {loading ? '...' : totalCases}
            </span>
            <span className="text-[11px] text-slate-400 font-mono">logged</span>
          </div>
          <p className="mt-1 text-[11px] text-slate-400">
            Active forensic case files recorded
          </p>
        </div>

        {/* Card 2: High Risk Cases */}
        <div className="bg-navy-900 border border-navy-750 p-5 rounded-xl hover:border-navy-600 transition shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              High Risk Cases
            </span>
            <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-rose-400">
              {loading ? '...' : highRiskCases}
            </span>
            <span className="text-[11px] text-rose-400/80 font-mono">Requires Review</span>
          </div>
          <p className="mt-1 text-[11px] text-slate-400">
            Cases with elevated risk indicators
          </p>
        </div>

        {/* Card 3: VASP Matches */}
        <div className="bg-navy-900 border border-navy-750 p-5 rounded-xl hover:border-navy-600 transition shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              VASP Matches
            </span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Building2 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-emerald-400">
              {loading ? '...' : vaspMatches}
            </span>
            <span className="text-[11px] text-emerald-400/80 font-mono">Synthetic Entities</span>
          </div>
          <p className="mt-1 text-[11px] text-slate-400">
            Attributed exchange and cluster nodes
          </p>
        </div>

        {/* Card 4: Recent Investigations */}
        <div className="bg-navy-900 border border-navy-750 p-5 rounded-xl hover:border-navy-600 transition shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Recent Investigations
            </span>
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-cyan-400">
              {loading ? '...' : recentInvestigationsCount}
            </span>
            <span className="text-[11px] text-slate-400 font-mono">Dockets</span>
          </div>
          <p className="mt-1 text-[11px] text-slate-400">
            Forensic summaries and dossiers
          </p>
        </div>
      </div>

      {/* Main Table: Recent Investigations */}
      <div className="bg-navy-900 border border-navy-750 rounded-xl overflow-hidden shadow-lg">
        <div className="px-6 py-4 border-b border-navy-750 flex items-center justify-between bg-navy-850/50">
          <div>
            <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-cyan-400" />
              Recent Investigations & Dossiers
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Comprehensive registry of analyzed subject wallets and case numbers.
            </p>
          </div>
          <button
            onClick={fetchCases}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-white bg-navy-800 hover:bg-navy-750 rounded-lg border border-navy-700 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="p-12 text-center">
            <div className="inline-block w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="mt-3 text-xs text-slate-400 font-mono">Retrieving forensic records from SQLite store...</p>
          </div>
        )}

        {/* Error State */}
        {!loading && error && (
          <div className="p-8 text-center bg-rose-500/5">
            <AlertTriangle className="w-8 h-8 text-rose-400 mx-auto mb-2" />
            <p className="text-sm font-semibold text-rose-300">Database Connection Error</p>
            <p className="text-xs text-slate-400 mt-1">{error}</p>
            <button
              onClick={fetchCases}
              className="mt-4 px-4 py-1.5 bg-navy-800 text-xs text-slate-200 rounded-lg border border-navy-700 hover:bg-navy-750"
            >
              Retry Connection
            </button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && investigations.length === 0 && (
          <div className="p-12 text-center">
            <ShieldCheck className="w-10 h-10 text-slate-500 mx-auto mb-3" />
            <h4 className="text-sm font-semibold text-slate-300">No Investigation Cases Logged Yet</h4>
            <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
              Initiate your first blockchain intelligence investigation by analyzing an Ethereum wallet address.
            </p>
            <Link
              to="/investigation"
              className="mt-4 inline-flex items-center gap-1.5 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold rounded-lg transition"
            >
              Launch First Analysis
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
        )}

        {/* Populated Table */}
        {!loading && !error && investigations.length > 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-navy-950/60 text-slate-400 font-mono uppercase text-[11px] tracking-wider border-b border-navy-750">
                <tr>
                  <th className="py-3.5 px-6">Case Number</th>
                  <th className="py-3.5 px-6">Subject Wallet</th>
                  <th className="py-3.5 px-6">Chain</th>
                  <th className="py-3.5 px-6">Risk Assessment</th>
                  <th className="py-3.5 px-6">Status</th>
                  <th className="py-3.5 px-6">Investigation Summary</th>
                  <th className="py-3.5 px-6 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-750/70 font-sans">
                {investigations.map((inv) => {
                  const c = inv.case || {};
                  return (
                    <tr
                      key={inv.id}
                      className="hover:bg-navy-800/40 transition group"
                    >
                      <td className="py-3.5 px-6 font-mono font-semibold text-cyan-400">
                        {c.case_number || `CASE-${inv.id}`}
                      </td>
                      <td className="py-3.5 px-6 font-mono text-slate-200">
                        <span className="bg-navy-950 px-2 py-0.5 rounded border border-navy-800 text-[11px]">
                          {c.wallet_address ? `${c.wallet_address.slice(0, 8)}...${c.wallet_address.slice(-6)}` : 'N/A'}
                        </span>
                      </td>
                      <td className="py-3.5 px-6">
                        <span className="uppercase text-[11px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                          {c.blockchain || 'ethereum'}
                        </span>
                      </td>
                      <td className="py-3.5 px-6">
                        <RiskBadge level={c.risk_level} score={c.risk_score} size="xs" />
                      </td>
                      <td className="py-3.5 px-6">
                        <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-slate-300">
                          <span className={`w-1.5 h-1.5 rounded-full ${c.status === 'Active' ? 'bg-cyan-400' : 'bg-slate-400'}`}></span>
                          {c.status || 'Active'}
                        </span>
                      </td>
                      <td className="py-3.5 px-6 max-w-xs text-slate-300 truncate" title={inv.summary}>
                        {inv.summary}
                      </td>
                      <td className="py-3.5 px-6 text-right">
                        <Link
                          to={`/investigation?address=${encodeURIComponent(c.wallet_address || '')}`}
                          className="inline-flex items-center gap-1 text-cyan-400 hover:text-cyan-300 font-semibold text-xs transition"
                        >
                          <span>Open</span>
                          <ArrowUpRight className="w-3.5 h-3.5" />
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Demo Intelligence Presets Banner */}
      <div className="bg-navy-900 border border-navy-750 p-5 rounded-xl">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
            Quick Demo Subject Wallets (Click to Inspect)
          </h4>
          <span className="text-[10px] text-slate-500 font-mono">Phase 1 Demo Seeds</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {[
            {
              title: 'Peel-Chain Dispersal Case',
              addr: '0x71c7656ec7ab88b098defb751b7401b5f6d8976f',
              label: 'High Risk • Multi-Hop Pass-Through'
            },
            {
              title: 'CEX Cluster Nexus',
              addr: '0x28c6c06298d514db089934071355e5743bf21d60',
              label: 'VASP Direct Match (Binance 6)'
            },
            {
              title: 'Institutional Audit Base',
              addr: '0x503828976d22510aad0201ac7ec88293211d23dc',
              label: 'Low Risk • Custody Treasury'
            }
          ].map((preset) => (
            <button
              key={preset.addr}
              onClick={() => navigate(`/investigation?address=${preset.addr}`)}
              className="text-left p-3 rounded-lg bg-navy-850 hover:bg-navy-800 border border-navy-750 hover:border-cyan-500/40 transition group"
            >
              <div className="text-xs font-semibold text-slate-200 group-hover:text-cyan-300">
                {preset.title}
              </div>
              <div className="font-mono text-[11px] text-slate-400 mt-1 truncate">
                {preset.addr}
              </div>
              <div className="text-[10px] text-slate-500 mt-1">{preset.label}</div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
