"""
Explainable Decision Engine for the NeuralOps Logistics System.
Feature 8: Generates human-readable explanations for every logistics decision.
"""
from typing import Optional, Dict
from models.order import Order, Priority
from models.store import DarkStore
from models.rider import Rider
from engine.sla_engine import SLAResult
from engine.profit_engine import ProfitResult


class DecisionExplainer:
    """
    Converts raw decision metadata into clear, human-readable narrative explanations.
    This makes the system's autonomous decisions transparent and understandable.
    """

    def explain_store_selection(
        self,
        store: DarkStore,
        metadata: Dict,
    ) -> str:
        """Generate explanation for why a specific store was selected."""
        dist = metadata.get("distance_km", 0)
        avail = metadata.get("availability_score", 0)
        load = metadata.get("load_factor", 0)
        candidates = metadata.get("all_candidates", [])
        n_candidates = len(candidates)

        avail_pct = int(avail * 100)
        load_pct = int(load * 100)

        reasons = []
        if dist < 1.5:
            reasons.append(f"very close at {dist:.2f} km")
        elif dist < 3.0:
            reasons.append(f"within reach at {dist:.2f} km")
        else:
            reasons.append(f"nearest viable option at {dist:.2f} km")

        if avail_pct >= 90:
            reasons.append(f"excellent stock ({avail_pct}% availability)")
        elif avail_pct >= 60:
            reasons.append(f"adequate stock ({avail_pct}% availability)")
        else:
            reasons.append(f"partial stock ({avail_pct}% availability)")

        if load_pct < 30:
            reasons.append(f"low workload ({load_pct}% capacity used)")
        elif load_pct < 70:
            reasons.append(f"moderate workload ({load_pct}% capacity used)")
        else:
            reasons.append(f"high load ({load_pct}% capacity used)")

        healed = metadata.get("healed", False)
        prefix = "🔄 [SELF-HEALED] Store switched to" if healed else "🏪 Store selected:"
        return (
            f"{prefix} {store.name} ({store.id}) — "
            + ", ".join(reasons)
            + f". Best among {n_candidates} candidate(s)."
        )

    def explain_rider_assignment(
        self,
        rider: Rider,
        metadata: Dict,
        sla_result: SLAResult,
    ) -> str:
        """Generate explanation for why a specific rider was assigned."""
        dist = metadata.get("distance_to_store_km", 0)
        pickup_min = metadata.get("pickup_time_min", 0)
        eff = metadata.get("efficiency_score", 0)
        load = metadata.get("workload_score", 0)
        candidates = metadata.get("all_candidates", [])
        n_candidates = len(candidates)

        eff_pct = int(eff * 100)
        load_pct = int(load * 100)

        reasons = []
        if dist < 1.0:
            reasons.append(f"nearest to store ({dist:.2f} km away)")
        else:
            reasons.append(f"{dist:.2f} km from store (pickup est. {pickup_min:.1f} min)")

        if eff_pct >= 90:
            reasons.append(f"top efficiency ({eff_pct}%)")
        elif eff_pct >= 75:
            reasons.append(f"good efficiency ({eff_pct}%)")
        else:
            reasons.append(f"efficiency at {eff_pct}%")

        if load_pct == 0:
            reasons.append("fully free (no active orders)")
        elif load_pct < 50:
            reasons.append(f"light workload ({load_pct}% loaded)")
        else:
            reasons.append(f"workload at {load_pct}%")

        healed = metadata.get("healed", False)
        strategy = metadata.get("strategy", "")
        if healed and strategy == "rider_swap":
            prefix = "🔄 [SELF-HEALED] Rider swapped to"
        else:
            prefix = "🚴 Rider assigned:"

        return (
            f"{prefix} {rider.name} ({rider.id}) — "
            + ", ".join(reasons)
            + f". Selected from {n_candidates} available rider(s)."
        )

    def explain_sla(
        self,
        order: Order,
        sla_result: SLAResult,
    ) -> str:
        """Generate explanation for the SLA evaluation outcome."""
        total = sla_result.total_time_min
        threshold = sla_result.sla_threshold_min
        r2s = sla_result.rider_to_store_min
        s2c = sla_result.store_to_customer_min
        priority_label = "🔴 HIGH" if order.priority == Priority.HIGH else "🟡 NORMAL"

        breakdown = (f"Pickup: {r2s:.1f} min + Delivery: {s2c:.1f} min + "
                     f"Prep: 1.0 min = {total:.1f} min total")

        if sla_result.sla_met:
            margin = threshold - total
            return (
                f"✅ SLA MET [{priority_label} priority, {threshold:.0f}-min SLA] — "
                f"{breakdown}. Margin: {margin:.1f} min to spare."
            )
        else:
            overage = total - threshold
            return (
                f"⚠️  SLA BREACH [{priority_label} priority, {threshold:.0f}-min SLA] — "
                f"{breakdown}. Over by {overage:.1f} min. Self-healing triggered."
            )

    def explain_profit(
        self,
        profit_result: ProfitResult,
    ) -> str:
        """Generate explanation for the profit/cost breakdown."""
        p = profit_result
        emoji = "💚" if p.profit > 0 else "🔴"
        return (
            f"{emoji} Profit: ₹{p.profit:.2f} ({p.margin_pct:.1f}% margin) — "
            f"Revenue: ₹{p.order_revenue:.2f} | "
            f"Cost: ₹{p.total_delivery_cost:.2f} "
            f"[Base: ₹{p.base_cost:.2f} + Dist: ₹{p.distance_cost:.2f} "
            f"+ Time: ₹{p.time_cost:.2f} + Commission: ₹{p.platform_commission:.2f}]"
        )

    def full_explanation(
        self,
        order: Order,
        store: Optional[DarkStore],
        rider: Optional[Rider],
        store_decision: Dict,
        rider_decision: Dict,
        sla_result: Optional[SLAResult],
        profit_result: Optional[ProfitResult],
        healed: bool = False,
    ) -> str:
        """Compose the full multi-line explanation for an order."""
        lines = [f"\n{'='*60}"]
        lines.append(f"  ORDER {order.id} — {order.priority.value} PRIORITY")
        lines.append(f"{'='*60}")

        if store:
            lines.append(self.explain_store_selection(store, store_decision))
        if rider and sla_result:
            lines.append(self.explain_rider_assignment(rider, rider_decision, sla_result))
        if sla_result:
            lines.append(self.explain_sla(order, sla_result))
        if profit_result:
            lines.append(self.explain_profit(profit_result))
        if healed:
            lines.append("🛠️  System autonomously healed this order to meet SLA.")

        lines.append(f"{'='*60}")
        return "\n".join(lines)
