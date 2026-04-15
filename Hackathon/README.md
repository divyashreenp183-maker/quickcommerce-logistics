# Quick Commerce Logistics System

A Python-based autonomous quick-commerce logistics system that simulates 10-minute delivery using Flask as the backend API with intelligent optimization and real-time decision making.

## Features

### Core Functionality
- **Nearest Dark Store Selection**: Intelligent store selection based on distance, inventory availability, and workload
- **Smart Rider Assignment**: Greedy scoring algorithm considering distance, efficiency, and availability
- **SLA Enforcement**: 10-minute delivery guarantee with automatic reassignment for at-risk orders
- **Route Optimization**: Distance-based route calculation and optimization
- **Profit Computation**: Real-time profit analysis per order with detailed breakdown
- **Explainable AI**: Plain English explanations for all system decisions
- **SLA Risk Detection**: Proactive risk assessment with actionable recommendations

### Advanced Features
- **Demand Zone Simulation**: Multi-zone demand modeling with surge prediction
- **What-If Analysis**: Simulation mode for various operational scenarios
- **Real-time Analytics**: Dashboard with key performance indicators
- **Modern Web UI**: Responsive interface with good UX design

## System Architecture

### Object-Oriented Design
```
├── models/
│   ├── order.py      # Order management and status tracking
│   ├── rider.py      # Rider assignment and performance tracking
│   └── store.py      # Store inventory and workload management
├── services/
│   ├── optimization_engine.py  # Core optimization algorithms
│   └── demand_simulator.py    # Demand forecasting and simulation
├── templates/
│   └── index.html    # Modern web interface
├── app.py           # Flask API server
├── requirements.txt # Python dependencies
└── vercel.json     # Deployment configuration
```

## API Endpoints

### Order Management
- `POST /api/orders` - Create new order with automatic optimization
- `GET /api/orders` - List all orders
- `GET /api/orders/{id}` - Get specific order details
- `POST /api/orders/{id}/reassign` - Reassign order if SLA at risk

### System Information
- `GET /api/stores` - List all stores
- `GET /api/riders` - List all riders
- `GET /api/analytics/dashboard` - Dashboard analytics

### Simulation & Analysis
- `GET /api/demand/heatmap` - Current demand heatmap
- `POST /api/demand/simulate` - Simulate demand surge
- `POST /api/simulation/what-if` - What-if scenario analysis
- `POST /api/route/optimize` - Route optimization

## Order Output Structure

Each order response includes:
```json
{
  "order": {
    "id": "order_uuid",
    "customer_id": "customer_1234",
    "customer_location": [lat, lon],
    "items": [{"id": "burger", "quantity": 2, "price": 8.99}],
    "assigned_store_id": "store_1",
    "assigned_rider_id": "rider_1",
    "estimated_delivery_time": "2024-01-01T12:10:00",
    "sla_met": true,
    "cost": 15.50,
    "profit": 8.25,
    "decision_explanation": "Store selected based on...",
    "recommendations": ["Monitor rider progress..."]
  },
  "store": {...},
  "rider": {...},
  "profit_analysis": {...},
  "sla_risk": {...}
}
```

## Installation & Setup

### Local Development
1. Install Python 3.9+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Access the web interface at `http://localhost:5000`

### Deployment (Vercel)
1. Install Vercel CLI
2. Deploy:
   ```bash
   vercel --prod
   ```

## Key Algorithms

### Store Selection Score
```
score = efficiency_score × distance_penalty × inventory_score × workload_penalty × hours_bonus
```

### Rider Assignment Score
```
score = efficiency_score × rating × distance_penalty × availability_bonus × workload_penalty × priority_bonus × vehicle_factor
```

### SLA Risk Assessment
- **Critical**: >10 minutes estimated delivery
- **High**: 8-10 minutes estimated delivery
- **Medium**: 6-8 minutes estimated delivery
- **Low**: <6 minutes estimated delivery

## Simulation Capabilities

### Demand Scenarios
- **Demand Surge**: Multiplier-based order generation
- **Rider Shortage**: Availability percentage simulation
- **Store Closure**: Impact analysis for store downtime

### What-If Analysis
- Surge multiplier effects
- Rider shortage impacts
- Store closure consequences
- Recommended mitigation strategies

## Performance Metrics

### Real-time Dashboard
- Total orders and delivery rate
- SLA compliance percentage
- Available riders vs total
- Total profit and margins
- Store and rider utilization

### Order Analytics
- Per-order profit breakdown
- Delivery time accuracy
- Store performance metrics
- Rider efficiency tracking

## Technology Stack

- **Backend**: Python 3.9+, Flask
- **Frontend**: HTML5, TailwindCSS, JavaScript
- **Deployment**: Vercel (@vercel/python)
- **Algorithms**: Haversine distance, Greedy optimization, Nearest neighbor

## Sample Usage

### Create Order
```javascript
const orderData = {
  customer_id: "customer_1234",
  customer_location: [40.7128, -74.0060],
  priority: "normal",
  items: [{"id": "burger", "quantity": 2, "price": 8.99}]
};

fetch('/api/orders', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify(orderData)
})
.then(response => response.json())
.then(data => console.log(data));
```

### Simulate Demand Surge
```javascript
fetch('/api/demand/simulate', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    zone: "downtown",
    multiplier: 2.0,
    duration_minutes: 30
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Configuration

### System Constants
- **SLA_MINUTES**: 10 (delivery guarantee)
- **AVERAGE_SPEED_KMH**: 30 (city delivery speed)
- **PICKUP_TIME_MINUTES**: 2 (store pickup time)

### Store Configuration
- **max_concurrent_orders**: 20 per store
- **preparation_time_avg**: 3 minutes base
- **operating_hours**: 8:00 - 20:00

### Rider Configuration
- **efficiency_score**: 0.5 - 1.5 (performance multiplier)
- **vehicle_types**: bike, scooter, car
- **shift_hours**: 8-hour shifts

## Future Enhancements

- Machine learning for demand prediction
- Real-time GPS tracking integration
- Multi-warehouse optimization
- Dynamic pricing algorithms
- Customer preference learning
- Traffic-aware routing
- Predictive maintenance for vehicles

## License

MIT License - see LICENSE file for details.
