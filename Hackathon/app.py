from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import uuid
from typing import Dict, List, Any

from models.order import Order
from models.rider import Rider
from models.store import Store
from services.optimization_engine import OptimizationEngine
from services.demand_simulator import DemandSimulator

app = Flask(__name__)
CORS(app)

# Initialize services
optimization_engine = OptimizationEngine()
demand_simulator = DemandSimulator()

# In-memory storage (in production, use a proper database)
orders: Dict[str, Order] = {}
riders: Dict[str, Rider] = {}
stores: Dict[str, Store] = {}

def initialize_sample_data():
    """Initialize sample data for demonstration"""
    
    # Sample stores
    stores_data = [
        {
            "id": "store_1",
            "name": "Downtown Dark Store",
            "location": (40.7128, -74.0060),
            "inventory": {
                "burger": 50, "pizza": 30, "sandwich": 40, "salad": 35,
                "pasta": 25, "sushi": 20, "coffee": 100, "smoothie": 60,
                "chicken": 45, "dessert": 70
            },
            "zone": "downtown"
        },
        {
            "id": "store_2", 
            "name": "North District Store",
            "location": (40.7589, -73.9851),
            "inventory": {
                "burger": 40, "pizza": 25, "sandwich": 35, "salad": 30,
                "pasta": 20, "sushi": 15, "coffee": 80, "smoothie": 50,
                "chicken": 35, "dessert": 60
            },
            "zone": "residential_north"
        },
        {
            "id": "store_3",
            "name": "South District Store", 
            "location": (40.6892, -74.0445),
            "inventory": {
                "burger": 35, "pizza": 20, "sandwich": 30, "salad": 25,
                "pasta": 15, "sushi": 10, "coffee": 70, "smoothie": 40,
                "chicken": 30, "dessert": 50
            },
            "zone": "residential_south"
        }
    ]
    
    for store_data in stores_data:
        store = Store(**store_data)
        stores[store.id] = store
    
    # Sample riders
    riders_data = [
        {
            "id": "rider_1",
            "name": "Alex Johnson",
            "current_location": (40.7128, -74.0060),
            "phone": "+1-555-0101",
            "efficiency_score": 1.2,
            "rating": 4.8
        },
        {
            "id": "rider_2", 
            "name": "Maria Garcia",
            "current_location": (40.7589, -73.9851),
            "phone": "+1-555-0102",
            "efficiency_score": 1.1,
            "rating": 4.6
        },
        {
            "id": "rider_3",
            "name": "David Chen",
            "current_location": (40.6892, -74.0445), 
            "phone": "+1-555-0103",
            "efficiency_score": 0.9,
            "rating": 4.4
        },
        {
            "id": "rider_4",
            "name": "Sarah Williams",
            "current_location": (40.7614, -73.9776),
            "phone": "+1-555-0104", 
            "efficiency_score": 1.3,
            "rating": 4.9
        },
        {
            "id": "rider_5",
            "name": "Mike Brown",
            "current_location": (40.8075, -73.9626),
            "phone": "+1-555-0105",
            "efficiency_score": 1.0,
            "rating": 4.5
        }
    ]
    
    for rider_data in riders_data:
        rider = Rider(**rider_data)
        riders[rider.id] = rider

