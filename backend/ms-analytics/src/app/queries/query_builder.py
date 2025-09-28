"""
Query builder for analytics SQL templates
"""

import os
from string import Template
from typing import List, Dict, Any, Optional
from datetime import date, datetime
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class QueryBuilder:
    """Build SQL queries from templates with parameter substitution"""
    
    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.catalog_database = settings.aws_glue_catalog_database
    
    def build_revenue_query(
        self,
        year_from: int = None,
        month_from: int = 1,
        route_codes: List[str] = None,
        date_from: date = None,
        date_to: date = None,
        limit: int = 100
    ) -> str:
        """Build revenue by route query"""
        
        template = self._load_template('revenue_queries.sql')
        
        # Build filters
        filters = self._build_filters(route_codes, date_from, date_to)
        
        # Default year if not provided
        if year_from is None:
            year_from = datetime.now().year
        
        query = template.substitute(
            catalog_database=self.catalog_database,
            year_from=year_from,
            month_from=month_from,
            route_filter=filters['route_filter'],
            date_filter=filters['date_filter'],
            limit=limit
        )
        
        logger.info("Built revenue query", year_from=year_from, limit=limit)
        return query
    
    def build_occupancy_query(
        self,
        year_from: int = None,
        route_codes: List[str] = None,
        date_from: date = None,
        date_to: date = None,
        group_by: str = "day_of_week"
    ) -> str:
        """Build occupancy trends query"""
        
        template = self._load_template('occupancy_queries.sql')
        
        # Build filters
        filters = self._build_filters(route_codes, date_from, date_to)
        
        # Default year if not provided
        if year_from is None:
            year_from = datetime.now().year
        
        query = template.substitute(
            catalog_database=self.catalog_database,
            year_from=year_from,
            route_filter=filters['route_filter'],
            date_filter=filters['date_filter']
        )
        
        logger.info("Built occupancy query", year_from=year_from, group_by=group_by)
        return query
    
    def build_customer_segmentation_query(
        self,
        segment_criteria: str = "frequency",
        year_from: int = None,
        date_from: date = None,
        date_to: date = None,
        limit: int = 100
    ) -> str:
        """Build customer segmentation query"""
        
        template = self._load_template('customer_queries.sql')
        
        # Build date filter
        filters = self._build_filters(None, date_from, date_to)
        
        # Default year if not provided
        if year_from is None:
            year_from = datetime.now().year
        
        query = template.substitute(
            catalog_database=self.catalog_database,
            year_from=year_from,
            date_filter=filters['date_filter'],
            segment_criteria=segment_criteria,
            limit=limit
        )
        
        logger.info("Built customer segmentation query", segment_criteria=segment_criteria, limit=limit)
        return query
    
    def build_route_performance_query(
        self,
        metrics: List[str],
        year_from: int = None,
        route_codes: List[str] = None,
        date_from: date = None,
        date_to: date = None
    ) -> str:
        """Build route performance query"""
        
        template = self._load_template('route_queries.sql')
        
        # Build filters
        filters = self._build_filters(route_codes, date_from, date_to)
        
        # Default year if not provided
        if year_from is None:
            year_from = datetime.now().year
        
        # Join metrics for template
        metrics_str = ','.join(metrics) if metrics else 'revenue,occupancy,on_time'
        
        query = template.substitute(
            catalog_database=self.catalog_database,
            year_from=year_from,
            route_filter=filters['route_filter'],
            date_filter=filters['date_filter'],
            metrics=metrics_str
        )
        
        logger.info("Built route performance query", metrics=metrics, year_from=year_from)
        return query
    
    def _build_filters(
        self, 
        route_codes: List[str] = None, 
        date_from: date = None, 
        date_to: date = None
    ) -> Dict[str, str]:
        """Build WHERE clause filters"""
        
        route_filter = ""
        if route_codes:
            route_list = "', '".join(route_codes)
            route_filter = f"AND t.route_code IN ('{route_list}')"
        
        date_filter = ""
        if date_from:
            date_filter += f"AND DATE(t.departure_time) >= '{date_from}'"
        if date_to:
            date_filter += f" AND DATE(t.departure_time) <= '{date_to}'"
        
        return {
            'route_filter': route_filter,
            'date_filter': date_filter
        }
    
    def _load_template(self, template_name: str) -> Template:
        """Load SQL template from file"""
        template_path = os.path.join(self.template_dir, template_name)
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return Template(content)
        except FileNotFoundError:
            logger.error("Template file not found", template=template_name)
            raise
        except Exception as e:
            logger.error("Failed to load template", template=template_name, error=str(e))
            raise
    
    def validate_custom_query(self, sql_query: str) -> bool:
        """Validate custom SQL query for security"""
        
        # Convert to uppercase for checking
        upper_query = sql_query.upper().strip()
        
        # Must start with SELECT
        if not upper_query.startswith('SELECT'):
            return False
        
        # Forbidden operations
        forbidden_keywords = [
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'CREATE', 'ALTER', 
            'TRUNCATE', 'EXEC', 'EXECUTE', 'DECLARE', 'GRANT', 'REVOKE'
        ]
        
        for keyword in forbidden_keywords:
            if keyword in upper_query:
                logger.warning("Custom query contains forbidden keyword", keyword=keyword)
                return False
        
        # Must reference our catalog database
        if self.catalog_database not in sql_query:
            logger.warning("Custom query must reference catalog database", database=self.catalog_database)
            return False
        
        return True
