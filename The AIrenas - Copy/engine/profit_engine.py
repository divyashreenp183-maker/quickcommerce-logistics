"""
Profit Engine for the NeuralOps Logistics System.
Features 5-7: Calculate delivery costs, compute per-order profit,
              and track aggregate efficiency metrics.
"""
from dataclasses import dataclass
from typing import List, Dict
from models.order import Order
from models.rider import Rider


# Cost model constants (INR)
BASE_DELIVERY_COST = 15.0        # Fixed platform cost per delivery
COST_PER_KM = 4.5               # Fuel + wear per kilometer
COST_PER_MINUTE = 0.80          # Rider time cost per minute
PLATFORM_COMMISSION_RATE = 0.10  # 10% commission on order revenue


@dataclass
class ProfitResult:
    """Profit breakdown for a single order."""
    order_id: str
    order_revenue: float
    base_cost: float
    distance_cost: float
    time_cost: float
    platform_commission: float
    total_delivery_cost: float
    profit: float
    margin_pct: float


class ProfitEngine:
    """
    Calculates per-order profitability and tracks cumulative system metrics.
    """

    def __init__(self):
        self._results: List[ProfitResult] = []

    def calculate(
        self,
        order: Order,
        total_km: float,
        total_min: float,
    ) -> ProfitResult:
        """
        Calculate the cost and profit for a single order.

        Args:
            order: The order being processed
            total_km: Total delivery distance (rider→store + store→customer)
            total_min: Total delivery time in minutes

        Returns:
            ProfitResult with full cost breakdown
        """
        base_cost = BASE_DELIVERY_COST
        distance_cost = total_km * COST_PER_KM
        time_cost = total_min * COST_PER_MINUTE
        platform_commission = order.revenue * PLATFORM_COMMISSION_RATE
        total_cost = base_cost + distance_cost + time_cost + platform_commission

        profit = order.revenue - total_cost
        margin_pct = (profit / order.revenue * 100) if order.revenue > 0 else 0.0

        result = ProfitResult(
            order_id=order.id,
            order_revenue=order.revenue,
            base_cost=round(base_cost, 2),
            distance_cost=round(distance_cost, 2),
            time_cost=round(time_cost, 2),
            platform_commission=round(platform_commission, 2),
            total_delivery_cost=round(total_cost, 2),
            profit=round(profit, 2),
            margin_pct=round(margin_pct, 1),
        )

        self._results.append(result)
        return result

    # ---------- Aggregate Statistics ----------

    @property
    def total_revenue(self) -> float:
        return round(sum(r.order_revenue for r in self._results), 2)

    @property
    def total_cost(self) -> float:
        return round(sum(r.total_delivery_cost for r in self._results), 2)

    @property
    def total_profit(self) -> float:
        return round(sum(r.profit for r in self._results), 2)

    @property
    def avg_profit_per_order(self) -> float:
        if not self._results:
            return 0.0
        return round(self.total_profit / len(self._results), 2)

    @property
    def profitable_orders(self) -> int:
        return sum(1 for r in self._results if r.profit > 0)

    @property
    def loss_orders(self) -> int:
        return sum(1 for r in self._results if r.profit <= 0)

    def get_summary(self) -> Dict:
        return {
            "total_orders_processed": len(self._results),
            "total_revenue_inr": self.total_revenue,
            "total_cost_inr": self.total_cost,
            "total_profit_inr": self.total_profit,
            "avg_profit_per_order_inr": self.avg_profit_per_order,
            "profitable_orders": self.profitable_orders,
            "loss_orders": self.loss_orders,
        }

    def get_per_order_data(self) -> List[Dict]:
        """Return all per-order profit data for chart rendering."""
        return [
            {
                "order_id": r.order_id,
                "revenue": r.order_revenue,
                "cost": r.total_delivery_cost,
                "profit": r.profit,
                "margin_pct": r.margin_pct,
            }
            for r in self._results
        ]

    def to_dict(self, result: ProfitResult) -> Dict:
        return {
            "order_revenue": result.order_revenue,
            "base_cost": result.base_cost,
            "distance_cost": result.distance_cost,
            "time_cost": result.time_cost,
            "platform_commission": result.platform_commission,
            "total_delivery_cost": result.total_delivery_cost,
            "profit": result.profit,
            "margin_pct": result.margin_pct,
        }