# Initialize sample data on startup
initialize_sample_data()

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/api/orders', methods=['POST'])
def create_order():
    """Create a new order with automatic optimization"""
    try:
        data = request.get_json()
        
        # Create order
        order = Order(
            id=str(uuid.uuid4()),
            customer_id=data['customer_id'],
            customer_location=tuple(data['customer_location']),
            items=data['items'],
            order_time=datetime.now(),
            priority=data.get('priority', 'normal')
        )
        
        # Select best store
        best_store, store_explanation = optimization_engine.select_best_store(
            order.customer_location,
            order.items,
            list(stores.values())
        )
        
        if not best_store:
            return jsonify({
                'error': 'No suitable store available',
                'explanation': store_explanation
            }), 400
        
        # Assign best rider
        best_rider, rider_explanation = optimization_engine.assign_best_rider(
            order,
            best_store,
            list(riders.values())
        )
        
        if not best_rider:
            return jsonify({
                'error': 'No suitable rider available within SLA',
                'explanation': rider_explanation
            }), 400
        
        # Calculate estimated delivery time
        estimated_time = optimization_engine.estimate_delivery_time(
            order.customer_location,
            best_store.location,
            best_rider.current_location,
            best_store.calculate_preparation_time(order.items),
            best_rider.efficiency_score
        )
        
        # Check SLA
        time_to_delivery = (estimated_time - datetime.now()).total_seconds() / 60
        sla_met = time_to_delivery <= optimization_engine.SLA_MINUTES
        
        # Calculate profit
        profit_data = optimization_engine.calculate_order_profit(order, best_store, best_rider)
        
        # Check SLA risk
        sla_risk = optimization_engine.check_sla_risk(order, best_store, best_rider)
        
        # Update order with assignments
        order.assigned_store_id = best_store.id
        order.assigned_rider_id = best_rider.id
        order.estimated_delivery_time = estimated_time
        order.sla_met = sla_met
        order.cost = profit_data['cost']
        order.profit = profit_data['profit']
        order.decision_explanation = f"Store Selection: {store_explanation}\n\nRider Assignment: {rider_explanation}"
        order.recommendations = sla_risk['recommendations']
        order.status = 'assigned'
        
        # Update store and rider
        best_store.reserve_inventory(order.items)
        best_store.add_order()
        best_rider.assign_order(order.id)
        
        # Store order
        orders[order.id] = order
        
        return jsonify({
            'order': order.to_dict(),
            'store': best_store.to_dict(),
            'rider': best_rider.to_dict(),
            'profit_analysis': profit_data,
            'sla_risk': sla_risk,
            'success': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get order details"""
    order = orders.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    return jsonify(order.to_dict())

@app.route('/api/orders', methods=['GET'])
def list_orders():
    """List all orders"""
    return jsonify([order.to_dict() for order in orders.values()])

@app.route('/api/orders/<order_id>/reassign', methods=['POST'])
def reassign_order(order_id):
    """Reassign order to different store/rider if SLA at risk"""
    order = orders.get(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    try:
        # Release current assignments
        if order.assigned_store_id:
            current_store = stores.get(order.assigned_store_id)
            if current_store:
                current_store.release_inventory(order.items)
                current_store.complete_order()
        
        if order.assigned_rider_id:
            current_rider = riders.get(order.assigned_rider_id)
            if current_rider:
                current_rider.complete_order()
        
        # Find new assignments
        best_store, store_explanation = optimization_engine.select_best_store(
            order.customer_location,
            order.items,
            list(stores.values())
        )
        
        if not best_store:
            return jsonify({'error': 'No suitable store available for reassignment'}), 400
        
        best_rider, rider_explanation = optimization_engine.assign_best_rider(
            order,
            best_store,
            list(riders.values())
        )
        
        if not best_rider:
            return jsonify({'error': 'No suitable rider available for reassignment'}), 400
        
        # Update order
        order.assigned_store_id = best_store.id
        order.assigned_rider_id = best_rider.id
        order.decision_explanation = f"REASSIGNMENT - Store Selection: {store_explanation}\n\nRider Assignment: {rider_explanation}"
        
        # Update store and rider
        best_store.reserve_inventory(order.items)
        best_store.add_order()
        best_rider.assign_order(order.id)
        
        return jsonify({
            'order': order.to_dict(),
            'store': best_store.to_dict(),
            'rider': best_rider.to_dict(),
            'success': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stores', methods=['GET'])
def list_stores():
    """List all stores"""
    return jsonify([store.to_dict() for store in stores.values()])

@app.route('/api/riders', methods=['GET'])
def list_riders():
    """List all riders"""
    return jsonify([rider.to_dict() for rider in riders.values()])

@app.route('/api/demand/heatmap', methods=['GET'])
def get_demand_heatmap():
    """Get current demand heatmap"""
    return jsonify(demand_simulator.get_demand_heatmap())

@app.route('/api/demand/simulate', methods=['POST'])
def simulate_demand():
    """Simulate demand surge"""
    try:
        data = request.get_json()
        zone = data.get('zone', 'downtown')
        multiplier = data.get('multiplier', 2.0)
        duration = data.get('duration_minutes', 30)
        
        orders = demand_simulator.simulate_demand_surge(zone, multiplier, duration)
        
        return jsonify({
            'zone': zone,
            'multiplier': multiplier,
            'duration_minutes': duration,
            'generated_orders': len(orders),
            'orders': [order.to_dict() for order in orders]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/simulation/what-if', methods=['POST'])
def what_if_simulation():
    """Run what-if simulation"""
    try:
        scenario = request.get_json()
        results = demand_simulator.what_if_simulation(scenario)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/route/optimize', methods=['POST'])
def optimize_route():
    """Optimize delivery route"""
    try:
        data = request.get_json()
        waypoints = data.get('waypoints', [])
        
        if len(waypoints) < 2:
            return jsonify({'error': 'At least 2 waypoints required'}), 400
        
        optimized_indices = optimization_engine.optimize_route(waypoints)
        optimized_route = [waypoints[i] for i in optimized_indices]
        
        return jsonify({
            'original_route': waypoints,
            'optimized_route': optimized_route,
            'optimization_indices': optimized_indices
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/dashboard', methods=['GET'])
def get_dashboard_analytics():
    """Get dashboard analytics"""
    total_orders = len(orders)
    delivered_orders = len([o for o in orders.values() if o.status == 'delivered'])
    sla_met_orders = len([o for o in orders.values() if o.sla_met])
    
    total_profit = sum(o.profit for o in orders.values())
    avg_delivery_time = 8.5  # Mock average
    
    available_riders = len([r for r in riders.values() if r.is_available])
    active_stores = len([s for s in stores.values() if s.is_open()])
    
    return jsonify({
        'total_orders': total_orders,
        'delivered_orders': delivered_orders,
        'sla_met_orders': sla_met_orders,
        'sla_compliance_rate': (sla_met_orders / total_orders * 100) if total_orders > 0 else 0,
        'total_profit': total_profit,
        'average_delivery_time': avg_delivery_time,
        'available_riders': available_riders,
        'total_riders': len(riders),
        'active_stores': active_stores,
        'total_stores': len(stores)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
