from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

@dataclass
class Order:
    id: str
    customer_id: str
    customer_location: tuple  # (lat, lon)
    items: list  # List of item dictionaries
    order_time: datetime
    priority: str = "normal"  # normal, high, urgent
    assigned_store_id: Optional[str] = None
    assigned_rider_id: Optional[str] = None
    estimated_delivery_time: Optional[datetime] = None
    actual_delivery_time: Optional[datetime] = None
    status: str = "pending"  # pending, assigned, picked_up, delivered, cancelled
    sla_met: Optional[bool] = None
    cost: float = 0.0
    profit: float = 0.0
    decision_explanation: str = ""
    recommendations: list = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.recommendations is None:
            self.recommendations = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_location': self.customer_location,
            'items': self.items,
            'order_time': self.order_time.isoformat() if self.order_time else None,
            'priority': self.priority,
            'assigned_store_id': self.assigned_store_id,
            'assigned_rider_id': self.assigned_rider_id,
            'estimated_delivery_time': self.estimated_delivery_time.isoformat() if self.estimated_delivery_time else None,
            'actual_delivery_time': self.actual_delivery_time.isoformat() if self.actual_delivery_time else None,
            'status': self.status,
            'sla_met': self.sla_met,
            'cost': self.cost,
            'profit': self.profit,
            'decision_explanation': self.decision_explanation,
            'recommendations': self.recommendations
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Order':
        order_time = datetime.fromisoformat(data['order_time']) if data.get('order_time') else None
        estimated_delivery_time = datetime.fromisoformat(data['estimated_delivery_time']) if data.get('estimated_delivery_time') else None
        actual_delivery_time = datetime.fromisoformat(data['actual_delivery_time']) if data.get('actual_delivery_time') else None
        
        return cls(
            id=data.get('id'),
            customer_id=data['customer_id'],
            customer_location=tuple(data['customer_location']),
            items=data['items'],
            order_time=order_time,
            priority=data.get('priority', 'normal'),
            assigned_store_id=data.get('assigned_store_id'),
            assigned_rider_id=data.get('assigned_rider_id'),
            estimated_delivery_time=estimated_delivery_time,
            actual_delivery_time=actual_delivery_time,
            status=data.get('status', 'pending'),
            sla_met=data.get('sla_met'),
            cost=data.get('cost', 0.0),
            profit=data.get('profit', 0.0),
            decision_explanation=data.get('decision_explanation', ''),
            recommendations=data.get('recommendations', [])
        )
