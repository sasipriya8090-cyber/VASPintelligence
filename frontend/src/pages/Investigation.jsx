import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Search,
  RotateCcw,
  AlertTriangle,
  ShieldAlert,
  ArrowRight,
  GitFork,
  Building2,
  Wallet,
  Clock,
  Info,
  CheckCircle2,
  TrendingDown,
  TrendingUp,
  Fingerprint
} from 'lucide-react';

import api from '../services/api';
import RiskBadge from '../components/RiskBadge';
import DemoDisclaimerBanner from '../components/DemoDisclaimerBanner';

export default function Investigation() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [walletAddress, setWalletAddress] = useState('');
  const [blockchain, setBlockchain] = useState('ethereum');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [validationError, setValidationError] = useState('');
  const [result, setResult] = useState(null);

  // Quick preset triggers
  const demoPresets = [
    {
      label: 'Peel-Chain Target',
      addr: '0x71c7656ec7ab88b098defb751b7401b5f6d8976f'
    },
    {
      label: 'Direct VASP Hot Wallet',
      addr: '0x28c6c06298d514db089934071355e5743bf21d60'
    },
    {
      label: 'Flash Swapper Cluster',
      addr: '0x3cda2097645d52be2250bc33abdb5ac87124f56b'
    },
    {
      label: 'Institutional Safe Pool',
      addr: '0x503828976d22510aad0201ac7ec88293211d23dc'
    }
  ];

  // Auto-run if address passed in query params
  useEffect(() => {
    const queryAddress = searchParams.get('address');

    if (queryAddress) {
      setWalletAddress(queryAddress);
      triggerAnalysis(queryAddress, blockchain);
    }
  }, [searchParams]);

  const validate = (addr) => {
    const clean = (addr || '').trim();

    if (!clean) {
      return 'Wallet address is required.';
    }

    if (
      blockchain === 'ethereum' &&
      !/^0x[a-fA-F0-9]{40}$/.test(clean)
    ) {
      return 'Invalid Ethereum address. Must be a 42-character string starting with 0x.';
    }

    return '';
  };

  const triggerAnalysis = async (addrToUse, chainToUse) => {
    const err = validate(addrToUse);

    if (err) {
      setValidationError(err);
      return;
    }

    setValidationError('');
    setError(null);
    setLoading(true);

    try {
      const data = await api.analyzeWallet(addrToUse, chainToUse);
      setResult(data);
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message || 'An error occurred during analysis.');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = (e) => {
    e.preventDefault();
    triggerAnalysis(walletAddress, blockchain);
  };

  const handleClear = () => {
    setWalletAddress('');
    setValidationError('');
    setError(null);
    setResult(null);
  };

  // Phase 7 — Generate dynamic investigation report
  const handleGenerateReport = () => {
    if (!result) {
      return;
    }

    try {
      // Save complete analysis for Reports page
      localStorage.setItem(
        'vasp_report_data',
        JSON.stringify(result)
      );

      // Also pass the same data through React Router
      navigate('/reports', {
        state: {
          reportData: result
        }
      });
    } catch (storageError) {
      console.error(
        'Failed to save report data:',
        storageError
      );

      // Router state still allows the report to open
      navigate('/reports', {
        state: {
          reportData: result
        }
      });
    }
  };

  const handleSelectPreset = (addr) => {
    setWalletAddress(addr);
    triggerAnalysis(addr, blockchain);
  };

  return (
    <div className="space-y-6">
      <DemoDisclaimerBanner />

      {/* Page Title & Intro */}
      <div className="space-y-1">
        <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
          <Search className="w-5 h-5 text-cyan-400" />
          Blockchain Subject Investigation & Analysis
        </h2>

        <p className="text-xs text-slate-400">
          Enter an Ethereum wallet address to query DEMO ledger activity,
          compute risk indicators, and resolve synthetic VASP attribution.
        </p>
      </div>

      {/* Investigation Input Form */}
      <div className="bg-navy-900 border border-navy-750 p-6 rounded-2xl shadow-xl">
        <form onSubmit={handleAnalyze} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">

            {/* Wallet Address Input */}
            <div className="md:col-span-3 space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-300 flex items-center justify-between">
                <span>Subject Wallet Address</span>

                <span className="text-[10px] text-slate-500 font-mono">
                  Format: 0x... (42 chars)
                </span>
              </label>

              <div className="relative">
                <input
                  type="text"
                  placeholder="0x71c7656ec7ab88b098defb751b7401b5f6d8976f"
                  value={walletAddress}
                  onChange={(e) => {
                    setWalletAddress(e.target.value);

                    if (validationError) {
                      setValidationError('');
                    }
                  }}
                  className={`w-full bg-navy-950 border ${
                    validationError
                      ? 'border-rose-500 ring-1 ring-rose-500'
                      : 'border-navy-700'
                  } rounded-xl px-4 py-3 text-xs sm:text-sm font-mono text-slate-100 placeholder-slate-600 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition`}
                />
              </div>

              {validationError && (
                <p className="text-xs text-rose-400 font-mono flex items-center gap-1 mt-1">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  {validationError}
                </p>
              )}
            </div>

            {/* Blockchain Selector */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                Blockchain Network
              </label>

              <select
                value={blockchain}
                onChange={(e) => setBlockchain(e.target.value)}
                className="w-full bg-navy-950 border border-navy-700 rounded-xl px-3 py-3 text-xs sm:text-sm font-sans text-slate-100 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 transition"
              >
                <option value="ethereum">
                  Ethereum (Mainnet DEMO)
                </option>

                <option value="solana" disabled>
                  Solana (Phase 2 Roadmap)
                </option>

                <option value="bitcoin" disabled>
                  Bitcoin (Phase 2 Roadmap)
                </option>
              </select>
            </div>
          </div>

          {/* Action Buttons & Presets */}
          <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-navy-800">

            {/* Quick Demo Presets */}
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="text-[11px] text-slate-400 mr-1 font-mono">
                Demo Presets:
              </span>

              {demoPresets.map((p) => (
                <button
                  key={p.addr}
                  type="button"
                  onClick={() => handleSelectPreset(p.addr)}
                  className="px-2 py-1 rounded bg-navy-800 hover:bg-navy-750 text-slate-300 hover:text-cyan-300 border border-navy-700 text-[10px] font-mono transition"
                >
                  {p.label}
                </button>
              ))}
            </div>

            {/* Form Buttons */}
            <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
              <button
                type="button"
                onClick={handleClear}
                disabled={loading}
                className="px-4 py-2.5 bg-navy-800 hover:bg-navy-750 text-slate-300 rounded-xl text-xs font-semibold tracking-wide border border-navy-700 transition flex items-center gap-1.5"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                Clear
              </button>

              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl text-xs font-bold tracking-wide shadow-lg shadow-cyan-600/30 transition flex items-center gap-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>

                    <span>
                      Analyzing Ledger...
                    </span>
                  </>
                ) : (
                  <>
                    <Search className="w-3.5 h-3.5" />

                    <span>
                      Analyze Wallet
                    </span>
                  </>
                )}
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Loading State Skeleton */}
      {loading && (
        <div className="bg-navy-900 border border-navy-750 rounded-2xl p-10 text-center space-y-4 shadow-xl">
          <div className="relative inline-block">
            <div className="w-14 h-14 border-4 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin"></div>

            <Fingerprint className="w-6 h-6 text-cyan-400 absolute inset-0 m-auto animate-pulse" />
          </div>

          <div>
            <h4 className="text-base font-bold text-white">
              Forensic Analysis In Progress
            </h4>

            <p className="text-xs text-slate-400 mt-1 font-mono">
              Querying EthereumAdapter DEMO node • Matching synthetic VASP
              addresses • Calculating risk heuristics...
            </p>
          </div>
        </div>
      )}

      {/* Error State */}
      {!loading && error && (
        <div className="bg-rose-500/10 border border-rose-500/30 rounded-2xl p-6 shadow-xl flex items-start gap-4">
          <div className="p-2.5 rounded-xl bg-rose-500/20 text-rose-400 flex-shrink-0">
            <AlertTriangle className="w-6 h-6" />
          </div>

          <div>
            <h4 className="text-sm font-bold text-rose-300">
              Analysis Request Failed
            </h4>

            <p className="text-xs text-slate-300 mt-1 leading-relaxed">
              {error}
            </p>

            <button
              onClick={() => triggerAnalysis(walletAddress, blockchain)}
              className="mt-3 text-xs font-semibold text-rose-400 hover:text-rose-300 flex items-center gap-1 font-mono"
            >
              <span>
                Retry Investigation
              </span>

              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && !result && (
        <div className="bg-navy-900/60 border border-navy-800 rounded-2xl p-12 text-center space-y-3">
          <div className="w-12 h-12 rounded-2xl bg-navy-800 border border-navy-700 flex items-center justify-center text-slate-400 mx-auto">
            <Wallet className="w-6 h-6" />
          </div>

          <h4 className="text-sm font-semibold text-slate-200">
            No Target Subject Analyzed
          </h4>

          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Input a suspect Ethereum wallet address above or click one of the
            pre-configured Demo Presets to generate forensic scores and
            typologies.
          </p>
        </div>
      )}

      {/* Populated Result View */}
      {!loading && !error && result && (
        <div className="space-y-6">

          {/* Quick Result Top Bar */}
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 bg-navy-900 border border-navy-750 p-5 rounded-2xl shadow-xl">

            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-cyan-600/20 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                <Fingerprint className="w-5 h-5" />
              </div>

              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-slate-400">
                    Subject Address:
                  </span>

                  <span className="text-sm font-bold font-mono text-white select-all">
                    {result.wallet_address}
                  </span>
                </div>

                <div className="flex items-center gap-2 mt-1">
                  <span className="text-[11px] font-mono text-cyan-400 uppercase bg-navy-950 px-2 py-0.5 rounded border border-navy-800">
                    {result.blockchain}
                  </span>

                  <span className="text-[11px] text-slate-400 font-sans">
                    {result.wallet_type}
                  </span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3 w-full lg:w-auto justify-end">

              <button
                onClick={() => navigate('/graph')}
                className="px-4 py-2 bg-navy-800 hover:bg-navy-750 text-cyan-300 rounded-xl text-xs font-semibold tracking-wide border border-navy-700 transition flex items-center gap-2"
              >
                <GitFork className="w-4 h-4 text-cyan-400" />

                <span>
                  Open in Wallet Graph
                </span>
              </button>

              {/* Dynamic Report Button */}
              <button
                onClick={handleGenerateReport}
                className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-xs font-semibold tracking-wide transition shadow-lg shadow-cyan-600/20"
              >
                Generate Report
              </button>
            </div>
          </div>

          {/* Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

            {/* Card 1: Balance & Volume */}
            <div className="bg-navy-900 border border-navy-750 p-5 rounded-xl">
              <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
                <span>
                  Account Balance (DEMO)
                </span>

                <Wallet className="w-4 h-4 text-cyan-400" />
              </div>

              <div className="mt-2 text-2xl font-bold font-mono text-white">
                {result.balance} {result.token_symbol}
              </div>

              <div className="text-xs text-slate-400 font-mono mt-1">
                ≈ ${(result.balance * 3150).toLocaleString()} USD
              </div>

              <div className="mt-3 pt-3 border-t border-navy-800 text-[11px] text-slate-400 flex justify-between font-mono">
                <span>
                  Analyzed Txs:
                </span>

                <span className="text-slate-200">
                  {result.total_transactions_analyzed} records
                </span>
              </div>
            </div>

            {/* Card 2: Risk Assessment */}
            <div className="bg-navy-900 border border-navy-750 p-5 rounded-xl">
              <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
                <span>
                  Risk Assessment
                </span>

                <ShieldAlert className="w-4 h-4 text-rose-400" />
              </div>

              <div className="mt-2 flex items-baseline gap-2">
                <span className="text-2xl font-bold font-mono text-white">
                  {result.risk_score}
                </span>

                <span className="text-xs text-slate-400 font-mono">
                  / 100
                </span>

                <div className="ml-auto">
                  <RiskBadge
                    level={result.risk_level}
                    size="sm"
                  />
                </div>
              </div>

              <p className="text-[11px] text-slate-400 mt-1">
                Requires Further Investigation by compliance team
              </p>

              <div className="mt-3 pt-3 border-t border-navy-800 text-[11px] text-slate-400 flex justify-between">
                <span>
                  Classification:
                </span>

                <span className="text-amber-400 font-medium">
                  Potential Suspicious Activity
                </span>
              </div>
            </div>

            {/* Card 3: VASP Attribution */}
            <div className="bg-navy-900 border border-navy-750 p-5 rounded-xl">
              <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
                <span>
                  VASP Attribution (DEMO)
                </span>

                <Building2 className="w-4 h-4 text-emerald-400" />
              </div>

              <div className="mt-2">
                {result.vasp_attribution.matched ? (
                  <>
                    <div className="text-base font-bold text-emerald-400 truncate">
                      {result.vasp_attribution.name}
                    </div>

                    <div className="text-xs text-slate-400 truncate mt-0.5">
                      {result.vasp_attribution.type}
                    </div>
                  </>
                ) : (
                  <>
                    <div className="text-base font-semibold text-slate-300">
                      Unhosted / Unattributed
                    </div>

                    <div className="text-xs text-slate-400 mt-0.5">
                      No synthetic cluster match
                    </div>
                  </>
                )}
              </div>

              <div className="mt-3 pt-3 border-t border-navy-800 text-[11px] text-slate-400 flex justify-between font-mono">
                <span>
                  Confidence:
                </span>

                <span className="text-cyan-400 font-bold">
                  {(result.vasp_attribution.confidence * 100).toFixed(0)}%
                  {' '}(DEMO)
                </span>
              </div>
            </div>
          </div>

          {/* ========================================================= */}
          {/* PHASE 7 — AI INVESTIGATION SUMMARY                       */}
          {/* ========================================================= */}

          {result.ai_investigation && (
            <div className="bg-navy-900 border border-cyan-500/30 rounded-2xl p-6 shadow-xl">

              {/* Header */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 pb-4 border-b border-navy-800">

                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/25 flex items-center justify-center">
                    <Fingerprint className="w-5 h-5 text-cyan-400" />
                  </div>

                  <div>
                    <h3 className="font-bold text-sm text-white">
                      AI Investigation Summary
                    </h3>

                    <p className="text-[11px] text-slate-400 mt-0.5">
                      Automated investigation synthesis from transaction,
                      risk, and VASP attribution data
                    </p>
                  </div>
                </div>

                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-amber-500/10 border border-amber-500/25 text-amber-300 text-[10px] font-mono font-semibold">
                  <AlertTriangle className="w-3 h-3" />

                  {result.ai_investigation.status}
                </span>
              </div>

              {/* Summary */}
              <div className="mt-5 bg-navy-950/70 border border-navy-800 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Info className="w-4 h-4 text-cyan-400" />

                  <span className="text-xs font-semibold text-slate-200">
                    Investigation Summary
                  </span>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed">
                  {result.ai_investigation.summary}
                </p>
              </div>

              {/* Key Findings */}
              <div className="mt-4">
                <h4 className="text-xs font-bold text-slate-200 mb-3">
                  Key Findings
                </h4>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {result.ai_investigation.key_findings?.map(
                    (finding, index) => (
                      <div
                        key={index}
                        className="bg-navy-850 border border-navy-750 rounded-xl p-3 flex items-start gap-2.5"
                      >
                        <CheckCircle2 className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />

                        <p className="text-[11px] text-slate-300 leading-relaxed">
                          {finding}
                        </p>
                      </div>
                    )
                  )}
                </div>
              </div>

              {/* AI Risk + VASP */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">

                {/* AI Risk */}
                <div className="bg-navy-850 border border-navy-750 rounded-xl p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] uppercase tracking-wider font-bold text-slate-400">
                      AI Risk Assessment
                    </span>

                    <RiskBadge
                      level={result.ai_investigation.risk_level}
                      size="xs"
                    />
                  </div>

                  <div className="mt-2 flex items-baseline gap-2">
                    <span className="text-2xl font-bold font-mono text-white">
                      {result.ai_investigation.risk_score}
                    </span>

                    <span className="text-[11px] text-slate-500 font-mono">
                      / 100
                    </span>
                  </div>

                  <p className="text-[10px] text-slate-500 mt-1">
                    Assessment generated from available DEMO analysis data.
                  </p>
                </div>

                {/* AI VASP Attribution */}
                <div className="bg-navy-850 border border-navy-750 rounded-xl p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] uppercase tracking-wider font-bold text-slate-400">
                      AI VASP Finding
                    </span>

                    <Building2 className="w-4 h-4 text-emerald-400" />
                  </div>

                  {result.ai_investigation.vasp_attribution?.matched ? (
                    <>
                      <div className="mt-2 text-sm font-bold text-emerald-400 truncate">
                        {result.ai_investigation.vasp_attribution.name}
                      </div>

                      <div className="mt-1 text-[10px] text-slate-500 font-mono">
                        Confidence:{' '}
                        {result.ai_investigation.vasp_attribution.confidence !==
                        null
                          ? `${(
                              Number(
                                result.ai_investigation.vasp_attribution
                                  .confidence
                              ) * 100
                            ).toFixed(0)}%`
                          : 'N/A'}
                      </div>
                    </>
                  ) : (
                    <div className="mt-2 text-sm text-slate-300">
                      No known VASP identified
                    </div>
                  )}
                </div>
              </div>

              {/* Possible Typologies */}
              <div className="mt-4 bg-navy-850 border border-navy-750 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-3">
                  <GitFork className="w-4 h-4 text-amber-400" />

                  <span className="text-xs font-bold text-slate-200">
                    Possible Transaction Typologies
                  </span>
                </div>

                <div className="flex flex-wrap gap-2">
                  {result.ai_investigation.possible_typologies?.map(
                    (typology, index) => (
                      <span
                        key={index}
                        className="px-2.5 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/25 text-amber-300 text-[10px] font-mono"
                      >
                        {typology}
                      </span>
                    )
                  )}
                </div>
              </div>

              {/* Recommended Next Steps */}
              <div className="mt-4">
                <h4 className="text-xs font-bold text-slate-200 mb-3">
                  Recommended Investigation Steps
                </h4>

                <div className="space-y-2">
                  {result.ai_investigation.recommended_next_steps?.map(
                    (step, index) => (
                      <div
                        key={index}
                        className="flex items-start gap-2.5 bg-navy-950/60 border border-navy-800 rounded-lg px-3 py-2.5"
                      >
                        <span className="w-5 h-5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center text-[9px] font-bold flex-shrink-0">
                          {index + 1}
                        </span>

                        <span className="text-[11px] text-slate-300 leading-relaxed">
                          {step}
                        </span>
                      </div>
                    )
                  )}
                </div>
              </div>

              {/* Demo Data Notice */}
              <div className="mt-4 pt-4 border-t border-navy-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                <span className="text-[10px] text-slate-500 font-mono">
                  {result.ai_investigation.data_mode}
                </span>

                <span className="text-[10px] text-amber-400/80 font-mono">
                  Requires Further Investigation
                </span>
              </div>
            </div>
          )}

          {/* Risk Indicators & Observed Typologies */}
          <div className="bg-navy-900 border border-navy-750 rounded-xl p-6 shadow-lg space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                Forensic Risk Indicators & Observed Typologies
              </h3>

              <span className="text-xs font-mono text-slate-500">
                {result.risk_indicators.length} signals identified
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {result.risk_indicators.map((ind, idx) => (
                <div
                  key={idx}
                  className="bg-navy-850 border border-navy-750/80 rounded-xl p-4 space-y-1.5 hover:border-navy-650 transition"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono uppercase font-bold text-cyan-400 tracking-wider">
                      {ind.category}
                    </span>

                    <RiskBadge
                      level={ind.severity}
                      size="xs"
                    />
                  </div>

                  <h4 className="text-xs font-bold text-slate-200">
                    {ind.indicator}
                  </h4>

                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    {ind.description}
                  </p>
                </div>
              ))}
            </div>

            {/* Typologies List */}
            <div className="mt-4 pt-4 border-t border-navy-800">
              <div className="text-xs font-semibold text-slate-300 mb-2">
                Suspected Behavioral Typologies:
              </div>

              <div className="flex flex-wrap gap-2">
                {result.possible_typologies.map((typ, i) => (
                  <span
                    key={i}
                    className="px-2.5 py-1 rounded-md bg-amber-500/10 border border-amber-500/25 text-amber-300 text-xs font-mono"
                  >
                    {typ}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Recent Ledger Transactions Table */}
          <div className="bg-navy-900 border border-navy-750 rounded-xl overflow-hidden shadow-lg">

            <div className="px-6 py-4 border-b border-navy-750 flex items-center justify-between bg-navy-850/50">
              <div>
                <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-cyan-400" />
                  Associated Transactions (DEMO)
                </h3>

                <p className="text-xs text-slate-400 mt-0.5">
                  Flow analysis for inbound and outbound transaction hops.
                </p>
              </div>

              <span className="text-[11px] font-mono text-slate-400 bg-navy-950 px-2 py-1 rounded border border-navy-800">
                {result.recent_transactions.length} Transactions
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">

                <thead className="bg-navy-950/60 text-slate-400 font-mono uppercase text-[11px] tracking-wider border-b border-navy-750">
                  <tr>
                    <th className="py-3 px-6">
                      Direction
                    </th>

                    <th className="py-3 px-6">
                      Tx Hash
                    </th>

                    <th className="py-3 px-6">
                      From Address
                    </th>

                    <th className="py-3 px-6">
                      To Address
                    </th>

                    <th className="py-3 px-6">
                      Amount
                    </th>

                    <th className="py-3 px-6">
                      Attribution Nexus
                    </th>

                    <th className="py-3 px-6">
                      Risk Signals
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-navy-750/70 font-sans">
                  {result.recent_transactions.map((tx, idx) => {
                    const isOut = tx.direction === 'OUTGOING';

                    return (
                      <tr
                        key={idx}
                        className="hover:bg-navy-800/40 transition font-sans"
                      >

                        <td className="py-3.5 px-6">
                          <span
                            className={`inline-flex items-center gap-1 font-mono text-[10px] font-bold px-2 py-0.5 rounded ${
                              isOut
                                ? 'bg-amber-500/15 text-amber-400 border border-amber-500/25'
                                : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25'
                            }`}
                          >
                            {isOut ? (
                              <TrendingUp className="w-3 h-3" />
                            ) : (
                              <TrendingDown className="w-3 h-3" />
                            )}

                            {tx.direction}
                          </span>
                        </td>

                        <td className="py-3.5 px-6 font-mono text-cyan-400">
                          {tx.tx_hash.slice(0, 10)}...
                          {tx.tx_hash.slice(-6)}
                        </td>

                        <td className="py-3.5 px-6 font-mono text-slate-300">
                          {tx.from_address.slice(0, 8)}...
                          {tx.from_address.slice(-6)}
                        </td>

                        <td className="py-3.5 px-6 font-mono text-slate-300">
                          {tx.to_address.slice(0, 8)}...
                          {tx.to_address.slice(-6)}
                        </td>

                        <td className="py-3.5 px-6 font-mono font-semibold text-white">
                          {tx.amount} {tx.token}
                        </td>

                        <td className="py-3.5 px-6">
                          {tx.vasp_attribution ? (
                            <span className="px-2 py-0.5 rounded bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 text-[10px] font-semibold">
                              {tx.vasp_attribution}
                            </span>
                          ) : (
                            <span className="text-slate-500 text-[11px] font-mono">
                              Unhosted
                            </span>
                          )}
                        </td>

                        <td className="py-3.5 px-6">
                          {tx.risk_indicators.length > 0 ? (
                            <div className="flex flex-col gap-0.5">
                              {tx.risk_indicators.map((sig, sIdx) => (
                                <span
                                  key={sIdx}
                                  className="text-[10px] text-amber-400 truncate max-w-xs font-mono"
                                >
                                  • {sig}
                                </span>
                              ))}
                            </div>
                          ) : (
                            <span className="text-[11px] text-slate-500">
                              Normal
                            </span>
                          )}
                        </td>

                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}