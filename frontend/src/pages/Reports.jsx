import React, { useEffect, useState } from 'react';
import {
  FileText,
  Printer,
  Shield,
  AlertTriangle,
  Building2,
  Calendar,
  User,
  CheckCircle2,
  ArrowRight,
  Wallet,
  Activity,
  Brain,
  Route,
  ClipboardCheck
} from 'lucide-react';

import RiskBadge from '../components/RiskBadge';
import DemoDisclaimerBanner from '../components/DemoDisclaimerBanner';

export default function Reports() {
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    try {
      const savedData = localStorage.getItem('vasp_report_data');

      if (savedData) {
        const parsedData = JSON.parse(savedData);
        setReportData(parsedData);
      }
    } catch (error) {
      console.error('Failed to load report data:', error);
      setReportData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const handlePrint = () => {
    window.print();
  };

  const formatConfidence = (confidence) => {
    if (confidence === null || confidence === undefined) {
      return 'N/A';
    }

    const numericConfidence = Number(confidence);

    if (Number.isNaN(numericConfidence)) {
      return confidence;
    }

    return `${(numericConfidence * 100).toFixed(0)}%`;
  };

  const formatDate = () => {
    return new Date().toLocaleString('en-IN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <DemoDisclaimerBanner />

        <div className="bg-navy-900 border border-navy-750 rounded-2xl p-12 text-center">
          <div className="w-10 h-10 border-4 border-cyan-500/20 border-t-cyan-400 rounded-full animate-spin mx-auto mb-4"></div>

          <h3 className="text-sm font-bold text-white">
            Loading Investigation Report...
          </h3>

          <p className="text-xs text-slate-400 mt-2">
            Preparing the latest wallet analysis dossier.
          </p>
        </div>
      </div>
    );
  }

  if (!reportData) {
    return (
      <div className="space-y-6">
        <DemoDisclaimerBanner />

        <div className="bg-navy-900 border border-navy-750 rounded-2xl p-10 text-center">
          <div className="w-14 h-14 rounded-2xl bg-navy-800 border border-navy-700 flex items-center justify-center mx-auto mb-4">
            <FileText className="w-7 h-7 text-slate-400" />
          </div>

          <h2 className="text-lg font-bold text-white">
            No Investigation Report Available
          </h2>

          <p className="text-xs text-slate-400 mt-2 max-w-lg mx-auto leading-relaxed">
            Run a wallet investigation first and click
            <span className="text-cyan-400 font-semibold">
              {' Generate Report '}
            </span>
            to create an investigation-ready report.
          </p>
        </div>
      </div>
    );
  }

  const ai = reportData.ai_investigation || {};

  const vasp =
    reportData.vasp_attribution ||
    ai.vasp_attribution ||
    {};

  const matchedVasp =
    vasp.matched === true ||
    Boolean(vasp.name);

  const vaspName =
    vasp.name ||
    'No known VASP identified';

  const vaspType =
    vasp.type ||
    'Unhosted / Unattributed';

  const vaspConfidence =
    vasp.confidence ??
    ai.vasp_attribution?.confidence ??
    null;

  const riskIndicators =
    reportData.risk_indicators ||
    ai.risk_indicators ||
    [];

  const typologies =
    reportData.possible_typologies ||
    ai.possible_typologies ||
    [];

  const transactions =
    reportData.recent_transactions ||
    [];

  const transactionCount =
    reportData.total_transactions_analyzed ??
    ai.transaction_count ??
    transactions.length ??
    0;

  const riskScore =
    reportData.risk_score ??
    ai.risk_score ??
    0;

  const riskLevel =
    reportData.risk_level ||
    ai.risk_level ||
    'LOW';

  const walletAddress =
    reportData.wallet_address ||
    ai.wallet_address ||
    'Unknown';

  const blockchain =
    reportData.blockchain ||
    ai.blockchain ||
    'ethereum';

  const walletType =
    reportData.wallet_type ||
    'Subject Wallet';

  const aiSummary =
    ai.summary ||
    'The wallet was assessed using available transaction, risk, and VASP attribution data. Findings represent potential risk indicators and require further investigation.';

  const keyFindings =
    ai.key_findings ||
    [];

  const nextSteps =
    ai.recommended_next_steps ||
    [
      'Review the identified transaction paths and intermediary wallets.',
      'Validate the VASP attribution against authoritative intelligence sources.',
      'Review the identified risk indicators and possible typologies.',
      'Conduct further investigation before taking any enforcement action.'
    ];

  return (
    <div className="space-y-6 print:space-y-0">

      {/* Demo Warning */}
      <div className="print:hidden">
        <DemoDisclaimerBanner />
      </div>

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 print:hidden">

        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-cyan-400" />
            Investigation-Ready Forensic Report
          </h2>

          <p className="text-xs text-slate-400 mt-1">
            Generated from the latest blockchain wallet investigation.
          </p>
        </div>

        <button
          onClick={handlePrint}
          className="flex items-center justify-center gap-2 px-4 py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-xs font-semibold transition shadow-lg shadow-cyan-600/20"
        >
          <Printer className="w-4 h-4" />
          Print Dossier
        </button>
      </div>

      {/* Main Report */}
      <div
        className="
          bg-navy-900
          border border-navy-750
          rounded-2xl
          p-6
          sm:p-8
          lg:p-10
          shadow-2xl
          space-y-8
          print:bg-white
          print:text-black
          print:border-0
          print:shadow-none
          print:rounded-none
          print:p-0
        "
      >

        {/* Report Header */}
        <div className="border-b border-navy-750 pb-6 print:border-gray-300">

          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">

            <div>
              <div className="text-[10px] sm:text-[11px] font-mono tracking-[0.18em] text-cyan-400 uppercase font-bold print:text-gray-600">
                BLOCKCHAIN INTELLIGENCE & FORENSIC ANALYSIS
              </div>

              <h1 className="text-2xl sm:text-3xl font-bold text-white mt-2 print:text-black">
                Automated Investigation Report
              </h1>

              <p className="text-xs text-slate-400 mt-2 print:text-gray-600">
                Automated Blockchain Intelligence & VASP Attribution Engine
              </p>
            </div>

            <div className="text-left md:text-right">
              <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                Report Generated
              </div>

              <div className="text-xs text-slate-300 font-mono mt-1 print:text-gray-700">
                {formatDate()}
              </div>

              <div className="text-[10px] text-amber-400 mt-2 font-semibold print:text-gray-700">
                DEMO / SYNTHETIC DATA
              </div>
            </div>

          </div>
        </div>

        {/* Subject Information */}
        <section className="space-y-4">

          <div className="flex items-center gap-2">
            <Wallet className="w-4 h-4 text-cyan-400" />

            <h2 className="text-sm font-bold text-white print:text-black">
              1. Subject Wallet Information
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

            <div className="bg-navy-950 border border-navy-800 rounded-xl p-4 print:bg-gray-50 print:border-gray-300">
              <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                Wallet Address
              </div>

              <div className="text-xs sm:text-sm font-mono text-cyan-300 mt-2 break-all print:text-black">
                {walletAddress}
              </div>
            </div>

            <div className="bg-navy-950 border border-navy-800 rounded-xl p-4 print:bg-gray-50 print:border-gray-300">
              <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                Blockchain
              </div>

              <div className="text-sm font-semibold text-white mt-2 capitalize print:text-black">
                {blockchain}
              </div>
            </div>

            <div className="bg-navy-950 border border-navy-800 rounded-xl p-4 print:bg-gray-50 print:border-gray-300">
              <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                Wallet Type
              </div>

              <div className="text-sm font-semibold text-white mt-2 print:text-black">
                {walletType}
              </div>
            </div>

            <div className="bg-navy-950 border border-navy-800 rounded-xl p-4 print:bg-gray-50 print:border-gray-300">
              <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                Transactions Analyzed
              </div>

              <div className="text-sm font-bold text-cyan-300 mt-2 print:text-black">
                {transactionCount}
              </div>
            </div>

          </div>
        </section>

        {/* Risk Assessment */}
        <section className="space-y-4">

          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-cyan-400" />

            <h2 className="text-sm font-bold text-white print:text-black">
              2. Risk Assessment
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

            <div className="bg-navy-950 border border-navy-800 rounded-xl p-5 print:bg-gray-50 print:border-gray-300">
              <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                Risk Score
              </div>

              <div className="flex items-end gap-2 mt-2">
                <span className="text-3xl font-bold font-mono text-white print:text-black">
                  {Number(riskScore).toFixed(0)}
                </span>

                <span className="text-xs text-slate-500 mb-1">
                  / 100
                </span>
              </div>
            </div>

            <div className="bg-navy-950 border border-navy-800 rounded-xl p-5 print:bg-gray-50 print:border-gray-300">
              <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-2">
                Risk Level
              </div>

              <RiskBadge
                level={riskLevel}
                size="sm"
              />
            </div>

            <div className="bg-navy-950 border border-navy-800 rounded-xl p-5 print:bg-gray-50 print:border-gray-300">

              <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                Investigation Status
              </div>

              <div className="flex items-center gap-2 mt-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />

                <span className="text-xs font-semibold text-amber-300 print:text-gray-800">
                  Requires Further Investigation
                </span>
              </div>

            </div>

          </div>

          <div className="bg-amber-500/5 border border-amber-500/20 rounded-xl p-4 print:bg-gray-50 print:border-gray-300">

            <div className="text-xs font-semibold text-amber-300 print:text-gray-800">
              Classification
            </div>

            <p className="text-xs text-slate-400 mt-1 print:text-gray-700">
              Potential Suspicious Activity
            </p>

          </div>

        </section>

        {/* VASP Attribution */}
        <section className="space-y-4">

          <div className="flex items-center gap-2">
            <Building2 className="w-4 h-4 text-emerald-400" />

            <h2 className="text-sm font-bold text-white print:text-black">
              3. VASP Attribution
            </h2>
          </div>

          <div className="bg-navy-950 border border-navy-800 rounded-xl p-5 print:bg-gray-50 print:border-gray-300">

            {matchedVasp ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">

                <div>
                  <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                    Attributed Entity
                  </div>

                  <div className="text-base font-bold text-emerald-400 mt-2 print:text-black">
                    {vaspName}
                  </div>
                </div>

                <div>
                  <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                    Entity Type
                  </div>

                  <div className="text-sm text-slate-300 mt-2 print:text-gray-700">
                    {vaspType}
                  </div>
                </div>

                <div>
                  <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                    Attribution Confidence
                  </div>

                  <div className="text-xl font-bold text-cyan-300 mt-1 print:text-black">
                    {formatConfidence(vaspConfidence)}
                  </div>
                </div>

              </div>
            ) : (
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-400" />

                <div>
                  <div className="text-sm font-semibold text-slate-200 print:text-black">
                    No known VASP attribution identified
                  </div>

                  <p className="text-xs text-slate-400 mt-1 print:text-gray-600">
                    No matching entity was found in the available synthetic registry.
                  </p>
                </div>
              </div>
            )}

          </div>

          <div className="text-[11px] text-slate-500 font-mono">
            Attribution source: Synthetic DEMO VASP Registry
          </div>

        </section>

        {/* AI Investigation Summary */}
        <section className="space-y-4">

          <div className="flex items-center gap-2">
            <Brain className="w-4 h-4 text-purple-400" />

            <h2 className="text-sm font-bold text-white print:text-black">
              4. AI Investigation Summary
            </h2>
          </div>

          <div className="bg-purple-500/5 border border-purple-500/20 rounded-xl p-5 print:bg-gray-50 print:border-gray-300">

            <p className="text-sm leading-7 text-slate-300 print:text-gray-800">
              {aiSummary}
            </p>

          </div>

          {keyFindings.length > 0 && (
            <div className="space-y-3">

              <h3 className="text-xs font-semibold text-slate-300 print:text-gray-800">
                Key Findings
              </h3>

              <div className="space-y-2">

                {keyFindings.map((finding, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-3 bg-navy-950 border border-navy-800 rounded-lg p-3 print:bg-gray-50 print:border-gray-300"
                  >
                    <CheckCircle2 className="w-4 h-4 text-cyan-400 mt-0.5 flex-shrink-0" />

                    <span className="text-xs text-slate-300 leading-relaxed print:text-gray-800">
                      {finding}
                    </span>
                  </div>
                ))}

              </div>

            </div>
          )}

        </section>

        {/* Risk Indicators */}
        <section className="space-y-4">

          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />

            <h2 className="text-sm font-bold text-white print:text-black">
              5. Risk Indicators
            </h2>
          </div>

          {riskIndicators.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">

              {riskIndicators.map((indicator, index) => {

                const indicatorText =
                  typeof indicator === 'string'
                    ? indicator
                    : indicator.indicator ||
                      indicator.description ||
                      indicator.signal ||
                      'Risk indicator identified';

                const description =
                  typeof indicator === 'string'
                    ? ''
                    : indicator.description ||
                      indicator.finding ||
                      '';

                const severity =
                  typeof indicator === 'object'
                    ? indicator.severity
                    : null;

                return (
                  <div
                    key={index}
                    className="bg-navy-950 border border-navy-800 rounded-xl p-4 print:bg-gray-50 print:border-gray-300"
                  >

                    <div className="flex items-start justify-between gap-3">

                      <div className="flex items-start gap-2">

                        <Activity className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />

                        <div>
                          <h3 className="text-xs font-semibold text-slate-200 print:text-black">
                            {indicatorText}
                          </h3>

                          {description && (
                            <p className="text-[11px] text-slate-400 mt-1 leading-relaxed print:text-gray-600">
                              {description}
                            </p>
                          )}
                        </div>

                      </div>

                      {severity && (
                        <RiskBadge
                          level={severity}
                          size="xs"
                        />
                      )}

                    </div>

                  </div>
                );
              })}

            </div>
          ) : (
            <div className="bg-navy-950 border border-navy-800 rounded-xl p-5 text-xs text-slate-400 print:bg-gray-50 print:border-gray-300 print:text-gray-600">
              No individual risk indicator records were returned in the current analysis response.
            </div>
          )}

        </section>

        {/* Typologies */}
        <section className="space-y-4">

          <div className="flex items-center gap-2">
            <Route className="w-4 h-4 text-amber-400" />

            <h2 className="text-sm font-bold text-white print:text-black">
              6. Possible Transaction Typologies
            </h2>
          </div>

          {typologies.length > 0 ? (
            <div className="space-y-2">

              {typologies.map((typology, index) => (
                <div
                  key={index}
                  className="flex items-center gap-3 bg-amber-500/5 border border-amber-500/20 rounded-xl p-3 print:bg-gray-50 print:border-gray-300"
                >
                  <ArrowRight className="w-4 h-4 text-amber-400 flex-shrink-0" />

                  <span className="text-xs text-amber-200 print:text-gray-800">
                    {typology}
                  </span>
                </div>
              ))}

            </div>
          ) : (
            <div className="text-xs text-slate-500">
              No typologies returned.
            </div>
          )}

        </section>

        {/* Transaction Summary */}
        <section className="space-y-4">

          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />

            <h2 className="text-sm font-bold text-white print:text-black">
              7. Transaction Analysis
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

            <div className="bg-navy-950 border border-navy-800 rounded-xl p-4 print:bg-gray-50 print:border-gray-300">
              <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                Transactions Considered
              </div>

              <div className="text-2xl font-bold text-white mt-2 print:text-black">
                {transactionCount}
              </div>
            </div>

            <div className="bg-navy-950 border border-navy-800 rounded-xl p-4 print:bg-gray-50 print:border-gray-300">
              <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                Data Environment
              </div>

              <div className="text-sm font-semibold text-amber-300 mt-2 print:text-black">
                DEMO
              </div>
            </div>

            <div className="bg-navy-950 border border-navy-800 rounded-xl p-4 print:bg-gray-50 print:border-gray-300">
              <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                Analysis Type
              </div>

              <div className="text-sm font-semibold text-cyan-300 mt-2 print:text-black">
                Automated
              </div>
            </div>

          </div>

          {transactions.length > 0 && (
            <div className="overflow-x-auto border border-navy-800 rounded-xl print:border-gray-300">

              <table className="w-full text-left text-xs">

                <thead className="bg-navy-950 text-slate-400 border-b border-navy-800 print:bg-gray-100 print:text-gray-700 print:border-gray-300">
                  <tr>
                    <th className="px-4 py-3">Direction</th>
                    <th className="px-4 py-3">Amount</th>
                    <th className="px-4 py-3">VASP Attribution</th>
                    <th className="px-4 py-3">Risk Signals</th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-navy-800 print:divide-gray-300">

                  {transactions.slice(0, 10).map((tx, index) => (

                    <tr key={index}>

                      <td className="px-4 py-3">
                        <span className="text-slate-300 print:text-gray-800">
                          {tx.direction || 'UNKNOWN'}
                        </span>
                      </td>

                      <td className="px-4 py-3 font-mono text-white print:text-black">
                        {tx.amount ?? '-'} {tx.token || ''}
                      </td>

                      <td className="px-4 py-3">
                        <span className="text-emerald-400 print:text-gray-800">
                          {tx.vasp_attribution || 'Unhosted'}
                        </span>
                      </td>

                      <td className="px-4 py-3">
                        {tx.risk_indicators?.length > 0 ? (
                          <span className="text-amber-400 print:text-gray-800">
                            {tx.risk_indicators.length} signal(s)
                          </span>
                        ) : (
                          <span className="text-slate-500">
                            Normal
                          </span>
                        )}
                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>
          )}

        </section>

        {/* Recommended Next Steps */}
        <section className="space-y-4">

          <div className="flex items-center gap-2">
            <ClipboardCheck className="w-4 h-4 text-cyan-400" />

            <h2 className="text-sm font-bold text-white print:text-black">
              8. Recommended Investigation Next Steps
            </h2>
          </div>

          <div className="space-y-2">

            {nextSteps.map((step, index) => (
              <div
                key={index}
                className="flex items-start gap-3 bg-navy-950 border border-navy-800 rounded-xl p-4 print:bg-gray-50 print:border-gray-300"
              >

                <div className="w-5 h-5 rounded-full bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-[10px] text-cyan-300 font-bold flex-shrink-0">
                  {index + 1}
                </div>

                <span className="text-xs text-slate-300 leading-relaxed print:text-gray-800">
                  {step}
                </span>

              </div>
            ))}

          </div>

        </section>

        {/* Compliance / Disclaimer */}
        <section className="border-t border-navy-750 pt-6 print:border-gray-300">

          <div className="bg-rose-500/5 border border-rose-500/20 rounded-xl p-5 print:bg-gray-50 print:border-gray-300">

            <div className="flex items-start gap-3">

              <AlertTriangle className="w-5 h-5 text-rose-400 mt-0.5 flex-shrink-0" />

              <div>

                <h3 className="text-xs font-bold text-rose-300 print:text-gray-800">
                  Investigation Disclaimer
                </h3>

                <p className="text-[11px] text-slate-400 leading-relaxed mt-2 print:text-gray-700">
                  This report is generated from synthetic DEMO blockchain
                  intelligence data. Risk classifications, VASP attribution,
                  transaction typologies, and confidence values are analytical
                  outputs for demonstration purposes only. They should be
                  independently validated against authoritative blockchain
                  intelligence and compliance sources before any enforcement,
                  disclosure, freezing, or legal action is considered.
                </p>

              </div>

            </div>

          </div>

        </section>

        {/* Footer */}
        <div className="border-t border-navy-800 pt-5 flex flex-col sm:flex-row justify-between gap-3 text-[10px] text-slate-500 font-mono print:border-gray-300 print:text-gray-600">

          <span>
            Automated Blockchain Intelligence & VASP Attribution Engine
          </span>

          <span>
            DEMO REPORT • NOT FOR OPERATIONAL USE
          </span>

        </div>

      </div>
    </div>
  );
}