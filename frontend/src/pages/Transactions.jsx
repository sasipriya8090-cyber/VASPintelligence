import React, { useState, useEffect } from 'react';
import {
  ArrowLeftRight,
  Search,
  Filter,
  TrendingDown,
  TrendingUp,
  Download,
  Building2,
  ExternalLink,
  ShieldAlert
} from 'lucide-react';
import DemoDisclaimerBanner from '../components/DemoDisclaimerBanner';

export default function Transactions() {
  const [filterDirection, setFilterDirection] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  // Curated demo transaction dataset for Phase 1 ledger review
  const allTransactions = [
    {
      tx_hash: '0x3a4f89d71b5690e8a712c9b4e721d00923f124a87265bc6721ea1029384756ab',
      case_number: 'CASE-2026-001',
      blockchain: 'ethereum',
      from_address: '0x742d35cc6634c0532925a3b844bc454e4438f44e',
      to_address: '0x71c7656ec7ab88b098defb751b7401b5f6d8976f',
      amount: 42.5,
      token: 'ETH',
      timestamp: '2026-10-03 12:45:10',
      direction: 'INCOMING',
      vasp_attribution: 'Demo Kraken Deposit Pool',
      risk_indicator: 'High-value threshold exceeded (42.5 ETH)'
    },
    {
      tx_hash: '0x992b8120485712e0941235123985710293847510293847561029384756102938',
      case_number: 'CASE-2026-001',
      blockchain: 'ethereum',
      from_address: '0x71c7656ec7ab88b098defb751b7401b5f6d8976f',
      to_address: '0x89205a3e3b2db69dce6aa645f778d655fba73bfa',
      amount: 25.0,
      token: 'ETH',
      timestamp: '2026-10-03 13:15:32',
      direction: 'OUTGOING',
      vasp_attribution: 'Unhosted Intermediary',
      risk_indicator: 'Rapid outbound dispersal (Peel chain)'
    },
    {
      tx_hash: '0x5c4d123490812349810239481029384019283401928340192834019283401928',
      case_number: 'CASE-2026-001',
      blockchain: 'ethereum',
      from_address: '0x71c7656ec7ab88b098defb751b7401b5f6d8976f',
      to_address: '0x28c6c06298d514db089934071355e5743bf21d60',
      amount: 16.85,
      token: 'ETH',
      timestamp: '2026-10-03 14:02:18',
      direction: 'OUTGOING',
      vasp_attribution: 'Demo Binance Hot Wallet 6',
      risk_indicator: 'Exchange off-ramp funneling'
    },
    {
      tx_hash: '0xfe10293847561029384756102938475610293847561029384756102938475610',
      case_number: 'CASE-2026-002',
      blockchain: 'ethereum',
      from_address: '0x3cda2097645d52be2250bc33abdb5ac87124f56b',
      to_address: '0xdfd5293d8e347dff59e4571400ba7aba95eeb0e9',
      amount: 60.0,
      token: 'ETH',
      timestamp: '2026-10-02 18:22:04',
      direction: 'OUTGOING',
      vasp_attribution: 'Demo Uniswap Universal Router',
      risk_indicator: 'High-frequency DEX router swap'
    },
    {
      tx_hash: '0x77b0192834710293847561029384756102938475610293847561029384756102',
      case_number: 'CASE-2026-003',
      blockchain: 'ethereum',
      from_address: '0x503828976d22510aad0201ac7ec88293211d23dc',
      to_address: '0x28c6c06298d514db089934071355e5743bf21d60',
      amount: 110.0,
      token: 'ETH',
      timestamp: '2026-10-02 10:14:55',
      direction: 'INCOMING',
      vasp_attribution: 'Demo Coinbase Hot Wallet',
      risk_indicator: 'Inter-exchange custody rebalancing'
    },
    {
      tx_hash: '0xaa12837461928374619283746192837461928374619283746192837461928374',
      case_number: 'CASE-2026-004',
      blockchain: 'ethereum',
      from_address: '0x503828976d22510aad0201ac7ec88293211d23dc',
      to_address: '0x1111111254eeb25477b68fb85ed929f73a960582',
      amount: 15.2,
      token: 'ETH',
      timestamp: '2026-10-01 09:30:12',
      direction: 'OUTGOING',
      vasp_attribution: 'Demo 1inch V5 Aggregator',
      risk_indicator: 'Normal routing'
    }
  ];

  const filtered = allTransactions.filter((tx) => {
    if (filterDirection !== 'ALL' && tx.direction !== filterDirection) return false;
    if (searchTerm) {
      const q = searchTerm.toLowerCase();
      const matchHash = tx.tx_hash.toLowerCase().includes(q);
      const matchFrom = tx.from_address.toLowerCase().includes(q);
      const matchTo = tx.to_address.toLowerCase().includes(q);
      const matchVasp = tx.vasp_attribution.toLowerCase().includes(q);
      return matchHash || matchFrom || matchTo || matchVasp;
    }
    return true;
  });

  return (
    <div className="space-y-6">
      <DemoDisclaimerBanner />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <ArrowLeftRight className="w-5 h-5 text-cyan-400" />
            Transaction Ledger & Flow Tracing
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Cross-case transaction ledger records, risk signals, and synthetic VASP endpoint tags.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-slate-400 bg-navy-900 border border-navy-750 px-3 py-1.5 rounded-lg">
            Total Ledger Rows: {filtered.length}
          </span>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="bg-navy-900 border border-navy-750 p-4 rounded-xl flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Search Input */}
        <div className="relative w-full md:max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by Tx Hash, From/To Address, or VASP..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-navy-950 border border-navy-700 rounded-lg pl-9 pr-3 py-2 text-xs font-mono text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400"
          />
        </div>

        {/* Direction Filter Tabs */}
        <div className="flex items-center gap-1.5 bg-navy-950 p-1 rounded-lg border border-navy-800 w-full md:w-auto">
          {['ALL', 'INCOMING', 'OUTGOING'].map((dir) => (
            <button
              key={dir}
              onClick={() => setFilterDirection(dir)}
              className={`px-3 py-1.5 rounded-md text-xs font-semibold tracking-wide transition flex-1 md:flex-none ${
                filterDirection === dir
                  ? 'bg-cyan-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {dir}
            </button>
          ))}
        </div>
      </div>

      {/* Ledger Table */}
      <div className="bg-navy-900 border border-navy-750 rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-navy-950/60 text-slate-400 font-mono uppercase text-[11px] tracking-wider border-b border-navy-750">
              <tr>
                <th className="py-3 px-6">Direction</th>
                <th className="py-3 px-6">Tx Hash</th>
                <th className="py-3 px-6">Timestamp</th>
                <th className="py-3 px-6">From Address</th>
                <th className="py-3 px-6">To Address</th>
                <th className="py-3 px-6">Amount</th>
                <th className="py-3 px-6">VASP Counterparty</th>
                <th className="py-3 px-6">Investigative Indicator</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-750/70 font-sans">
              {filtered.map((tx, idx) => {
                const isOut = tx.direction === 'OUTGOING';
                return (
                  <tr key={idx} className="hover:bg-navy-800/40 transition">
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
                      {tx.tx_hash.slice(0, 10)}...{tx.tx_hash.slice(-6)}
                    </td>
                    <td className="py-3.5 px-6 font-mono text-slate-400 text-[11px]">
                      {tx.timestamp}
                    </td>
                    <td className="py-3.5 px-6 font-mono text-slate-300">
                      {tx.from_address.slice(0, 8)}...{tx.from_address.slice(-6)}
                    </td>
                    <td className="py-3.5 px-6 font-mono text-slate-300">
                      {tx.to_address.slice(0, 8)}...{tx.to_address.slice(-6)}
                    </td>
                    <td className="py-3.5 px-6 font-mono font-bold text-white">
                      {tx.amount} {tx.token}
                    </td>
                    <td className="py-3.5 px-6">
                      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-navy-950 border border-navy-800 text-[11px] font-medium text-slate-200">
                        <Building2 className="w-3 h-3 text-cyan-400" />
                        {tx.vasp_attribution}
                      </span>
                    </td>
                    <td className="py-3.5 px-6">
                      <span className="text-[11px] text-amber-300/90 font-mono">
                        {tx.risk_indicator}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
