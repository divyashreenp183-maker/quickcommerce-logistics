"""
Rider assigner for the NeuralOps Logistics System.
Feature 2: Smart delivery partner assignment based on distance to store,
           efficiency score, and current workload.
"""
from typing import List, Optional, Dict, Tuple
from models.order import Order
from models.rider import Rider
from models.store import DarkStore
from engine.distance import haversine, estimate_travel_time


# Scoring weights for rider selection (must sum to 1.0)
WEIGHT_DISTANCE_TO_STORE = 0.50  # Proximity to the selected store
WEIGHT_EFFICIENCY = 0.30         # Rider's historical efficiency
WEIGHT_WORKLOAD = 0.20           # Current active orders


class RiderAssigner:
    """
    Assigns the optimal delivery rider for an order using a weighted scoring model.

    Score = w_dist * norm_dist + w_eff * (1 - efficiency) + w_load * workload
    Lower score = better rider.
    """

    def assign(
        self,
        order: Order,
        store: DarkStore,
        riders: List[Rider]
    ) -> Tuple[Optional[Rider], Dict]:
        """
        Assign the best available rider for an order from a given store.

        Returns:
            (best_rider, decision_metadata_dict)
        """
        # Filter only available riders
        available = [r for r in riders if r.is_available]

        if not available:
            return None, {"reason": "No riders available"}

        candidates = []

        for rider in available:
            distance_to_store_km = haversine(rider.location, store.location)
            pickup_time_min = estimate_travel_time(distance_to_store_km, rider.speed_kmph)

            # Normalize distance (assume >5km is max penalty)
            distance_penalty = min(distance_to_store_km / 5.0, 1.0)

            # Lower score = better
            score = (
                WEIGHT_DISTANCE_TO_STORE * distance_penalty
                + WEIGHT_EFFICIENCY * (1.0 - rider.efficiency_score)
                + WEIGHT_WORKLOAD * rider.workload_score
            )

            candidates.append({
                "rider": rider,
                "score": score,
                "distance_to_store_km": round(distance_to_store_km, 3),
                "pickup_time_min": round(pickup_time_min, 2),
                "efficiency_score": rider.efficiency_score,
                "workload_score": round(rider.workload_score, 3),
            })

        # Sort by score ascending
        candidates.sort(key=lambda x: x["score"])
        best = candidates[0]

        metadata = {
            "selected_rider_id": best["rider"].id,
            "selected_rider_name": best["rider"].name,
            "distance_to_store_km": best["distance_to_store_km"],
            "pickup_time_min": best["pickup_time_min"],
            "efficiency_score": best["efficiency_score"],
            "workload_score": best["workload_score"],
            "composite_score": round(best["score"], 4),
            "all_candidates": [
                {
                    "id": c["rider"].id,
                    "name": c["rider"].name,
                    "distance_to_store_km": c["distance_to_store_km"],
                    "pickup_time_min": c["pickup_time_min"],
                    "efficiency_score": c["efficiency_score"],
                    "workload_score": c["workload_score"],
                    "score": round(c["score"], 4),
                }
                for c in candidates
            ],
        }

        return best["rider"], metadata
