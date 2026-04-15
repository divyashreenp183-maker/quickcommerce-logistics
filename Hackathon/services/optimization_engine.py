import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from models.order import Order
from models.rider import Rider
from models.store import Store


class OptimizationEngine:
    def __init__(self):
        self.SLA_MINUTES = 10
        self.AVERAGE_SPEED_KMH = 30  # Average delivery speed in city
        self.PICKUP_TIME_MINUTES = 2  # Time for rider to pickup order
    
    def calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate Haversine distance between two points in kilometers"""
        lat1, lon1 = point1
        lat2, lon2 = point2
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        return 6371 * c
    
    def estimate_delivery_time(self, 
                             customer_location: Tuple[float, float],
                             store_location: Tuple[float, float],
                             rider_location: Tuple[float, float],
                             preparation_time: float,
                             rider_efficiency: float = 1.0) -> datetime:
        """Calculate estimated delivery time"""
        
        # Time for rider to reach store
        rider_to_store_distance = self.calculate_distance(rider_location, store_location)
        rider_to_store_time = (rider_to_store_distance / self.AVERAGE_SPEED_KMH) * 60 / rider_efficiency
        
        # Time for store to customer
        store_to_customer_distance = self.calculate_distance(store_location, customer_location)
        store_to_customer_time = (store_to_customer_distance / self.AVERAGE_SPEED_KMH) * 60 / rider_efficiency
        
        # Total time
        total_time = rider_to_store_time + self.PICKUP_TIME_MINUTES + preparation_time + store_to_customer_time
        
        return datetime.now() + timedelta(minutes=total_time)
    
    def select_best_store(self, 
                         customer_location: Tuple[float, float],
                         items: List[Dict],
                         stores: List[Store]) -> Tuple[Optional[Store], str]:
        """Select best store based on distance, inventory, and workload"""
        
        best_store = None
        best_score = -1
        explanation = []
        
        for store in stores:
            if not store.can_accept_order(items):
                explanation.append(f"Store {store.name} rejected: Cannot accept order (closed, full capacity, or insufficient inventory)")
                continue
            
            distance = self.calculate_distance(customer_location, store.location)
            score = store.calculate_store_score(distance, items)
            
            explanation.append(f"Store {store.name}: Distance {distance:.2f}km, Score {score:.2f}, Workload {store.current_workload}/{store.max_concurrent_orders}")
            
            if score > best_score:
                best_score = score
                best_store = store
        
        if best_store:
            explanation.append(f"Selected store {best_store.name} with highest score: {best_score:.2f}")
            return best_store, "\n".join(explanation)
        else:
            return None, "\n".join(explanation) + "\nNo suitable store found"
    
    def assign_best_rider(self,
                          order: Order,
                          store: Store,
                          riders: List[Rider]) -> Tuple[Optional[Rider], str]:
        """Assign best rider using greedy scoring algorithm"""
        
        best_rider = None
        best_score = -1
        explanation = []
        
        for rider in riders:
            if not rider.is_available:
                explanation.append(f"Rider {rider.name} unavailable: Currently on order {rider.current_order_id}")
                continue
            
            # Calculate distance from rider to store
            distance = self.calculate_distance(rider.current_location, store.location)
            
            # Calculate estimated delivery time
            estimated_time = self.estimate_delivery_time(
                order.customer_location,
                store.location,
                rider.current_location,
                store.calculate_preparation_time(order.items),
                rider.efficiency_score
            )
            
            # Check if within SLA
            time_to_delivery = (estimated_time - datetime.now()).total_seconds() / 60
            if time_to_delivery > self.SLA_MINUTES:
                explanation.append(f"Rider {rider.name} rejected: Estimated delivery time {time_to_delivery:.1f}min exceeds SLA")
                continue
            
            # Calculate rider score
            score = rider.calculate_delivery_score(distance, order.priority)
            
            explanation.append(f"Rider {rider.name}: Distance {distance:.2f}km, Score {score:.2f}, ETA {time_to_delivery:.1f}min")
            
            if score > best_score:
                best_score = score
                best_rider = rider
        
        if best_rider:
            explanation.append(f"Selected rider {best_rider.name} with highest score: {best_score:.2f}")
            return best_rider, "\n".join(explanation)
        else:
            return None, "\n".join(explanation) + "\nNo suitable rider available within SLA"
    
    def check_sla_risk(self, order: Order, store: Store, rider: Rider) -> Dict:
        """Check SLA risk and provide recommendations"""
        
        # Calculate current estimated delivery time
        estimated_time = self.estimate_delivery_time(
            order.customer_location,
            store.location,
            rider.current_location,
            store.calculate_preparation_time(order.items),
            rider.efficiency_score
        )
        
        time_to_delivery = (estimated_time - datetime.now()).total_seconds() / 60
        risk_level = "low"
        recommendations = []
        
        if time_to_delivery > self.SLA_MINUTES:
            risk_level = "critical"
            recommendations.append("Order exceeds SLA - consider reassignment to closer store/rider")
            recommendations.append("Offer customer delivery time extension or cancellation option")
        elif time_to_delivery > self.SLA_MINUTES * 0.8:
            risk_level = "high"
            recommendations.append("Close to SLA limit - monitor rider progress closely")
            recommendations.append("Prepare backup rider if needed")
        elif time_to_delivery > self.SLA_MINUTES * 0.6:
            risk_level = "medium"
            recommendations.append("Moderate SLA risk - ensure efficient route")
        
        # Check store workload
        if store.current_workload >= store.max_concurrent_orders * 0.8:
            recommendations.append("Store workload high - consider diverting future orders")
        
        # Check rider efficiency
        if rider.efficiency_score < 0.8:
            recommendations.append("Rider efficiency below optimal - consider training or reassignment")
        
        return {
            'risk_level': risk_level,
            'estimated_time_minutes': time_to_delivery,
            'sla_buffer': self.SLA_MINUTES - time_to_delivery,
            'recommendations': recommendations
        }
    
    def calculate_order_profit(self, order: Order, store: Store, rider: Rider) -> Dict:
        """Calculate profit for the order"""
        
        # Base revenue (could be item-based)
        base_revenue = sum(item.get('price', 10) * item.get('quantity', 1) for item in order.items)
        
        # Delivery fee
        delivery_fee = 5.0
        
        # Distance-based cost
        distance = self.calculate_distance(store.location, order.customer_location)
        distance_cost = distance * 2.0  # $2 per km
        
        # Rider cost
        rider_cost = 3.0 + (distance * 1.5)  # Base + per km
        
        # Store preparation cost
        prep_cost = len(order.items) * 0.5
        
        # Total cost
        total_cost = distance_cost + rider_cost + prep_cost
        
        # Total revenue
        total_revenue = base_revenue + delivery_fee
        
        # Profit
        profit = total_revenue - total_cost
        
        return {
            'revenue': total_revenue,
            'cost': total_cost,
            'profit': profit,
            'profit_margin': (profit / total_revenue * 100) if total_revenue > 0 else 0,
            'breakdown': {
                'base_revenue': base_revenue,
                'delivery_fee': delivery_fee,
                'distance_cost': distance_cost,
                'rider_cost': rider_cost,
                'prep_cost': prep_cost
            }
        }
    
    def optimize_route(self, waypoints: List[Tuple[float, float]]) -> List[int]:
        """Simple route optimization using nearest neighbor algorithm"""
        
        if len(waypoints) <= 2:
            return list(range(len(waypoints)))
        
        unvisited = set(range(1, len(waypoints)))  # Start from first point
        route = [0]
        current = 0
        
        while unvisited:
            nearest = min(unvisited, 
                         key=lambda i: self.calculate_distance(waypoints[current], waypoints[i]))
            route.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        return route
