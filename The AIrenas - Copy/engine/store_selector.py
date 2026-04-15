"""
Dark Store selector for the NeuralOps Logistics System.
Feature 1: Select the best dark store for an order based on distance,
           product availability, and current workload.
"""
from typing import List, Optional, Dict, Tuple
from models.order import Order
from models.store import DarkStore
from engine.distance import haversine


# Scoring weights (must sum to 1.0)
WEIGHT_DISTANCE = 0.50       # How far the store is from the customer
WEIGHT_AVAILABILITY = 0.30   # Whether the store has the required items
WEIGHT_LOAD = 0.20           # Current store workload (lower = better)


class StoreSelector:
    """
    Selects the optimal dark store for a given order using a weighted scoring model.

    Score = w_dist * norm_dist_penalty + w_avail * (1 - avail_score) + w_load * load_factor
    Lower score = better store.
    """

    def select(
        self,
        order: Order,
        stores: List[DarkStore]
    ) -> Tuple[Optional[DarkStore], Dict]:
        """
        Select the best store for an order.

        Returns:
            (best_store, decision_metadata_dict)
        """
        if not stores:
            return None, {"reason": "No stores available"}

        candidates = []
        scores = []

        for store in stores:
            avail_score = store.get_availability_score(order.items)
            distance_km = haversine(store.location, order.location)
            load_factor = store.load_factor

            # Penalize stores over 3km (beyond which 10-min SLA gets very hard)
            distance_penalty = min(distance_km / 5.0, 1.0)

            # Lower score = better
            score = (
                WEIGHT_DISTANCE * distance_penalty
                + WEIGHT_AVAILABILITY * (1.0 - avail_score)
                + WEIGHT_LOAD * load_factor
            )

            candidates.append({
                "store": store,
                "score": score,
                "distance_km": round(distance_km, 3),
                "avail_score": round(avail_score, 3),
                "load_factor": round(load_factor, 3),
            })
            scores.append(score)

        # Sort by score ascending (lowest = best)
        candidates.sort(key=lambda x: x["score"])
        best = candidates[0]

        # Build decision metadata
        metadata = {
            "selected_store_id": best["store"].id,
            "selected_store_name": best["store"].name,
            "distance_km": best["distance_km"],
            "availability_score": best["avail_score"],
            "load_factor": best["load_factor"],
            "composite_score": round(best["score"], 4),
            "all_candidates": [
                {
                    "id": c["store"].id,
                    "name": c["store"].name,
                    "distance_km": c["distance_km"],
                    "avail_score": c["avail_score"],
                    "load_factor": c["load_factor"],
                    "score": round(c["score"], 4),
                }
                for c in candidates
            ],
        }

        return best["store"], metadata
