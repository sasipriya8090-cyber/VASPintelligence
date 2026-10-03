import React, { useState, useMemo, useCallback } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType
} from '@xyflow/react';
import {
  GitFork,
  ZoomIn,
  ZoomOut,
  Maximize2,
  RefreshCw,
  Building2,
  AlertCircle,
  Wallet,
  ShieldAlert,
  ArrowRight,
  Info
} from 'lucide-react';
import CustomNode from '../components/CustomNode';
import DemoDisclaimerBanner from '../components/DemoDisclaimerBanner';
import RiskBadge from '../components/RiskBadge';

export default function WalletGraph() {
  const nodeTypes = useMemo(() => ({ customNode: CustomNode }), []);

  // Demo flow requirement:
  // Suspicious Wallet -> Wallet A -> Wallet B (plus VASP exchange endpoint)
  const initialNodes = [
    {
      id: 'node-suspicious',
      type: 'customNode',
      data: {
        label: 'Suspicious Target Wallet',
        sublabel: '0x71c7...8976f',
        fullAddress: '0x71c7656ec7ab88b098defb751b7401b5f6d8976f',
        role: 'Primary Origin Subject',
        riskLevel: 'HIGH',
        riskScore: 78.5,
        isTarget: true,
        notes: 'Inflow of 42.5 ETH followed by immediate split dispersal. Typology: Peeling Chain Structure.'
      },
      position: { x: 300, y: 40 }
    },
    {
      id: 'node-wallet-a',
      type: 'customNode',
      data: {
        label: 'Wallet A',
        sublabel: '0x742d...8f44e',
        fullAddress: '0x742d35cc6634c0532925a3b844bc454e4438f44e',
        role: 'Intermediary Pass-Through',
        riskLevel: 'MEDIUM',
        riskScore: 62.0,
        isTarget: false,
        notes: 'Intermediate hop holding balance for under 15 minutes before secondary transfer.'
      },
      position: { x: 300, y: 220 }
    },
    {
      id: 'node-wallet-b',
      type: 'customNode',
      data: {
        label: 'Wallet B',
        sublabel: '0x8920...73bfa',
        fullAddress: '0x89205a3e3b2db69dce6aa645f778d655fba73bfa',
        role: 'Secondary Dispersal Leaf',
        riskLevel: 'HIGH',
        riskScore: 74.0,
        isTarget: false,
        notes: 'Further divided into micro-fractions across unattributed accounts.'
      },
      position: { x: 140, y: 400 }
    },
    {
      id: 'node-vasp',
      type: 'customNode',
      data: {
        label: 'Demo Binance Hot Wallet',
        sublabel: '0x28c6...21d60',
        fullAddress: '0x28c6c06298d514db089934071355e5743bf21d60',
        role: 'Centralized Exchange (CEX)',
        riskLevel: 'LOW',
        riskScore: 15.0,
        isTarget: false,
        isVASP: true,
        notes: 'Identified VASP off-ramp endpoint. Synthetic attribution confidence: 95%.'
      },
      position: { x: 480, y: 400 }
    }
  ];

  const initialEdges = [
    {
      id: 'edge-suspicious-to-a',
      source: 'node-suspicious',
      target: 'node-wallet-a',
      animated: true,
      label: '42.5 ETH',
      markerEnd: { type: MarkerType.ArrowClosed, color: '#f59e0b' },
      style: { stroke: '#f59e0b', strokeWidth: 2 }
    },
    {
      id: 'edge-a-to-b',
      source: 'node-wallet-a',
      target: 'node-wallet-b',
      animated: true,
      label: '25.0 ETH',
      markerEnd: { type: MarkerType.ArrowClosed, color: '#ef4444' },
      style: { stroke: '#ef4444', strokeWidth: 2 }
    },
    {
      id: 'edge-a-to-vasp',
      source: 'node-wallet-a',
      target: 'node-vasp',
      animated: true,
      label: '16.85 ETH (CEX Off-Ramp)',
      markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' },
      style: { stroke: '#10b981', strokeWidth: 2 }
    }
  ];

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [selectedNode, setSelectedNode] = useState(initialNodes[0]);

  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
  }, []);

  const handleResetGraph = () => {
    setNodes(initialNodes);
    setEdges(initialEdges);
    setSelectedNode(initialNodes[0]);
  };

  return (
    <div className="space-y-6">
      <DemoDisclaimerBanner />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <GitFork className="w-5 h-5 text-cyan-400" />
            Interactive Wallet Fund-Flow Graph
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Visualization of multi-hop asset movement, peeling chains, and VASP exchange attribution nexus.
          </p>
        </div>

        <button
          onClick={handleResetGraph}
          className="flex items-center gap-2 px-3.5 py-2 bg-navy-800 hover:bg-navy-750 text-slate-300 rounded-xl text-xs font-semibold border border-navy-700 transition"
        >
          <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
          <span>Reset Layout</span>
        </button>
      </div>

      {/* Graph Container & Inspector Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* React Flow Canvas (3 cols) */}
        <div className="lg:col-span-3 bg-navy-950 border border-navy-750 rounded-2xl overflow-hidden h-[620px] relative shadow-2xl">
          {/* Canvas Floating Top Info */}
          <div className="absolute top-4 left-4 z-10 bg-navy-900/90 backdrop-blur-md border border-navy-750 px-3.5 py-2 rounded-xl text-xs flex items-center gap-3 shadow-lg">
            <span className="font-mono text-cyan-400 font-semibold text-[11px]">
              DEMO FLOW: Suspicious Wallet → Wallet A → Wallet B
            </span>
            <span className="text-[10px] bg-navy-950 px-2 py-0.5 rounded text-slate-400 font-mono">
              Draggable & Zoomable
            </span>
          </div>

          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            fitView
            fitViewOptions={{ padding: 0.3 }}
            attributionPosition="bottom-right"
          >
            <Background color="#1e293b" gap={20} size={1} />
            <Controls className="!bg-navy-900 !border-navy-750 !text-slate-300" />
            <MiniMap
              nodeColor={(n) => {
                if (n.data?.isVASP) return '#10b981';
                if (n.data?.isTarget) return '#f59e0b';
                return '#38bdf8';
              }}
              maskColor="rgba(7, 11, 20, 0.7)"
            />
          </ReactFlow>
        </div>

        {/* Selected Node Inspector Drawer (1 col) */}
        <div className="bg-navy-900 border border-navy-750 rounded-2xl p-5 shadow-xl flex flex-col h-[620px]">
          <div className="flex items-center justify-between pb-3 border-b border-navy-750">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <Info className="w-4 h-4 text-cyan-400" />
              Node Forensic Inspector
            </h3>
            <span className="text-[10px] font-mono text-slate-500">Live Focus</span>
          </div>

          {selectedNode ? (
            <div className="mt-4 flex-1 flex flex-col justify-between space-y-4 overflow-y-auto">
              <div className="space-y-4">
                <div>
                  <span className="text-[10px] font-mono uppercase text-slate-500 block">
                    Entity Designation
                  </span>
                  <h4 className="text-sm font-bold text-white mt-0.5">
                    {selectedNode.data.label}
                  </h4>
                  <div className="text-xs text-slate-400 font-mono mt-0.5">
                    {selectedNode.data.role}
                  </div>
                </div>

                <div className="bg-navy-950 p-3 rounded-xl border border-navy-800 space-y-1">
                  <span className="text-[10px] font-mono text-slate-500">Full Wallet Address</span>
                  <div className="text-xs font-mono text-cyan-400 break-all select-all">
                    {selectedNode.data.fullAddress}
                  </div>
                </div>

                <div className="space-y-1.5">
                  <span className="text-[10px] font-mono uppercase text-slate-500">
                    Risk Classification
                  </span>
                  <div className="flex items-center justify-between">
                    <RiskBadge
                      level={selectedNode.data.riskLevel}
                      score={selectedNode.data.riskScore}
                      size="sm"
                    />
                    <span className="text-xs font-mono text-slate-400">
                      Score: {selectedNode.data.riskScore}/100
                    </span>
                  </div>
                </div>

                <div className="bg-navy-850 p-3.5 rounded-xl border border-navy-750 text-xs text-slate-300 space-y-1">
                  <span className="text-[10px] font-bold uppercase text-amber-400 flex items-center gap-1 font-mono">
                    <ShieldAlert className="w-3.5 h-3.5" />
                    Investigative Context
                  </span>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    {selectedNode.data.notes}
                  </p>
                </div>
              </div>

              <div className="pt-4 border-t border-navy-800">
                <a
                  href={`/investigation?address=${selectedNode.data.fullAddress}`}
                  className="w-full py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-xl text-xs font-bold tracking-wide transition flex items-center justify-center gap-2"
                >
                  <span>Launch Deep Scan</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </a>
              </div>
            </div>
          ) : (
            <div className="m-auto text-center text-xs text-slate-500">
              Click any node in the graph above to inspect its forensic attribution and risk heuristics.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
