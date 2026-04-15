#!/usr/bin/env python3
"""
Test script to verify the Quick Commerce Logistics System functionality
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_models():
    """Test the core models"""
    print("Testing Models...")
    
    try:
        from models.order import Order
        from models.rider import Rider
        from models.store import Store
        
        # Test Order creation
        order = Order(
            id="test_order_1",
            customer_id="customer_123",
            customer_location=(40.7128, -74.0060),
            items=[{"id": "burger", "quantity": 2, "price": 8.99}],
            order_time=datetime.now(),
            priority="normal"
        )
        print(f"✓ Order created: {order.id}")
        
        # Test Rider creation
        rider = Rider(
            id="test_rider_1",
            name="Test Rider",
            current_location=(40.7128, -74.0060),
            phone="+1-555-0101",
            efficiency_score=1.2,
            rating=4.8
        )
        print(f"✓ Rider created: {rider.name}")
        
        # Test Store creation
        store = Store(
            id="test_store_1",
            name="Test Store",
            location=(40.7589, -73.9851),
            inventory={"burger": 50, "pizza": 30},
            zone="downtown"
        )
        print(f"✓ Store created: {store.name}")
        
        return True
        
    except Exception as e:
        print(f"✗ Model test failed: {e}")
        return False

def test_services():
    """Test the service classes"""
    print("\nTesting Services...")
    
    try:
        from services.optimization_engine import OptimizationEngine
        from services.demand_simulator import DemandSimulator
        
        # Test Optimization Engine
        engine = OptimizationEngine()
        distance = engine.calculate_distance((40.7128, -74.0060), (40.7589, -73.9851))
        print(f"✓ Distance calculation: {distance:.2f} km")
        
        # Test Demand Simulator
        simulator = DemandSimulator()
        order = simulator.generate_order()
        print(f"✓ Order generated: {order.id}")
        
        return True
        
    except Exception as e:
        print(f"✗ Service test failed: {e}")
        return False

def test_order_processing():
    """Test complete order processing workflow"""
    print("\nTesting Order Processing Workflow...")
    
    try:
        from models.order import Order
        from models.rider import Rider
        from models.store import Store
        from services.optimization_engine import OptimizationEngine
        from services.demand_simulator import DemandSimulator
        
        # Initialize components
        engine = OptimizationEngine()
        simulator = DemandSimulator()
        
        # Create test data
        order = simulator.generate_order()
        
        store = Store(
            id="store_1",
            name="Downtown Store",
            location=(40.7128, -74.0060),
            inventory={"burger": 50, "pizza": 30, "sandwich": 40},
            zone="downtown"
        )
        
        rider = Rider(
            id="rider_1",
            name="Test Rider",
            current_location=(40.7128, -74.0060),
            phone="+1-555-0101",
            efficiency_score=1.2,
            rating=4.8
        )
        
        # Test store selection
        best_store, explanation = engine.select_best_store(
            order.customer_location,
            order.items,
            [store]
        )
        
        if best_store:
            print(f"✓ Store selected: {best_store.name}")
        else:
            print("✗ No store selected")
            return False
        
        # Test rider assignment
        best_rider, rider_explanation = engine.assign_best_rider(
            order,
            best_store,
            [rider]
        )
        
        if best_rider:
            print(f"✓ Rider assigned: {best_rider.name}")
        else:
            print("✗ No rider assigned")
            return False
        
        # Test profit calculation
        profit_data = engine.calculate_order_profit(order, best_store, best_rider)
        print(f"✓ Profit calculated: ${profit_data['profit']:.2f}")
        
        # Test SLA risk assessment
        sla_risk = engine.check_sla_risk(order, best_store, best_rider)
        print(f"✓ SLA risk assessed: {sla_risk['risk_level']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Order processing test failed: {e}")
        return False

def test_api_structure():
    """Test if Flask app structure is correct"""
    print("\nTesting API Structure...")
    
    try:
        # Check if app.py exists and can be imported
        if os.path.exists('app.py'):
            print("✓ app.py exists")
        else:
            print("✗ app.py not found")
            return False
        
        # Check if templates directory exists
        if os.path.exists('templates'):
            print("✓ templates directory exists")
        else:
            print("✗ templates directory not found")
            return False
        
        # Check if index.html exists
        if os.path.exists('templates/index.html'):
            print("✓ index.html exists")
        else:
            print("✗ index.html not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ API structure test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Quick Commerce Logistics System - System Test")
    print("=" * 50)
    
    tests = [
        test_models,
        test_services,
        test_order_processing,
        test_api_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for deployment.")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
