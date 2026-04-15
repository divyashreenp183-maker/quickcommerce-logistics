from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid

@dataclass
class Rider:
    id: str
    name: str
    current_location: tuple  # (lat, lon)
    phone: str
    vehicle_type: str = "bike"  # bike, scooter, car
    efficiency_score: float = 1.0  # 0.5 to 1.5, higher is better
    is_available: bool = True
    current_order_id: Optional[str] = None
    completed_deliveries: int = 0
    average_delivery_time: float = 8.0  # minutes
    rating: float = 4.5
    shift_start: datetime = None
    shift_end: datetime = None
    workload_score: float = 0.0  # 0 to 1, higher means more loaded
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.shift_start is None:
            self.shift_start = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
        if self.shift_end is None:
            self.shift_end = datetime.now().replace(hour=20, minute=0, second=0, microsecond=0)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'current_location': self.current_location,
            'phone': self.phone,
            'vehicle_type': self.vehicle_type,
            'efficiency_score': self.efficiency_score,
            'is_available': self.is_available,
            'current_order_id': self.current_order_id,
            'completed_deliveries': self.completed_deliveries,
            'average_delivery_time': self.average_delivery_time,
            'rating': self.rating,
            'shift_start': self.shift_start.isoformat() if self.shift_start else None,
            'shift_end': self.shift_end.isoformat() if self.shift_end else None,
            'workload_score': self.workload_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Rider':
        shift_start = datetime.fromisoformat(data['shift_start']) if data.get('shift_start') else None
        shift_end = datetime.fromisoformat(data['shift_end']) if data.get('shift_end') else None
        
        return cls(
            id=data.get('id'),
            name=data['name'],
            current_location=tuple(data['current_location']),
            phone=data['phone'],
            vehicle_type=data.get('vehicle_type', 'bike'),
            efficiency_score=data.get('efficiency_score', 1.0),
            is_available=data.get('is_available', True),
            current_order_id=data.get('current_order_id'),
            completed_deliveries=data.get('completed_deliveries', 0),
            average_delivery_time=data.get('average_delivery_time', 8.0),
            rating=data.get('rating', 4.5),
            shift_start=shift_start,
            shift_end=shift_end,
            workload_score=data.get('workload_score', 0.0)
        )
    
    def assign_order(self, order_id: str):
        self.current_order_id = order_id
        self.is_available = False
        self.workload_score = min(1.0, self.workload_score + 0.2)
    
    def complete_order(self):
        if self.current_order_id:
            self.completed_deliveries += 1
            self.current_order_id = None
            self.is_available = True
            self.workload_score = max(0.0, self.workload_score - 0.2)
    
    def update_location(self, new_location: tuple):
        self.current_location = new_location
    
    def calculate_delivery_score(self, distance_km: float, order_priority: str) -> float:
        base_score = self.efficiency_score * self.rating
        
        # Distance penalty (closer is better)
        distance_penalty = max(0, 1 - (distance_km / 5.0))  # 5km as reference
        
        # Availability bonus
        availability_bonus = 1.0 if self.is_available else 0.0
        
        # Workload penalty
        workload_penalty = 1.0 - self.workload_score
        
        # Priority bonus
        priority_bonus = 1.2 if order_priority == "urgent" else 1.1 if order_priority == "high" else 1.0
        
        # Vehicle speed factor
        vehicle_factor = {"bike": 1.0, "scooter": 1.1, "car": 0.9}.get(self.vehicle_type, 1.0)
        
        return base_score * distance_penalty * availability_bonus * workload_penalty * priority_bonus * vehicle_factor
