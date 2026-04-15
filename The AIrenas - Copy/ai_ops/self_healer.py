"""
Self-Healing System for the NeuralOps Logistics System.
Feature 11: Automatically detects delivery delays and reassigns riders/stores
            to ensure SLA compliance without human intervention.
"""
from typing import List, Dict, Optional, Tuple
from models.order import Order, OrderStatus
from models.rider import Rider
from models.store import DarkStore
from engine.sla_engine import SLAEngine
from engine.store_selector import StoreSelector
from engine.rider_assigner import RiderAssigner
from engine.distance import haversine


class SelfHealer:
    """
    Autonomous self-healing subsystem that detects and corrects SLA breaches.
    Tries multiple healing strategies in order of cost/disruption.
    """

    STRATEGIES = ["RIDER_SWAP", "STORE_SWAP", "RIDER_AND_STORE_SWAP"]

    def __init__(self):
        self._sla_engine = SLAEngine()
        self._store_selector = StoreSelector()
        self._rider_assigner = RiderAssigner()
        self._heal_log: List[Dict] = []

    def heal(
        self,
        order: Order,
        current_store: DarkStore,
        current_rider: Rider,
        all_stores: List[DarkStore],
        all_riders: List[Rider],
    ) -> Tuple[bool, Optional[DarkStore], Optional[Rider], str]:
        """
        Attempt to heal an order that will breach SLA.

        Returns:
            (success, new_store, new_rider, strategy_used)
        """
        for strategy in self.STRATEGIES:
            result = self._apply_strategy(
                strategy, order, current_store, current_rider,
                all_stores, all_riders
            )
            if result:
                new_store, new_rider = result
                log_entry = {
                    "order_id": order.id,
                    "strategy": strategy,
                    "original_store": current_store.id,
                    "original_rider": current_rider.id,
                    "new_store": new_store.id,
                    "new_rider": new_rider.id,
                    "healed": True,
                }
                self._heal_log.append(log_entry)
                return True, new_store, new_rider, strategy

        # All strategies failed
        self._heal_log.append({
            "order_id": order.id,
            "strategy": "NONE",
            "healed": False,
        })
        return False, None, None, "NONE"

    def _apply_strategy(
        self,
        strategy: str,
        order: Order,
        current_store: DarkStore,
        current_rider: Rider,
        all_stores: List[DarkStore],
        all_riders: List[Rider],
    ) -> Optional[Tuple[DarkStore, Rider]]:
        """Apply a specific healing strategy and return (store, rider) if successful."""
        other_riders = [r for r in all_riders
                        if r.is_available and r.id != current_rider.id]
        other_stores = [s for s in all_stores
                        if s.id != current_store.id and s.check_availability(order.items)]

        if strategy == "RIDER_SWAP":
            # Keep same store, try different riders sorted by proximity
            candidates = sorted(other_riders,
                                key=lambda r: haversine(r.location, current_store.location))
            for rider in candidates:
                sla = self._sla_engine.evaluate(order, rider, current_store)
                if sla.sla_met:
                    return current_store, rider

        elif strategy == "STORE_SWAP":
            # Keep same rider, try different stores sorted by proximity to customer
            candidate_stores = sorted(other_stores,
                                      key=lambda s: haversine(s.location, order.location))
            for store in candidate_stores:
                sla = self._sla_engine.evaluate(order, current_rider, store)
                if sla.sla_met:
                    return store, current_rider

        elif strategy == "RIDER_AND_STORE_SWAP":
            # Try all combinations of other stores + other riders
            candidate_stores = sorted(other_stores,
                                      key=lambda s: haversine(s.location, order.location))
            for store in candidate_stores:
                candidates = sorted(other_riders,
                                    key=lambda r: haversine(r.location, store.location))
                for rider in candidates:
                    sla = self._sla_engine.evaluate(order, rider, store)
                    if sla.sla_met:
                        return store, rider

        return None

    def get_heal_log(self) -> List[Dict]:
        return self._heal_log

    def get_heal_summary(self) -> Dict:
        total = len(self._heal_log)
        healed = sum(1 for e in self._heal_log if e["healed"])
        strategies_used = {}
        for e in self._heal_log:
            if e["healed"]:
                s = e["strategy"]
                strategies_used[s] = strategies_used.get(s, 0) + 1

        return {
            "total_healing_attempts": total,
            "successful_heals": healed,
            "failed_heals": total - healed,
            "heal_success_rate_pct": round(healed / total * 100, 1) if total > 0 else 0,
            "strategies_used": strategies_used,
        }
