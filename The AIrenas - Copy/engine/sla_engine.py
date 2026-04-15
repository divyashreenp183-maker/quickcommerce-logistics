"""
SLA Enforcement Engine for the NeuralOps Logistics System.
Feature 3: Calculate total delivery time and enforce the 10-minute SLA.
           HIGH priority orders get a stricter 8-minute threshold.
"""
from dataclasses import dataclass
from typing import Optional, Dict
from models.order import Order, Priority
from models.rider import Rider
from models.store import DarkStore
from engine.distance import haversine, estimate_travel_time


@dataclass
class SLAResult:
    """Result of an SLA check."""
    rider_to_store_km: float
    rider_to_store_min: float
    store_to_customer_km: float
    store_to_customer_min: float
    total_time_min: float
    sla_threshold_min: float
    sla_met: bool
    risk_level: str   # "LOW", "MEDIUM", "HIGH"
    flagged: bool     # True if projected time is within 1.5 min of threshold


class SLAEngine:
    """
    Enforces the 10-minute (or 8-minute for HIGH priority) SLA.
    Computes end-to-end delivery time and flags risky orders.
    """

    # Risk detection margin: flag if within this many minutes of SLA threshold
    RISK_MARGIN_MIN = 1.5

    def evaluate(
        self,
        order: Order,
        rider: Rider,
        store: DarkStore
    ) -> SLAResult:
        """
        Evaluate whether an order can be delivered within SLA.

        Delivery time = (Rider → Store) + (Store → Customer)
        """
        # Leg 1: Rider to Store
        r2s_km = haversine(rider.location, store.location)
        r2s_min = estimate_travel_time(r2s_km, rider.speed_kmph)

        # Leg 2: Store to Customer (riders typically go 25 km/h after pickup)
        s2c_km = haversine(store.location, order.location)
        s2c_min = estimate_travel_time(s2c_km, rider.speed_kmph)

        # Add 1 min fixed store preparation time
        total_min = r2s_min + s2c_min + 1.0

        threshold = order.sla_threshold_min
        sla_met = total_min <= threshold

        # Risk level calculation
        gap = threshold - total_min
        if gap < 0:
            risk_level = "HIGH"       # Already breached
        elif gap <= self.RISK_MARGIN_MIN:
            risk_level = "MEDIUM"     # Close to breach
        else:
            risk_level = "LOW"        # Safe

        flagged = risk_level in ("MEDIUM", "HIGH")

        return SLAResult(
            rider_to_store_km=round(r2s_km, 3),
            rider_to_store_min=round(r2s_min, 2),
            store_to_customer_km=round(s2c_km, 3),
            store_to_customer_min=round(s2c_min, 2),
            total_time_min=round(total_min, 2),
            sla_threshold_min=threshold,
            sla_met=sla_met,
            risk_level=risk_level,
            flagged=flagged,
        )

    def to_dict(self, result: SLAResult) -> Dict:
        """Serialize SLAResult to a plain dict for logging/display."""
        return {
            "rider_to_store_km": result.rider_to_store_km,
            "rider_to_store_min": result.rider_to_store_min,
            "store_to_customer_km": result.store_to_customer_km,
            "store_to_customer_min": result.store_to_customer_min,
            "total_time_min": result.total_time_min,
            "sla_threshold_min": result.sla_threshold_min,
            "sla_met": result.sla_met,
            "risk_level": result.risk_level,
            "flagged": result.flagged,
        }
