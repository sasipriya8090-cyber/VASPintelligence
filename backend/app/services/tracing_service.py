"""
Phase 3/4: Transaction Tracing Service — Fund-Flow Analysis + VASP Attribution.

Phase 3:
- Breadth-first fund-flow tracing
- Configurable hop depth
- Transaction graph generation
- React Flow serialization

Phase 4:
- VASP attribution for every traced node
- VASP name and type
- Attribution confidence
- Attribution source
- VASP node classification
"""

import datetime
import logging
from collections import deque
from typing import Any, Dict, List, Optional, Set, Tuple

from app.adapters.ethereum import EthereumAdapter
from app.core.config import settings
from app.services.vasp_service import VASPAttributionService


logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Safety limits
# ─────────────────────────────────────────────────────────────────────────────

ABSOLUTE_MAX_HOPS = 5
MAX_ADDRESSES_PER_TRACE = 50


# ═════════════════════════════════════════════════════════════════════════════
# Trace Node
# ═════════════════════════════════════════════════════════════════════════════


class TraceNode:
    """
    Represents a single wallet in the fund-flow graph.

    Phase 4 VASP attribution is stored in `vasp_info`.
    """

    __slots__ = (
        "address",
        "hop",
        "is_origin",
        "vasp_info",
        "flow_stats",
    )

    def __init__(
        self,
        address: str,
        hop: int,
        is_origin: bool = False,
        vasp_info: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.address = address.lower()
        self.hop = hop
        self.is_origin = is_origin
        self.vasp_info = vasp_info or {}

        self.flow_stats: Dict[str, Any] = {
            "total_incoming_eth": 0.0,
            "total_outgoing_eth": 0.0,
            "tx_count": 0,
            "unique_counterparties": set(),
        }

    def add_transaction(
        self,
        tx: Dict[str, Any],
        direction: str,
    ) -> None:
        """Update flow statistics from a normalized transaction."""

        amount = tx.get(
            "value_eth",
            tx.get("amount", 0.0),
        )

        counterparty = (
            tx.get("to_address", "").lower()
            if direction == "OUTGOING"
            else tx.get("from_address", "").lower()
        )

        if direction == "INCOMING":
            self.flow_stats["total_incoming_eth"] += amount

        elif direction == "OUTGOING":
            self.flow_stats["total_outgoing_eth"] += amount

        self.flow_stats["tx_count"] += 1

        if counterparty:
            self.flow_stats["unique_counterparties"].add(
                counterparty
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize node for API response."""

        fs = self.flow_stats
        vasp = self.vasp_info

        is_vasp = bool(vasp.get("matched"))

        vasp_name = (
            vasp.get("name")
            if is_vasp
            else None
        )

        return {
            "address": self.address,
            "hop": self.hop,
            "is_origin": self.is_origin,

            # ─────────────────────────────────────────────
            # VASP Attribution — Phase 4
            # ─────────────────────────────────────────────
            "is_vasp": is_vasp,
            "vasp_name": vasp_name,
            "vasp_type": (
                vasp.get("type")
                if is_vasp
                else None
            ),
            "vasp_confidence": (
                vasp.get("confidence")
                if is_vasp
                else None
            ),
            "vasp_source": (
                vasp.get("source")
                if is_vasp
                else None
            ),

            # ─────────────────────────────────────────────
            # Flow statistics
            # ─────────────────────────────────────────────
            "total_incoming_eth": round(
                fs["total_incoming_eth"],
                8,
            ),
            "total_outgoing_eth": round(
                fs["total_outgoing_eth"],
                8,
            ),
            "net_flow_eth": round(
                fs["total_incoming_eth"]
                - fs["total_outgoing_eth"],
                8,
            ),
            "tx_count": fs["tx_count"],
            "unique_counterparty_count": len(
                fs["unique_counterparties"]
            ),

            # Human-readable graph label
            "label": (
                "Origin Wallet"
                if self.is_origin
                else (
                    f"VASP: {vasp_name}"
                    if is_vasp
                    else f"Hop-{self.hop} Wallet"
                )
            ),

            "data_mode": settings.get_data_mode(),
        }


# ═════════════════════════════════════════════════════════════════════════════
# Trace Edge
# ═════════════════════════════════════════════════════════════════════════════


class TraceEdge:
    """A single normalized transaction in the fund-flow graph."""

    __slots__ = (
        "tx_hash",
        "from_address",
        "to_address",
        "value_eth",
        "token",
        "timestamp_iso",
        "block_number",
        "status",
        "gas_fee_eth",
        "direction",
        "data_mode",
    )

    def __init__(
        self,
        tx: Dict[str, Any],
    ) -> None:

        self.tx_hash = tx.get(
            "tx_hash",
            "",
        )

        self.from_address = tx.get(
            "from_address",
            "",
        ).lower()

        self.to_address = tx.get(
            "to_address",
            "",
        ).lower()

        self.value_eth = tx.get(
            "value_eth",
            tx.get("amount", 0.0),
        )

        self.token = tx.get(
            "token",
            "ETH",
        )

        self.timestamp_iso = tx.get(
            "timestamp_iso"
        )

        self.block_number = tx.get(
            "block_number"
        )

        self.status = tx.get(
            "status",
            "unknown",
        )

        self.gas_fee_eth = tx.get(
            "gas_fee_eth"
        )

        self.direction = tx.get(
            "direction",
            "UNKNOWN",
        )

        self.data_mode = tx.get(
            "data_mode",
            settings.get_data_mode(),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tx_hash": self.tx_hash,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "value_eth": round(
                self.value_eth,
                8,
            ),
            "token": self.token,
            "timestamp_iso": self.timestamp_iso,
            "block_number": self.block_number,
            "status": self.status,
            "gas_fee_eth": self.gas_fee_eth,
            "direction": self.direction,
            "data_mode": self.data_mode,
        }


# ═════════════════════════════════════════════════════════════════════════════
# Fund Flow Graph
# ═════════════════════════════════════════════════════════════════════════════


class FundFlowGraph:
    """Completed fund-flow trace containing nodes, edges and statistics."""

    def __init__(
        self,
        origin_address: str,
        max_hops: int,
        nodes: List[TraceNode],
        edges: List[TraceEdge],
        data_mode: str,
    ) -> None:

        self.origin_address = origin_address.lower()
        self.max_hops = max_hops
        self.nodes = nodes
        self.edges = edges
        self.data_mode = data_mode
        self.traced_at = datetime.datetime.now(
            datetime.timezone.utc
        )

    # ─────────────────────────────────────────────────────────────────────
    # Aggregate statistics
    # ─────────────────────────────────────────────────────────────────────

    def _origin_node(self) -> Optional[TraceNode]:
        for node in self.nodes:
            if node.is_origin:
                return node

        return None

    @property
    def total_volume_eth(self) -> float:
        return round(
            sum(
                edge.value_eth
                for edge in self.edges
            ),
            8,
        )

    @property
    def unique_address_count(self) -> int:
        return len(self.nodes)

    @property
    def transaction_count(self) -> int:
        return len(self.edges)

    @property
    def vasp_count(self) -> int:
        return sum(
            1
            for node in self.nodes
            if node.vasp_info.get("matched")
        )

    def to_summary(self) -> Dict[str, Any]:

        origin = self._origin_node()

        fs = (
            origin.flow_stats
            if origin
            else {}
        )

        return {
            "origin_address": self.origin_address,
            "max_hops": self.max_hops,
            "data_mode": self.data_mode,
            "traced_at": self.traced_at.isoformat(),

            "total_volume_eth": self.total_volume_eth,

            "total_incoming_eth": round(
                fs.get(
                    "total_incoming_eth",
                    0.0,
                ),
                8,
            ),

            "total_outgoing_eth": round(
                fs.get(
                    "total_outgoing_eth",
                    0.0,
                ),
                8,
            ),

            "transaction_count": self.transaction_count,

            "unique_address_count": self.unique_address_count,

            "vasp_count": self.vasp_count,

            "unique_direct_counterparties": len(
                fs.get(
                    "unique_counterparties",
                    set(),
                )
            ),
        }

    # ─────────────────────────────────────────────────────────────────────
    # React Flow serialization
    # ─────────────────────────────────────────────────────────────────────

    def to_react_flow(self) -> Dict[str, Any]:

        HORIZONTAL_GAP = 280
        VERTICAL_GAP = 130

        layers: Dict[
            int,
            List[TraceNode],
        ] = {}

        for node in self.nodes:
            layers.setdefault(
                node.hop,
                [],
            ).append(node)

        rf_nodes = []

        for hop, hop_nodes in sorted(
            layers.items()
        ):

            for idx, node in enumerate(
                hop_nodes
            ):

                nd = node.to_dict()

                # Node classification
                if node.is_origin:
                    node_type = "originNode"

                elif nd["is_vasp"]:
                    node_type = "vaspNode"

                elif node.hop == self.max_hops:
                    node_type = "leafNode"

                else:
                    node_type = "customNode"

                total_in_layer = len(
                    hop_nodes
                )

                y_offset = (
                    idx
                    - (
                        total_in_layer - 1
                    ) / 2
                ) * VERTICAL_GAP

                rf_nodes.append(
                    {
                        "id": node.address,
                        "type": "customNode",
                        "nodeType": node_type,

                        "position": {
                            "x": (
                                hop
                                * HORIZONTAL_GAP
                                + 60
                            ),
                            "y": (
                                300
                                + y_offset
                            ),
                        },

                        "data": {
                            "label": nd["label"],
                            "sublabel": (
                                f"{node.address[:8]}"
                                f"…"
                                f"{node.address[-6:]}"
                            ),
                            "fullAddress": node.address,

                            "hop": node.hop,

                            "isOrigin": (
                                node.is_origin
                            ),

                            "isVASP": nd[
                                "is_vasp"
                            ],

                            "vaspName": nd[
                                "vasp_name"
                            ],

                            "vaspType": nd[
                                "vasp_type"
                            ],

                            "vaspConfidence": nd[
                                "vasp_confidence"
                            ],

                            "vaspSource": nd[
                                "vasp_source"
                            ],

                            "totalIncomingEth": nd[
                                "total_incoming_eth"
                            ],

                            "totalOutgoingEth": nd[
                                "total_outgoing_eth"
                            ],

                            "netFlowEth": nd[
                                "net_flow_eth"
                            ],

                            "txCount": nd[
                                "tx_count"
                            ],

                            "uniqueCounterparties": nd[
                                "unique_counterparty_count"
                            ],

                            "dataMode": nd[
                                "data_mode"
                            ],
                        },
                    }
                )

        # ─────────────────────────────────────────────────────────────────
        # Edges
        # ─────────────────────────────────────────────────────────────────

        rf_edges = []

        seen_edge_ids: Set[str] = set()

        for edge in self.edges:

            edge_id = (
                f"edge-{edge.tx_hash}"
                if edge.tx_hash
                else (
                    "edge-"
                    f"{edge.from_address}"
                    f"{edge.to_address}"
                )
            )

            if edge_id in seen_edge_ids:
                continue

            seen_edge_ids.add(
                edge_id
            )

            if edge.value_eth >= 10.0:
                stroke = "#ef4444"

            elif edge.value_eth >= 1.0:
                stroke = "#f59e0b"

            else:
                stroke = "#6b7280"

            rf_edges.append(
                {
                    "id": edge_id,
                    "source": edge.from_address,
                    "target": edge.to_address,
                    "animated": True,
                    "label": (
                        f"{edge.value_eth:.4f}"
                        f" {edge.token}"
                    ),
                    "style": {
                        "stroke": stroke,
                        "strokeWidth": 2,
                    },
                    "data": edge.to_dict(),
                }
            )

        return {
            "nodes": rf_nodes,
            "edges": rf_edges,
        }


# ═════════════════════════════════════════════════════════════════════════════
# Transaction Tracing Service
# ═════════════════════════════════════════════════════════════════════════════


class TransactionTracingService:
    """
    Phase 3/4 breadth-first fund-flow tracer.

    Phase 4 enhancement:
    Every wallet encountered during traversal is checked against
    the VASP attribution registry.
    """

    def __init__(
        self,
        adapter: Optional[EthereumAdapter] = None,
        vasp_service: Optional[VASPAttributionService] = None,
    ) -> None:

        self._adapter = (
            adapter
            or EthereumAdapter()
        )

        self._vasp_service = (
            vasp_service
            or VASPAttributionService()
        )

    # ─────────────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────────────

    async def trace(
        self,
        wallet_address: str,
        max_hops: int = 2,
        page_size: int = 25,
    ) -> FundFlowGraph:

        max_hops = min(
            max(1, max_hops),
            ABSOLUTE_MAX_HOPS,
        )

        origin = wallet_address.strip().lower()

        nodes: Dict[
            str,
            TraceNode,
        ] = {}

        edges: List[
            TraceEdge
        ] = []

        visited: Set[str] = set()

        queue: deque[
            Tuple[str, int]
        ] = deque()

        queue.append(
            (origin, 0)
        )

        # ─────────────────────────────────────────────────────────────────
        # BFS traversal
        # ─────────────────────────────────────────────────────────────────

        while (
            queue
            and len(visited)
            < MAX_ADDRESSES_PER_TRACE
        ):

            address, hop = queue.popleft()

            if address in visited:
                continue

            visited.add(address)

            # ─────────────────────────────────────────────────────────────
            # VASP Attribution
            # ─────────────────────────────────────────────────────────────

            if address not in nodes:

                vasp_info = (
                    self._vasp_service.identify_vasp(
                        address,
                        "ethereum",
                    )
                )

                nodes[address] = TraceNode(
                    address=address,
                    hop=hop,
                    is_origin=(
                        address == origin
                    ),
                    vasp_info=vasp_info,
                )

            node = nodes[address]

            # ─────────────────────────────────────────────────────────────
            # Fetch transactions
            # ─────────────────────────────────────────────────────────────

            try:

                txs = await self._adapter.get_transactions(
                    address,
                    page=1,
                    page_size=page_size,
                )

            except Exception as exc:

                logger.warning(
                    "[Tracer] Could not fetch transactions "
                    "for %s at hop %d: %s",
                    address[:10] + "…",
                    hop,
                    exc,
                )

                txs = []

            # ─────────────────────────────────────────────────────────────
            # Process transactions
            # ─────────────────────────────────────────────────────────────

            for tx in txs:

                from_addr = tx.get(
                    "from_address",
                    "",
                ).lower()

                to_addr = tx.get(
                    "to_address",
                    "",
                ).lower()

                if not from_addr or not to_addr:
                    continue

                # Determine transaction direction
                if from_addr == address:

                    direction = "OUTGOING"
                    counterparty = to_addr

                elif to_addr == address:

                    direction = "INCOMING"
                    counterparty = from_addr

                else:
                    continue

                # Update flow statistics
                tx_with_dir = {
                    **tx,
                    "direction": direction,
                }

                node.add_transaction(
                    tx_with_dir,
                    direction,
                )

                # Create graph edge
                trace_edge = TraceEdge(
                    tx_with_dir
                )

                edges.append(
                    trace_edge
                )

                # ─────────────────────────────────────────────────────────
                # VASP Attribution for Counterparty
                # ─────────────────────────────────────────────────────────

                if counterparty not in nodes:

                    cp_vasp = (
                        self._vasp_service.identify_vasp(
                            counterparty,
                            "ethereum",
                        )
                    )

                    nodes[counterparty] = TraceNode(
                        address=counterparty,
                        hop=hop + 1,
                        is_origin=False,
                        vasp_info=cp_vasp,
                    )

                # Continue BFS if depth allows
                if (
                    hop < max_hops
                    and counterparty not in visited
                ):

                    queue.append(
                        (
                            counterparty,
                            hop + 1,
                        )
                    )

        # ─────────────────────────────────────────────────────────────────
        # Deduplicate edges
        # ─────────────────────────────────────────────────────────────────

        seen_hashes: Set[str] = set()

        deduped_edges: List[
            TraceEdge
        ] = []

        for edge in edges:

            key = (
                edge.tx_hash
                if edge.tx_hash
                else (
                    f"{edge.from_address}:"
                    f"{edge.to_address}:"
                    f"{edge.value_eth}"
                )
            )

            if key in seen_hashes:
                continue

            seen_hashes.add(key)

            deduped_edges.append(
                edge
            )

        logger.info(
            "[Tracer] Trace complete: "
            "origin=%s nodes=%d edges=%d hops=%d vasps=%d",
            origin[:10] + "…",
            len(nodes),
            len(deduped_edges),
            max_hops,
            sum(
                1
                for node in nodes.values()
                if node.vasp_info.get(
                    "matched"
                )
            ),
        )

        return FundFlowGraph(
            origin_address=origin,
            max_hops=max_hops,
            nodes=list(
                nodes.values()
            ),
            edges=deduped_edges,
            data_mode=settings.get_data_mode(),
        )