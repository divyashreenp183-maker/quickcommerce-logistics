"""
Main Logistics Optimizer for the NeuralOps Logistics System.
Orchestrates the full order processing pipeline:
Store Selection → Rider Assignment → SLA Check → Self-Healing → Profit Calculation
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

from models.order import Order, OrderStatus
from models.rider import Rider
from models.store import DarkStore
from engine.store_selector import StoreSelector
from engine.rider_assigner import RiderAssigner
from engine.sla_engine import SLAEngine, SLAResult
from engine.profit_engine import ProfitEngine, ProfitResult


@dataclass
class OrderResult:
    """Complete result of processing one order through the logistics pipeline."""
    order: Order
    store: Optional[DarkStore]
    rider: Optional[Rider]
    sla_result: Optional[SLAResult]
    profit_result: Optional[ProfitResult]
    store_decision: Dict = field(default_factory=dict)
    rider_decision: Dict = field(default_factory=dict)
    explanation: str = ""
    insights: List[str] = field(default_factory=list)
    healed: bool = False
    success: bool = False


class LogisticsOptimizer:
    """
    Central orchestration engine for the NeuralOps Logistics System.
    Processes orders end-to-end and integrates all subsystems.
    """

    def __init__(
        self,
        stores: List[DarkStore],
        riders: List[Rider],
        profit_engine: Optional[ProfitEngine] = None,
        enable_self_healing: bool = True,
    ):
        self.stores = stores
        self.riders = riders
        self.profit_engine = profit_engine or ProfitEngine()
        self.enable_self_healing = enable_self_healing

        self._store_selector = StoreSelector()
        self._rider_assigner = RiderAssigner()
        self._sla_engine = SLAEngine()
        self._processed_orders: List[OrderResult] = []

    def process_order(self, order: Order) -> OrderResult:
        """
        Process a single order through the full logistics pipeline.

        Pipeline:
        1. Select best store
        2. Assign best rider
        3. Evaluate SLA
        4. Self-heal if SLA is breached
        5. Calculate profit
        6. Update state
        """
        result = OrderResult(order=order, store=None, rider=None,
                             sla_result=None, profit_result=None)

        # ── Step 1: Store Selection ──────────────────────────────────────────
        store, store_decision = self._store_selector.select(order, self.stores)
        if store is None:
            order.status = OrderStatus.FAILED
            result.explanation = "❌ No stores available — order failed."
            self._processed_orders.append(result)
            return result

        result.store = store
        result.store_decision = store_decision

        # ── Step 2: Rider Assignment ─────────────────────────────────────────
        rider, rider_decision = self._rider_assigner.assign(order, store, self.riders)
        if rider is None:
            order.status = OrderStatus.FAILED
            result.explanation = "❌ No riders available — order failed."
            self._processed_orders.append(result)
            return result

        result.rider = rider
        result.rider_decision = rider_decision

        # ── Step 3: SLA Evaluation ───────────────────────────────────────────
        sla_result = self._sla_engine.evaluate(order, rider, store)
        result.sla_result = sla_result

        # ── Step 4: Self-Healing (if SLA breached and healing enabled) ───────
        if not sla_result.sla_met and self.enable_self_healing:
            healed_result = self._attempt_heal(order, store, rider, result)
            if healed_result:
                result = healed_result
                result.healed = True
                order.status = OrderStatus.HEALED
            else:
                order.status = OrderStatus.FAILED
                result.success = False
                order.sla_met = False
                self._processed_orders.append(result)
                return result
        elif not sla_result.sla_met:
            order.status = OrderStatus.FAILED
            order.sla_met = False
            result.success = False
            self._processed_orders.append(result)
            return result

        # ── Step 5: Profit Calculation ───────────────────────────────────────
        if result.sla_result:
            total_km = (result.sla_result.rider_to_store_km
                        + result.sla_result.store_to_customer_km)
            total_min = result.sla_result.total_time_min
            profit_result = self.profit_engine.calculate(order, total_km, total_min)
            result.profit_result = profit_result
            order.profit = profit_result.profit
            order.delivery_cost = profit_result.total_delivery_cost

        # ── Step 6: Update State ─────────────────────────────────────────────
        store.accept_order()
        rider.assign_order(order.id)
        order.status = OrderStatus.IN_TRANSIT
        order.assigned_store_id = result.store.id
        order.assigned_rider_id = result.rider.id
        order.estimated_delivery_min = result.sla_result.total_time_min
        order.sla_met = result.sla_result.sla_met
        result.success = True

        self._processed_orders.append(result)
        return result

    def _attempt_heal(
        self,
        order: Order,
        original_store: DarkStore,
        original_rider: Rider,
        original_result: OrderResult,
    ) -> Optional[OrderResult]:
        """
        Attempt self-healing by trying:
        1. Different rider (same store)
        2. Different store + different rider
        Returns a new OrderResult if healing succeeds, else None.
        """
        # Strategy 1: Try other riders with same store
        other_riders = [r for r in self.riders
                        if r.is_available and r.id != original_rider.id]
        for rider in other_riders:
            sla = self._sla_engine.evaluate(order, rider, original_store)
            if sla.sla_met:
                result = OrderResult(
                    order=order,
                    store=original_store,
                    rider=rider,
                    sla_result=sla,
                    profit_result=None,
                    store_decision=original_result.store_decision,
                    rider_decision={"healed": True, "strategy": "rider_swap",
                                    "selected_rider_id": rider.id,
                                    "selected_rider_name": rider.name},
                )
                return result

        # Strategy 2: Try other stores with any rider
        other_stores = [s for s in self.stores if s.id != original_store.id]
        for store in other_stores:
            if not store.check_availability(order.items):
                continue
            _, s_meta = self._store_selector.select(order, [store])
            for rider in [original_rider] + other_riders:
                if not rider.is_available:
                    continue
                sla = self._sla_engine.evaluate(order, rider, store)
                if sla.sla_met:
                    result = OrderResult(
                        order=order,
                        store=store,
                        rider=rider,
                        sla_result=sla,
                        profit_result=None,
                        store_decision={**s_meta, "healed": True,
                                        "strategy": "store_swap"},
                        rider_decision={"healed": True,
                                        "selected_rider_id": rider.id,
                                        "selected_rider_name": rider.name},
                    )
                    return result

        return None  # Could not heal

    def process_batch(self, orders: List[Order]) -> List[OrderResult]:
        """Process a list of orders, sorting HIGH priority first."""
        from models.order import Priority
        sorted_orders = sorted(
            orders,
            key=lambda o: (0 if o.priority == Priority.HIGH else 1, o.timestamp)
        )
        return [self.process_order(o) for o in sorted_orders]

    @property
    def processed_orders(self) -> List[OrderResult]:
        return self._processed_orders

    def get_system_stats(self) -> Dict:
        """Aggregate system-level statistics across all processed orders."""
        total = len(self._processed_orders)
        if total == 0:
            return {"total_orders": 0}

        successful = sum(1 for r in self._processed_orders if r.success)
        healed = sum(1 for r in self._processed_orders if r.healed)
        sla_met = sum(1 for r in self._processed_orders
                      if r.sla_result and r.sla_result.sla_met)
        avg_time = (
            sum(r.sla_result.total_time_min for r in self._processed_orders
                if r.sla_result)
            / max(1, sum(1 for r in self._processed_orders if r.sla_result))
        )

        return {
            "total_orders": total,
            "successful_deliveries": successful,
            "failed_deliveries": total - successful,
            "sla_met_count": sla_met,
            "sla_success_rate_pct": round(sla_met / total * 100, 1),
            "self_healed_count": healed,
            "avg_delivery_time_min": round(avg_time, 2),
            **self.profit_engine.get_summary(),
        }
