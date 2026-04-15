"""
Rider model for the NeuralOps Logistics System.
Represents a delivery partner with location, efficiency, and workload tracking.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Rider:
    """Represents a delivery partner / rider."""
    id: str
    name: str
    location: tuple          # (latitude, longitude)
    speed_kmph: float        # Average delivery speed in km/h
    efficiency_score: float  # 0.0 – 1.0 (1.0 = perfect on-time rate)
    is_available: bool = True

    # Runtime state
    current_orders: List[str] = field(default_factory=list, init=False)
    completed_deliveries: int = field(default=0, init=False)
    total_delivery_time: float = field(default=0.0, init=False)  # minutes
    total_earnings: float = field(default=0.0, init=False)       # INR

    def assign_order(self, order_id: str):
        """Assign an order to this rider."""
        self.current_orders.append(order_id)
        if len(self.current_orders) >= 3:
            self.is_available = False

    def complete_order(self, order_id: str, delivery_time_min: float, earnings: float):
        """Mark an order as completed by this rider."""
        if order_id in self.current_orders:
            self.current_orders.remove(order_id)
        self.completed_deliveries += 1
        self.total_delivery_time += delivery_time_min
        self.total_earnings += earnings
        self.is_available = True

    @property
    def workload_score(self) -> float:
        """Normalized workload score (0 = free, 1 = fully loaded)."""
        return len(self.current_orders) / 3.0

    @property
    def avg_delivery_time(self) -> Optional[float]:
        """Average delivery time across all completed orders."""
        if self.completed_deliveries == 0:
            return None
        return self.total_delivery_time / self.completed_deliveries

    @property
    def deliveries_per_hour(self) -> float:
        """Estimated deliveries per hour based on average delivery time."""
        avg = self.avg_delivery_time
        if avg is None or avg == 0:
            return 0.0
        return 60.0 / avg

    def __repr__(self):
        return (f"Rider({self.id}, {self.name}, speed={self.speed_kmph}km/h, "
                f"efficiency={self.efficiency_score:.0%}, load={self.workload_score:.0%})")
