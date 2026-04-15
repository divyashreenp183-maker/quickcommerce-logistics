"""
SLA Risk Detector for the NeuralOps Logistics System.
Feature 9: Proactively scans pending/in-transit orders to identify
           those at risk of SLA breach and suggest corrective action.
"""
from typing import List, Dict, Tuple, Optional
from models.order import Order, OrderStatus
from models.rider import Rider
from models.store import DarkStore
from engine.sla_engine import SLAEngine
from engine.distance import haversine


class SLARiskDetector:
    """
    Proactively identifies orders at risk of SLA breach before delivery.
    Provides specific remediation suggestions.
    """

    # Orders within this many minutes of breaching are flagged
    RISK_WINDOW_MIN = 2.0

    def __init__(self):
        self._sla_engine = SLAEngine()

    def scan(
        self,
        orders: List[Order],
        riders: List[Rider],
        stores: List[DarkStore],
    ) -> List[Dict]:
        """
        Scan all active orders and identify SLA risks.

        Returns a list of risk reports, one per at-risk order.
        """
        risk_reports = []

        active_statuses = {OrderStatus.PENDING, OrderStatus.IN_TRANSIT,
                           OrderStatus.ASSIGNED}
        active_orders = [o for o in orders if o.status in active_statuses]

        for order in active_orders:
            # Find the assigned or best candidate store
            if order.assigned_store_id:
                store = next((s for s in stores if s.id == order.assigned_store_id), None)
            else:
                # Pick closest store as proxy
                store = min(stores, key=lambda s: haversine(s.location, order.location),
                            default=None)

            if store is None:
                continue

            # Find the assigned rider
            if order.assigned_rider_id:
                rider = next((r for r in riders if r.id == order.assigned_rider_id), None)
            else:
                # Use nearest available rider as proxy
                avail = [r for r in riders if r.is_available]
                rider = min(avail, key=lambda r: haversine(r.location, store.location),
                            default=None) if avail else None

            if rider is None:
                continue

            sla = self._sla_engine.evaluate(order, rider, store)

            if sla.flagged:
                report = self._build_risk_report(order, store, rider, sla, stores, riders)
                risk_reports.append(report)

        return risk_reports

    def _build_risk_report(
        self,
        order: Order,
        current_store: DarkStore,
        current_rider: Rider,
        sla: "SLAResult",
        all_stores: List[DarkStore],
        all_riders: List[Rider],
    ) -> Dict:
        """Build a detailed risk report with suggestions."""
        suggestions = []
        gap = sla.sla_threshold_min - sla.total_time_min

        if not sla.sla_met:
            overage = sla.total_time_min - sla.sla_threshold_min
            severity = "CRITICAL"
            summary = (f"Order {order.id} will BREACH SLA by {overage:.1f} min "
                       f"({sla.total_time_min:.1f} vs {sla.sla_threshold_min:.0f}-min threshold).")
        else:
            severity = "WARNING"
            summary = (f"Order {order.id} is close to SLA breach — only {gap:.1f} min margin "
                       f"({sla.total_time_min:.1f} / {sla.sla_threshold_min:.0f} min).")

        # Suggest faster rider
        faster_riders = sorted(
            [r for r in all_riders if r.is_available and r.id != current_rider.id],
            key=lambda r: haversine(r.location, current_store.location)
        )
        if faster_riders:
            best = faster_riders[0]
            dist = haversine(best.location, current_store.location)
            suggestions.append(
                f"🔁 Reassign to {best.name} ({best.id}) — "
                f"{dist:.2f} km from store, efficiency {best.efficiency_score:.0%}"
            )

        # Suggest closer store
        nearer_stores = sorted(
            [s for s in all_stores if s.id != current_store.id
             and s.check_availability(order.items)],
            key=lambda s: haversine(s.location, order.location)
        )
        if nearer_stores:
            best_store = nearer_stores[0]
            dist = haversine(best_store.location, order.location)
            suggestions.append(
                f"🏪 Switch to {best_store.name} ({best_store.id}) — "
                f"{dist:.2f} km from customer, load {best_store.load_factor:.0%}"
            )

        if not suggestions:
            suggestions.append("⚠️ No immediate alternatives found — escalate manually.")

        return {
            "order_id": order.id,
            "severity": severity,
            "summary": summary,
            "current_time_min": round(sla.total_time_min, 2),
            "sla_threshold_min": sla.sla_threshold_min,
            "risk_level": sla.risk_level,
            "suggestions": suggestions,
        }
