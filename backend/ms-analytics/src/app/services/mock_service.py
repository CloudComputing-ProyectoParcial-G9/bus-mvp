"""
Mock data service for local development
"""

import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
import structlog

logger = structlog.get_logger(__name__)


class MockAnalyticsService:
    """Mock service for local development with realistic data"""
    
    def __init__(self):
        self.routes = [
            {"code": "RT001", "name": "Madrid - Barcelona Express", "origin": "Madrid", "destination": "Barcelona"},
            {"code": "RT002", "name": "Sevilla - Valencia Direct", "origin": "Sevilla", "destination": "Valencia"},
            {"code": "RT003", "name": "Bilbao - Zaragoza Route", "origin": "Bilbao", "destination": "Zaragoza"},
            {"code": "RT004", "name": "Barcelona - Madrid Night", "origin": "Barcelona", "destination": "Madrid"},
            {"code": "RT005", "name": "Valencia - Sevilla Express", "origin": "Valencia", "destination": "Sevilla"},
            {"code": "RT006", "name": "Zaragoza - Bilbao Direct", "origin": "Zaragoza", "destination": "Bilbao"},
        ]
        
        logger.info("Mock analytics service initialized")
    
    async def execute_query(self, sql_query: str, max_results: int = None) -> tuple[str, List[Dict[str, Any]]]:
        """Mock query execution"""
        execution_id = f"mock-{random.randint(1000, 9999)}"
        
        # Simple query routing based on keywords
        if "revenue" in sql_query.lower():
            results = self._generate_revenue_data()
        elif "occupancy" in sql_query.lower():
            results = self._generate_occupancy_data()
        elif "customer" in sql_query.lower():
            results = self._generate_customer_data()
        elif "performance" in sql_query.lower():
            results = self._generate_performance_data()
        else:
            results = self._generate_generic_data()
        
        # Limit results if specified
        if max_results:
            results = results[:max_results]
        
        logger.info(
            "Mock query executed", 
            execution_id=execution_id, 
            result_count=len(results)
        )
        
        return execution_id, results
    
    def _generate_revenue_data(self) -> List[Dict[str, Any]]:
        """Generate mock revenue data"""
        data = []
        
        for route in self.routes:
            # Generate data for last 6 months
            for month_offset in range(6):
                period_date = date.today().replace(day=1) - timedelta(days=month_offset * 30)
                period = period_date.strftime("%Y-%m")
                
                total_tickets = random.randint(400, 800)
                average_price = random.uniform(25.0, 65.0)
                total_revenue = total_tickets * average_price
                total_trips = random.randint(15, 30)
                
                data.append({
                    "route_code": route["code"],
                    "route_name": route["name"],
                    "origin_city": route["origin"],
                    "destination_city": route["destination"],
                    "period": period,
                    "total_revenue": round(total_revenue, 2),
                    "total_tickets": total_tickets,
                    "total_trips": total_trips,
                    "average_price": round(average_price, 2),
                    "revenue_growth": round(random.uniform(-15.0, 25.0), 1)
                })
        
        # Sort by revenue descending
        return sorted(data, key=lambda x: x["total_revenue"], reverse=True)
    
    def _generate_occupancy_data(self) -> List[Dict[str, Any]]:
        """Generate mock occupancy data"""
        days_of_week = [
            ("0", "Sunday"),
            ("1", "Monday"), 
            ("2", "Tuesday"),
            ("3", "Wednesday"),
            ("4", "Thursday"),
            ("5", "Friday"),
            ("6", "Saturday")
        ]
        
        data = []
        for day_num, day_name in days_of_week:
            total_trips = random.randint(80, 150)
            tickets_sold = random.randint(int(total_trips * 0.4), int(total_trips * 0.9))
            total_capacity = total_trips * random.randint(40, 50)
            occupancy_rate = (tickets_sold / total_capacity) * 100 if total_capacity > 0 else 0
            
            data.append({
                "period": day_num,
                "period_label": day_name,
                "total_trips": total_trips,
                "tickets_sold": tickets_sold,
                "total_capacity": total_capacity,
                "occupancy_rate": round(occupancy_rate, 2),
                "average_occupancy": round(tickets_sold / total_trips, 1) if total_trips > 0 else 0
            })
        
        return data
    
    def _generate_customer_data(self) -> List[Dict[str, Any]]:
        """Generate mock customer segmentation data"""
        segments = [
            "Frequent Travelers",
            "Occasional Users", 
            "Business Travelers",
            "Weekend Travelers",
            "Budget Conscious",
            "Premium Customers"
        ]
        
        data = []
        total_customers = random.randint(8000, 12000)
        remaining_customers = total_customers
        
        for i, segment in enumerate(segments):
            if i == len(segments) - 1:
                customer_count = remaining_customers
            else:
                customer_count = random.randint(800, 2500)
                remaining_customers -= customer_count
            
            average_trips = random.uniform(2.0, 12.0)
            average_revenue = random.uniform(80.0, 300.0)
            total_revenue = customer_count * average_revenue
            percentage = (customer_count / total_customers) * 100
            
            data.append({
                "segment_id": f"SEG{i+1:03d}",
                "segment_name": segment,
                "customer_count": customer_count,
                "average_trips": round(average_trips, 1),
                "average_revenue": round(average_revenue, 2),
                "total_revenue": round(total_revenue, 2),
                "percentage": round(percentage, 1)
            })
        
        return sorted(data, key=lambda x: x["total_revenue"], reverse=True)
    
    def _generate_performance_data(self) -> List[Dict[str, Any]]:
        """Generate mock route performance data"""
        data = []
        
        for route in self.routes:
            total_trips = random.randint(120, 200)
            total_revenue = random.uniform(15000, 45000)
            occupancy = random.uniform(55.0, 85.0)
            on_time = random.uniform(78.0, 95.0)
            cancellation = random.uniform(1.0, 8.0)
            
            # Calculate performance score
            performance_score = (occupancy + on_time - cancellation) / 2
            
            data.append({
                "route_code": route["code"],
                "route_name": route["name"],
                "origin_city": route["origin"],
                "destination_city": route["destination"],
                "total_revenue": round(total_revenue, 2),
                "average_occupancy": round(occupancy, 1),
                "on_time_performance": round(on_time, 1),
                "cancellation_rate": round(cancellation, 1),
                "total_trips": total_trips,
                "performance_score": round(performance_score, 1)
            })
        
        return sorted(data, key=lambda x: x["performance_score"], reverse=True)
    
    def _generate_generic_data(self) -> List[Dict[str, Any]]:
        """Generate generic mock data"""
        return [
            {
                "id": i,
                "value": random.randint(1, 1000),
                "category": f"Category {random.choice(['A', 'B', 'C', 'D'])}",
                "timestamp": datetime.utcnow().isoformat()
            }
            for i in range(random.randint(10, 50))
        ]
    
    async def health_check(self) -> Dict[str, str]:
        """Mock health check"""
        return {"status": "healthy", "message": "Mock service active"}
    
    async def get_table_metadata(self, table_name: str) -> Dict[str, Any]:
        """Mock table metadata"""
        return {
            "name": table_name,
            "columns": [
                {"name": "id", "type": "bigint"},
                {"name": "route_code", "type": "string"},
                {"name": "timestamp", "type": "timestamp"},
                {"name": "value", "type": "double"}
            ],
            "location": f"s3://mock-bucket/tables/{table_name}/",
            "partitions": [{"name": "year", "type": "string"}]
        }
