#!/usr/bin/env python3
"""
Advanced Analytics and Reporting for GCP Free Tier Monitor
"""

import json
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
from pathlib import Path

class GCPUsageAnalytics:
    """Advanced analytics for GCP resource usage tracking"""
    
    def __init__(self, db_path: str = "gcp_usage_history.db"):
        self.db_path = db_path
        self.init_database()
        self.logger = logging.getLogger(__name__)
    
    def init_database(self):
        """Initialize SQLite database for usage tracking"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS usage_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    project_id TEXT NOT NULL,
                    service TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    limit_value REAL NOT NULL,
                    usage_percentage REAL NOT NULL,
                    violation BOOLEAN DEFAULT FALSE
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    project_id TEXT NOT NULL,
                    service TEXT NOT NULL,
                    incident_type TEXT NOT NULL,
                    description TEXT,
                    severity TEXT DEFAULT 'warning',
                    resolved BOOLEAN DEFAULT FALSE,
                    resolution_time DATETIME
                )
            ''')
    
    def record_usage(self, project_id: str, service: str, metrics: Dict[str, Any]):
        """Record current usage metrics"""
        with sqlite3.connect(self.db_path) as conn:
            for metric_name, data in metrics.items():
                usage_percentage = (data['current'] / data['limit']) * 100 if data['limit'] > 0 else 0
                violation = usage_percentage > 100
                
                conn.execute('''
                    INSERT INTO usage_history 
                    (project_id, service, metric_name, metric_value, limit_value, usage_percentage, violation)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (project_id, service, metric_name, data['current'], data['limit'], usage_percentage, violation))
    
    def record_incident(self, project_id: str, service: str, incident_type: str, 
                       description: str, severity: str = 'warning'):
        """Record a monitoring incident"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO incidents 
                (project_id, service, incident_type, description, severity)
                VALUES (?, ?, ?, ?, ?)
            ''', (project_id, service, incident_type, description, severity))
    
    def generate_usage_report(self, days: int = 30) -> str:
        """Generate comprehensive usage report"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            # Get usage trends
            usage_df = pd.read_sql_query('''
                SELECT * FROM usage_history 
                WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp DESC
            ''', conn, params=(start_date, end_date))
            
            # Get incidents
            incidents_df = pd.read_sql_query('''
                SELECT * FROM incidents 
                WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp DESC
            ''', conn, params=(start_date, end_date))
        
        report = f"""
# GCP Free Tier Usage Report
**Report Period:** {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics
- **Total Measurements:** {len(usage_df)}
- **Services Monitored:** {usage_df['service'].nunique()}
- **Violations Detected:** {len(usage_df[usage_df['violation'] == True])}
- **Incidents Recorded:** {len(incidents_df)}

## Service Usage Overview
"""
        
        if not usage_df.empty:
            # Service-wise summary
            service_summary = usage_df.groupby('service').agg({
                'usage_percentage': ['mean', 'max'],
                'violation': 'sum'
            }).round(2)
            
            for service in service_summary.index:
                avg_usage = service_summary.loc[service, ('usage_percentage', 'mean')]
                max_usage = service_summary.loc[service, ('usage_percentage', 'max')]
                violations = service_summary.loc[service, ('violation', 'sum')]
                
                report += f"""
### {service.upper()}
- **Average Usage:** {avg_usage}%
- **Peak Usage:** {max_usage}%
- **Violations:** {violations}
"""
        
        # Recent incidents
        if not incidents_df.empty:
            report += "\n## Recent Incidents\n"
            for _, incident in incidents_df.head(10).iterrows():
                report += f"""
**{incident['timestamp']}** - {incident['service']} ({incident['severity']})
- {incident['description']}
"""
        
        # Recommendations
        report += self._generate_recommendations(usage_df, incidents_df)
        
        return report
    
    def _generate_recommendations(self, usage_df: pd.DataFrame, incidents_df: pd.DataFrame) -> str:
        """Generate actionable recommendations based on usage patterns"""
        recommendations = "\n## 🎯 Recommendations\n"
        
        if usage_df.empty:
            return recommendations + "- No usage data available for analysis.\n"
        
        # High usage services
        high_usage = usage_df[usage_df['usage_percentage'] > 80]
        if not high_usage.empty:
            services = high_usage['service'].unique()
            recommendations += f"""
### ⚠️ High Usage Alert
- **Services approaching limits:** {', '.join(services)}
- **Action:** Consider scaling down or optimizing these services
"""
        
        # Frequent violations
        violations_by_service = usage_df[usage_df['violation'] == True]['service'].value_counts()
        if not violations_by_service.empty:
            recommendations += f"""
### 🚨 Frequent Violations
- **Most violated service:** {violations_by_service.index[0]} ({violations_by_service.iloc[0]} times)
- **Action:** Review resource allocation and usage patterns
"""
        
        # Trend analysis
        if len(usage_df) > 1:
            latest_usage = usage_df.groupby('service')['usage_percentage'].last()
            increasing_services = []
            
            for service in latest_usage.index:
                service_data = usage_df[usage_df['service'] == service]['usage_percentage']
                if len(service_data) > 1 and service_data.iloc[0] > service_data.iloc[-1]:
                    increasing_services.append(service)
            
            if increasing_services:
                recommendations += f"""
### 📈 Usage Trends
- **Increasing usage:** {', '.join(increasing_services)}
- **Action:** Monitor closely and prepare scaling strategies
"""
        
        return recommendations
    
    def create_usage_dashboard(self, output_dir: str = "reports"):
        """Create visual dashboard with charts"""
        Path(output_dir).mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            usage_df = pd.read_sql_query('''
                SELECT * FROM usage_history 
                WHERE timestamp >= datetime('now', '-7 days')
                ORDER BY timestamp
            ''', conn)
        
        if usage_df.empty:
            self.logger.warning("No data available for dashboard")
            return
        
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('GCP Free Tier Usage Dashboard - Last 7 Days', fontsize=16)
        
        # Usage percentage over time
        for service in usage_df['service'].unique():
            service_data = usage_df[usage_df['service'] == service]
            axes[0, 0].plot(pd.to_datetime(service_data['timestamp']), 
                           service_data['usage_percentage'], 
                           marker='o', label=service, linewidth=2)
        
        axes[0, 0].set_title('Usage Percentage Over Time')
        axes[0, 0].set_ylabel('Usage %')
        axes[0, 0].legend()
        axes[0, 0].axhline(y=80, color='orange', linestyle='--', alpha=0.7, label='Warning (80%)')
        axes[0, 0].axhline(y=100, color='red', linestyle='--', alpha=0.7, label='Limit (100%)')
        
        # Service usage distribution
        latest_usage = usage_df.groupby('service')['usage_percentage'].last()
        colors = ['green' if x < 50 else 'orange' if x < 80 else 'red' for x in latest_usage.values]
        axes[0, 1].bar(latest_usage.index, latest_usage.values, color=colors)
        axes[0, 1].set_title('Current Usage by Service')
        axes[0, 1].set_ylabel('Usage %')
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Violation frequency
        violations = usage_df[usage_df['violation'] == True]['service'].value_counts()
        if not violations.empty:
            axes[1, 0].pie(violations.values, labels=violations.index, autopct='%1.1f%%')
            axes[1, 0].set_title('Violations by Service')
        else:
            axes[1, 0].text(0.5, 0.5, 'No Violations\nDetected', 
                           ha='center', va='center', fontsize=14, color='green')
            axes[1, 0].set_title('Violations by Service')
        
        # Usage trends
        daily_avg = usage_df.groupby(usage_df['timestamp'].str[:10])['usage_percentage'].mean()
        axes[1, 1].plot(daily_avg.index, daily_avg.values, marker='o', linewidth=3)
        axes[1, 1].set_title('Daily Average Usage Trend')
        axes[1, 1].set_ylabel('Avg Usage %')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/gcp_usage_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Dashboard saved to {output_dir}/gcp_usage_dashboard.png")
