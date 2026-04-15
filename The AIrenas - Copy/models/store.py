"""
Dark Store model for the NeuralOps Logistics System.
Represents a quick-commerce fulfillment hub with inventory and capacity management.
"""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DarkStore:
    """Represents a dark store / micro-fulfillment center."""
    id: str
    name: str
    location: tuple          # (latitude, longitude)
    inventory: Dict[str, int]  # {item_name: stock_count}
    capacity: int = 50       # Max simultaneous orders being fulfilled

    # Runtime state
    current_load: int = field(default=0, init=False)
    fulfilled_orders: int = field(default=0, init=False)

    def check_availability(self, items: Dict[str, int]) -> bool:
        """Check if all requested items are available in sufficient quantity."""
        for item, qty in items.items():
            if self.inventory.get(item, 0) < qty:
                return False
        return True

    def get_availability_score(self, items: Dict[str, int]) -> float:
        """
        Returns 0.0 – 1.0 based on how well this store can fulfil the order.
        1.0 = all items fully available, 0.0 = none available.
        """
        if not items:
            return 1.0
        total_items = sum(items.values())
        available_items = sum(
            min(self.inventory.get(item, 0), qty)
            for item, qty in items.items()
        )
        return available_items / total_items if total_items > 0 else 1.0

    @property
    def load_factor(self) -> float:
        """Normalized load factor (0 = idle, 1 = at full capacity)."""
        return self.current_load / self.capacity if self.capacity > 0 else 1.0

    def accept_order(self):
        """Increment store load when assigned an order."""
        self.current_load += 1

    def complete_order(self):
        """Decrement store load when order shipped out."""
        if self.current_load > 0:
            self.current_load -= 1
        self.fulfilled_orders += 1

    def __repr__(self):
        return (f"DarkStore({self.id}, '{self.name}', load={self.load_factor:.0%}, "
                f"fulfilled={self.fulfilled_orders})")
