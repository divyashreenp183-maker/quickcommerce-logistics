"""
Order model for the NeuralOps Logistics System.
Represents a customer order with location, items, priority, and lifecycle status.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional


class Priority(Enum):
    HIGH = "HIGH"
    NORMAL = "NORMAL"


class OrderStatus(Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    HEALED = "HEALED"   # Self-healed after SLA breach


@dataclass
class Order:
    """Represents a customer order in the quick-commerce system."""
    id: str
    location: tuple          # (latitude, longitude)
    items: Dict[str, int]    # {item_name: quantity}
    timestamp: datetime
    priority: Priority = Priority.NORMAL
    revenue: float = 150.0   # Revenue in INR

    # Lifecycle fields (populated after processing)
    status: OrderStatus = field(default=OrderStatus.PENDING, init=False)
    assigned_store_id: Optional[str] = field(default=None, init=False)
    assigned_rider_id: Optional[str] = field(default=None, init=False)
    estimated_delivery_min: Optional[float] = field(default=None, init=False)
    actual_delivery_min: Optional[float] = field(default=None, init=False)
    sla_met: Optional[bool] = field(default=None, init=False)
    profit: Optional[float] = field(default=None, init=False)
    delivery_cost: Optional[float] = field(default=None, init=False)
    decision_log: Dict = field(default_factory=dict, init=False)

    # SLA threshold
    @property
    def sla_threshold_min(self) -> float:
        """HIGH priority orders have stricter 8-min SLA."""
        return 8.0 if self.priority == Priority.HIGH else 10.0

    def __repr__(self):
        return (f"Order({self.id}, priority={self.priority.value}, "
                f"status={self.status.value}, revenue=₹{self.revenue})")
