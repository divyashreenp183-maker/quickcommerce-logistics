"""
Predictive Demand Zone Analyzer for the NeuralOps Logistics System.
Feature 10: Simulates demand heatmaps and suggests optimal rider pre-positioning.
"""
import math
from typing import List, Dict, Tuple
from collections import defaultdict
from models.order import Order
from models.rider import Rider
from engine.distance import haversine


# Clustering radius: orders within this distance (km) form a demand zone
CLUSTER_RADIUS_KM = 1.5

# Minimum orders to qualify as a hot zone
HOT_ZONE_THRESHOLD = 2


class DemandPredictor:
    """
    Analyzes historical order locations to identify demand hot zones.
    Suggests pre-positioning riders near those zones to reduce response time.
    """

    def analyze(
        self,
        orders: List[Order],
        riders: List[Rider],
    ) -> Dict:
        """
        Cluster orders by geographic proximity and identify hot zones.

        Returns dict with zones and positioning recommendations.
        """
        if not orders:
            return {"zones": [], "recommendations": ["No historical orders to analyze."]}

        # Simple greedy clustering: assign each order to the nearest existing cluster center
        cluster_centers: List[Tuple[float, float]] = []
        cluster_counts: List[int] = []
        cluster_labels: List[int] = []

        for order in orders:
            loc = order.location
            assigned = False

            for i, center in enumerate(cluster_centers):
                if haversine(loc, center) <= CLUSTER_RADIUS_KM:
                    # Update cluster center as weighted mean
                    n = cluster_counts[i]
                    new_lat = (center[0] * n + loc[0]) / (n + 1)
                    new_lon = (center[1] * n + loc[1]) / (n + 1)
                    cluster_centers[i] = (new_lat, new_lon)
                    cluster_counts[i] += 1
                    cluster_labels.append(i)
                    assigned = True
                    break

            if not assigned:
                cluster_centers.append(loc)
                cluster_counts.append(1)
                cluster_labels.append(len(cluster_centers) - 1)

        # Build zone list
        zones = []
        for i, (center, count) in enumerate(zip(cluster_centers, cluster_counts)):
            is_hot = count >= HOT_ZONE_THRESHOLD
            zones.append({
                "zone_id": f"Z{i+1}",
                "center_lat": round(center[0], 5),
                "center_lon": round(center[1], 5),
                "order_count": count,
                "is_hot_zone": is_hot,
                "intensity": "🔴 HIGH" if count >= 4 else ("🟡 MEDIUM" if is_hot else "🟢 LOW"),
            })

        # Sort by order count descending
        zones.sort(key=lambda z: z["order_count"], reverse=True)

        # Pre-positioning recommendations
        recommendations = self._build_recommendations(zones, riders)

        return {
            "total_orders_analyzed": len(orders),
            "total_zones_identified": len(zones),
            "hot_zones": sum(1 for z in zones if z["is_hot_zone"]),
            "zones": zones,
            "recommendations": recommendations,
        }

    def _build_recommendations(
        self,
        zones: List[Dict],
        riders: List[Rider],
    ) -> List[str]:
        """Generate rider pre-positioning recommendations."""
        hot_zones = [z for z in zones if z["is_hot_zone"]]
        if not hot_zones:
            return ["📍 No hot zones detected — maintain current rider distribution."]

        recs = []
        available_riders = [r for r in riders if r.is_available]
        n_available = len(available_riders)

        for i, zone in enumerate(hot_zones[:3]):  # Top 3 zones
            lat, lon = zone["center_lat"], zone["center_lon"]
            order_count = zone["order_count"]
            intensity = zone["intensity"]

            # Find riders nearest to this zone
            if available_riders:
                nearest = min(
                    available_riders,
                    key=lambda r: haversine(r.location, (lat, lon))
                )
                dist = haversine(nearest.location, (lat, lon))
                recs.append(
                    f"📍 Pre-position {nearest.name} ({nearest.id}) near Zone {zone['zone_id']} "
                    f"({lat:.4f}, {lon:.4f}) — {intensity} demand area "
                    f"({order_count} orders). Currently {dist:.2f} km away."
                )
                available_riders = [r for r in available_riders if r.id != nearest.id]

        if n_available < len(hot_zones):
            recs.append(
                f"⚡ {len(hot_zones)} hot zones detected but only {n_available} available "
                f"riders — consider dispatching additional riders."
            )

        return recs
