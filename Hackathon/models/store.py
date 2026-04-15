from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List
import uuid

@dataclass
class Store:
    id: str
    name: str
    location: tuple  # (lat, lon)
    inventory: Dict[str, int]  # item_id -> quantity
    capacity: int = 1000  # total inventory capacity
    current_workload: int = 0  # number of active orders
    max_concurrent_orders: int = 20
    preparation_time_avg: float = 3.0  # minutes
    operating_hours: tuple = (8, 20)  # (start_hour, end_hour)
    zone: str = "default"  # demand zone
    efficiency_score: float = 1.0  # 0.5 to 1.5
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'inventory': self.inventory,
            'capacity': self.capacity,
            'current_workload': self.current_workload,
            'max_concurrent_orders': self.max_concurrent_orders,
            'preparation_time_avg': self.preparation_time_avg,
            'operating_hours': self.operating_hours,
            'zone': self.zone,
            'efficiency_score': self.efficiency_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Store':
        return cls(
            id=data.get('id'),
            name=data['name'],
            location=tuple(data['location']),
            inventory=data['inventory'],
            capacity=data.get('capacity', 1000),
            current_workload=data.get('current_workload', 0),
            max_concurrent_orders=data.get('max_concurrent_orders', 20),
            preparation_time_avg=data.get('preparation_time_avg', 3.0),
            operating_hours=tuple(data.get('operating_hours', (8, 20))),
            zone=data.get('zone', 'default'),
            efficiency_score=data.get('efficiency_score', 1.0)
        )
    
    def is_open(self) -> bool:
        current_hour = datetime.now().hour
        return self.operating_hours[0] <= current_hour < self.operating_hours[1]
    
    def can_accept_order(self, items: List[Dict]) -> bool:
        if not self.is_open():
            return False
        
        if self.current_workload >= self.max_concurrent_orders:
            return False
        
        # Check inventory
        for item in items:
            item_id = item.get('id')
            quantity = item.get('quantity', 1)
            if self.inventory.get(item_id, 0) < quantity:
                return False
        
        return True
    
    def reserve_inventory(self, items: List[Dict]):
        for item in items:
            item_id = item.get('id')
            quantity = item.get('quantity', 1)
            if item_id in self.inventory:
                self.inventory[item_id] -= quantity
    
    def release_inventory(self, items: List[Dict]):
        for item in items:
            item_id = item.get('id')
            quantity = item.get('quantity', 1)
            if item_id in self.inventory:
                self.inventory[item_id] += quantity
    
    def add_order(self):
        self.current_workload += 1
    
    def complete_order(self):
        self.current_workload = max(0, self.current_workload - 1)
    
    def calculate_workload_score(self) -> float:
        return self.current_workload / self.max_concurrent_orders
    
    def calculate_preparation_time(self, items: List[Dict]) -> float:
        base_time = self.preparation_time_avg
        item_count = len(items)
        
        # More items = more preparation time
        item_factor = 1 + (item_count - 1) * 0.2
        
        # Workload affects preparation time
        workload_factor = 1 + self.calculate_workload_score() * 0.5
        
        # Store efficiency
        efficiency_factor = 1 / self.efficiency_score
        
        return base_time * item_factor * workload_factor * efficiency_factor
    
    def calculate_store_score(self, distance_km: float, items: List[Dict]) -> float:
        # Base score
        base_score = self.efficiency_score
        
        # Distance penalty (closer is better)
        distance_penalty = max(0, 1 - (distance_km / 5.0))
        
        # Inventory availability score
        inventory_score = 1.0
        for item in items:
            item_id = item.get('id')
            quantity = item.get('quantity', 1)
            available = self.inventory.get(item_id, 0)
            if available < quantity:
                inventory_score = 0.0
                break
            elif available < quantity * 2:  # Low inventory warning
                inventory_score *= 0.8
        
        # Workload penalty
        workload_penalty = 1 - self.calculate_workload_score()
        
        # Operating hours bonus
        hours_bonus = 1.0 if self.is_open() else 0.0
        
        return base_score * distance_penalty * inventory_score * workload_penalty * hours_bonus
