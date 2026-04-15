import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from models.order import Order
from models.store import Store


class DemandSimulator:
    def __init__(self):
        self.demand_zones = {
            "downtown": {"center": (40.7128, -74.0060), "radius": 2.0, "base_demand": 10},
            "residential_north": {"center": (40.7589, -73.9851), "radius": 3.0, "base_demand": 5},
            "residential_south": {"center": (40.6892, -74.0445), "radius": 3.0, "base_demand": 5},
            "business_district": {"center": (40.7614, -73.9776), "radius": 1.5, "base_demand": 8},
            "university_area": {"center": (40.8075, -73.9626), "radius": 2.5, "base_demand": 6}
        }
        
        self.item_catalog = [
            {"id": "burger", "price": 8.99, "prep_time": 5},
            {"id": "pizza", "price": 12.99, "prep_time": 8},
            {"id": "sandwich", "price": 6.99, "prep_time": 3},
            {"id": "salad", "price": 7.99, "prep_time": 4},
            {"id": "pasta", "price": 10.99, "prep_time": 6},
            {"id": "sushi", "price": 15.99, "prep_time": 10},
            {"id": "coffee", "price": 3.99, "prep_time": 2},
            {"id": "smoothie", "price": 5.99, "prep_time": 3},
            {"id": "chicken", "price": 9.99, "prep_time": 7},
            {"id": "dessert", "price": 4.99, "prep_time": 2}
        ]
        
        self.customer_names = [
            "John Smith", "Emily Johnson", "Michael Brown", "Sarah Davis", "David Wilson",
            "Jessica Martinez", "Robert Anderson", "Lisa Taylor", "William Thomas", "Maria Garcia"
        ]
    
    def generate_random_location(self, zone: str) -> Tuple[float, float]:
        """Generate random location within a demand zone"""
        zone_data = self.demand_zones[zone]
        center_lat, center_lon = zone_data["center"]
        radius = zone_data["radius"]
        
        # Generate random point within radius
        angle = random.uniform(0, 2 * 3.14159)
        distance = random.uniform(0, radius)
        
        # Convert to coordinates (rough approximation)
        lat_offset = distance * 0.009  # ~1km latitude
        lon_offset = distance * 0.009 * 0.8  # longitude correction
        
        lat = center_lat + lat_offset * (1 if random.random() > 0.5 else -1)
        lon = center_lon + lon_offset * (1 if random.random() > 0.5 else -1)
        
        return (lat, lon)
    
    def generate_order_items(self) -> List[Dict]:
        """Generate random order items"""
        num_items = random.choices([1, 2, 3, 4], weights=[40, 35, 20, 5])[0]
        items = []
        
        for _ in range(num_items):
            item = random.choice(self.item_catalog).copy()
            item["quantity"] = random.choices([1, 2, 3], weights=[70, 25, 5])[0]
            items.append(item)
        
        return items
    
    def generate_order(self, zone: str = None, priority: str = None) -> Order:
        """Generate a random order"""
        if zone is None:
            zone = random.choice(list(self.demand_zones.keys()))
        
        if priority is None:
            priority = random.choices(["normal", "high", "urgent"], weights=[70, 20, 10])[0]
        
        location = self.generate_random_location(zone)
        items = self.generate_order_items()
        customer_name = random.choice(self.customer_names)
        
        order = Order(
            id=None,
            customer_id=f"customer_{random.randint(1000, 9999)}",
            customer_location=location,
            items=items,
            order_time=datetime.now(),
            priority=priority
        )
        
        return order
    
    def simulate_demand_surge(self, zone: str, multiplier: float, duration_minutes: int = 30) -> List[Order]:
        """Simulate demand surge in a specific zone"""
        orders = []
        base_demand = self.demand_zones[zone]["base_demand"]
        surge_demand = int(base_demand * multiplier)
        
        for _ in range(surge_demand):
            order = self.generate_order(zone=zone)
            # Add some randomness to order time during surge
            order.order_time = datetime.now() + timedelta(minutes=random.randint(0, duration_minutes))
            orders.append(order)
        
        return orders
    
    def get_demand_heatmap(self) -> Dict[str, Dict]:
        """Get current demand heatmap data"""
        heatmap = {}
        
        for zone_name, zone_data in self.demand_zones.items():
            # Simulate current demand based on time of day
            current_hour = datetime.now().hour
            
            # Peak hours adjustment
            if 11 <= current_hour <= 14:  # Lunch peak
                demand_multiplier = 1.5
            elif 18 <= current_hour <= 21:  # Dinner peak
                demand_multiplier = 1.8
            elif 22 <= current_hour or current_hour <= 6:  # Late night/early morning
                demand_multiplier = 0.3
            else:
                demand_multiplier = 1.0
            
            current_demand = zone_data["base_demand"] * demand_multiplier
            
            heatmap[zone_name] = {
                "center": zone_data["center"],
                "radius": zone_data["radius"],
                "current_demand": current_demand,
                "base_demand": zone_data["base_demand"],
                "demand_multiplier": demand_multiplier
            }
        
        return heatmap
    
    def predict_demand(self, zone: str, hours_ahead: int = 1) -> Dict:
        """Predict demand for a zone in the next few hours"""
        current_hour = datetime.now().hour
        future_hour = (current_hour + hours_ahead) % 24
        
        # Simple demand prediction based on hour patterns
        if 11 <= future_hour <= 14:  # Lunch
            predicted_multiplier = 1.5
        elif 18 <= future_hour <= 21:  # Dinner
            predicted_multiplier = 1.8
        elif 22 <= future_hour or future_hour <= 6:  # Late night
            predicted_multiplier = 0.3
        else:
            predicted_multiplier = 1.0
        
        base_demand = self.demand_zones[zone]["base_demand"]
        predicted_demand = base_demand * predicted_multiplier
        
        return {
            "zone": zone,
            "hours_ahead": hours_ahead,
            "predicted_demand": predicted_demand,
            "predicted_multiplier": predicted_multiplier,
            "confidence": 0.75  # Mock confidence score
        }
    
    def what_if_simulation(self, scenario: Dict) -> Dict:
        """Run what-if simulation for different scenarios"""
        scenario_type = scenario.get("type", "demand_surge")
        results = {}
        
        if scenario_type == "demand_surge":
            zone = scenario.get("zone", "downtown")
            multiplier = scenario.get("multiplier", 2.0)
            duration = scenario.get("duration_minutes", 30)
            
            orders = self.simulate_demand_surge(zone, multiplier, duration)
            
            results = {
                "scenario_type": scenario_type,
                "zone": zone,
                "multiplier": multiplier,
                "duration_minutes": duration,
                "generated_orders": len(orders),
                "orders": [order.to_dict() for order in orders],
                "impact_assessment": {
                    "additional_load": len(orders),
                    "peak_orders_per_minute": len(orders) / duration,
                    "recommended_actions": [
                        f"Add {len(orders) // 5} additional riders to {zone}",
                        "Increase store preparation capacity",
                        "Consider dynamic pricing for surge periods"
                    ]
                }
            }
        
        elif scenario_type == "rider_shortage":
            shortage_percentage = scenario.get("shortage_percentage", 30)
            
            results = {
                "scenario_type": scenario_type,
                "shortage_percentage": shortage_percentage,
                "impact_assessment": {
                    "delivery_time_increase": f"{shortage_percentage * 0.2:.1f} minutes",
                    "sla_risk_increase": f"{shortage_percentage * 0.5:.1f}%",
                    "recommended_actions": [
                        "Activate backup rider pool",
                        "Offer overtime incentives",
                        "Temporarily increase delivery radius for remaining riders"
                    ]
                }
            }
        
        elif scenario_type == "store_closure":
            store_id = scenario.get("store_id")
            affected_zones = scenario.get("affected_zones", ["downtown"])
            
            results = {
                "scenario_type": scenario_type,
                "store_id": store_id,
                "affected_zones": affected_zones,
                "impact_assessment": {
                    "orders_redirected": "Estimated 15-20 orders per hour",
                    "additional_distance": "2-3km average increase",
                    "sla_risk_increase": "25-30%",
                    "recommended_actions": [
                        "Redirect orders to nearest available stores",
                        "Increase rider incentives for longer distances",
                        "Communicate delays to customers proactively"
                    ]
                }
            }
        
        return results
