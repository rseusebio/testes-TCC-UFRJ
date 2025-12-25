#!/usr/bin/env python3
"""
Comprehensive Visualization Script
Creates graphs comparing gRPC vs REST results across services and test scenarios
"""

import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class MetricsVisualizer:
    def __init__(self, metrics_dir: str, output_dir: str):
        """
        Initialize the visualizer
        
        Args:
            metrics_dir: Directory containing extracted metrics
            output_dir: Directory to save generated charts
        """
        self.metrics_dir = metrics_dir
        self.output_dir = output_dir
        self.protocols = ['grpc', 'rest']
        self.services = ['order', 'product', 'user', 'payment']
        self.test_scenarios = ['average_load', 'high_load', 'breakpoint', 'spike']
        
        # Create output directory structure
        self.create_output_structure()
        
        # Load all metrics data
        self.metrics_data = self.load_all_metrics()
    
    def create_output_structure(self):
        """Create organized folder structure for charts"""
        # Main categories
        categories = [
            'k6_performance',
            'latency_comparison', 
            'infrastructure_overview',
            'service_performance',
            'per_service_infrastructure',
            'per_service_logs',
            'line_graphs'
        ]
        
        # Create main output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create category subdirectories
        for category in categories:
            category_path = os.path.join(self.output_dir, category)
            os.makedirs(category_path, exist_ok=True)
        
        # Create service-specific subdirectories within per_service folders
        for service in self.services:
            # Infrastructure subdirectories
            infra_service_path = os.path.join(self.output_dir, 'per_service_infrastructure', service)
            os.makedirs(infra_service_path, exist_ok=True)
            
            # Logs subdirectories
            logs_service_path = os.path.join(self.output_dir, 'per_service_logs', service)
            os.makedirs(logs_service_path, exist_ok=True)
        
        print(f"📁 Created organized output structure in: {self.output_dir}")
        
    def load_all_metrics(self) -> Dict[str, Dict]:
        """Load all metrics from the extracted_metrics directory"""
        metrics = {}
        
        for protocol in self.protocols:
            metrics[protocol] = {}
            for scenario in self.test_scenarios:
                test_dir = f"{protocol}:{scenario}"
                test_path = os.path.join(self.metrics_dir, test_dir)
                
                if os.path.exists(test_path):
                    metrics[protocol][scenario] = self.load_test_metrics(test_path)
        
        return metrics
    
    def load_test_metrics(self, test_path: str) -> Dict[str, Any]:
        """Load metrics for a specific test scenario"""
        test_metrics = {}
        
        # Load k6 metrics
        k6_file = os.path.join(test_path, "k6_metrics.json")
        if os.path.exists(k6_file):
            with open(k6_file, 'r') as f:
                test_metrics['k6'] = json.load(f)
        
        # Load CloudWatch logs metrics
        logs_file = os.path.join(test_path, "cloudwatch_logs_metrics.json")
        if os.path.exists(logs_file):
            with open(logs_file, 'r') as f:
                test_metrics['logs'] = json.load(f)
        
        # Load CloudWatch infrastructure metrics per service
        test_metrics['infrastructure'] = {}
        for service in self.services:
            service_dir = os.path.join(test_path, service)
            if os.path.exists(service_dir):
                infra_file = os.path.join(service_dir, "cloudwatch_metrics.json")
                logs_file = os.path.join(service_dir, "cloudwatch_logs_metrics.json")
                
                if os.path.exists(infra_file):
                    with open(infra_file, 'r') as f:
                        test_metrics['infrastructure'][service] = json.load(f)
                
                if os.path.exists(logs_file):
                    with open(logs_file, 'r') as f:
                        test_metrics['logs'][service] = json.load(f)
        
        return test_metrics
    
    def create_protocol_comparison_charts(self):
        """Create charts comparing gRPC vs REST across all metrics"""
        print("📊 Creating protocol comparison charts...")
        
        # 1. K6 Performance Metrics Comparison
        self.create_k6_comparison_charts()
        
        # 2. Latency Comparison (serialize/deserialize)
        self.create_latency_comparison_charts()
        
        # 3. Infrastructure Metrics Comparison
        self.create_infrastructure_comparison_charts()
        
        # 4. Service-specific Performance Comparison
        self.create_service_performance_charts()
        
        # 5. Per-Service Infrastructure Metrics Comparison
        self.create_per_service_infrastructure_charts()
        
        # 6. Per-Service Logs Metrics Comparison
        self.create_per_service_logs_charts()
        
        # 7. Line Graph Comparisons
        self.create_line_graph_comparisons()
        
        print("✅ Protocol comparison charts created successfully!")
    
    def create_k6_comparison_charts(self):
        """Create separate K6 metrics comparison charts"""
        print("  📊 Creating K6 performance metrics charts...")
        
        metrics_to_plot = [
            ('throughput_requests_per_second', 'Throughput (req/s)', 'k6_throughput_comparison'),
            ('request_duration_avg', 'Avg Request Duration (ms)', 'k6_avg_duration_comparison'),
            ('request_duration_p95', 'P95 Request Duration (ms)', 'k6_p95_duration_comparison'),
            ('data_sent_count', 'Data Sent (bytes)', 'k6_data_sent_comparison'),
            ('data_received_count', 'Data Received (bytes)', 'k6_data_received_comparison'),
            ('vus_max', 'Max Virtual Users', 'k6_vus_max_comparison')
        ]
        
        for metric, title, filename in metrics_to_plot:
            # Prepare data
            grpc_values = []
            rest_values = []
            scenarios = []
            
            for scenario in self.test_scenarios:
                if (scenario in self.metrics_data.get('grpc', {}) and 
                    'k6' in self.metrics_data['grpc'][scenario] and
                    metric in self.metrics_data['grpc'][scenario]['k6']):
                    
                    grpc_values.append(self.metrics_data['grpc'][scenario]['k6'][metric])
                    rest_values.append(self.metrics_data['rest'][scenario]['k6'][metric])
                    scenarios.append(scenario.replace('_', ' ').title())
            
            if grpc_values and rest_values:
                # Create individual chart
                fig, ax = plt.subplots(figsize=(12, 8))
                
                x = np.arange(len(scenarios))
                width = 0.35
                
                bars1 = ax.bar(x - width/2, grpc_values, width, label='gRPC', alpha=0.8, color='#FF6B6B')
                bars2 = ax.bar(x + width/2, rest_values, width, label='REST', alpha=0.8, color='#4ECDC4')
                
                ax.set_xlabel('Test Scenario', fontsize=12)
                ax.set_ylabel(title, fontsize=12)
                ax.set_title(f'K6 {title}: gRPC vs REST Comparison', fontsize=14, fontweight='bold')
                ax.set_xticks(x)
                ax.set_xticklabels(scenarios, rotation=45, ha='right')
                ax.legend(fontsize=11)
                ax.grid(True, alpha=0.3)
                
                # Add value labels on bars
                for bar in bars1:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'{height:.2f}', ha='center', va='bottom', fontsize=10)
                
                for bar in bars2:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'{height:.2f}', ha='center', va='bottom', fontsize=10)
                
                plt.tight_layout()
                plt.savefig(os.path.join(self.output_dir, 'k6_performance', f'{filename}.png'), 
                           dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"    ✅ Created: k6_performance/{filename}.png")
    
    def create_latency_comparison_charts(self):
        """Create separate latency comparison charts for serialize/deserialize operations"""
        print("  📊 Creating latency comparison charts...")
        
        operations = ['serialize', 'deserialize']
        metrics = ['latency_avg', 'latency_p95', 'latency_p99']
        
        for operation in operations:
            for metric in metrics:
                # Prepare data
                grpc_values = []
                rest_values = []
                scenarios = []
                
                for scenario in self.test_scenarios:
                    grpc_scenario_data = self.metrics_data.get('grpc', {}).get(scenario, {})
                    rest_scenario_data = self.metrics_data.get('rest', {}).get(scenario, {})
                    
                    if ('logs' in grpc_scenario_data and 'order' in grpc_scenario_data['logs'] and
                    'logs' in rest_scenario_data and 'order' in rest_scenario_data['logs']):
                        
                        grpc_latency = grpc_scenario_data['logs']['order'].get(operation, {}).get(metric, 0)
                        rest_latency = rest_scenario_data['logs']['order'].get(operation, {}).get(metric, 0)
                        
                        if grpc_latency > 0 and rest_latency > 0:
                            grpc_values.append(grpc_latency)
                            rest_values.append(rest_latency)
                            scenarios.append(scenario.replace('_', ' ').title())
                
                if grpc_values and rest_values:
                    # Create individual chart
                    fig, ax = plt.subplots(figsize=(12, 8))
                    
                    x = np.arange(len(scenarios))
                    width = 0.35
                    
                    bars1 = ax.bar(x - width/2, grpc_values, width, label='gRPC', alpha=0.8, color='#FF6B6B')
                    bars2 = ax.bar(x + width/2, rest_values, width, label='REST', alpha=0.8, color='#4ECDC4')
                    
                    ax.set_xlabel('Test Scenario', fontsize=12)
                    ax.set_ylabel(f'{operation.title()} {metric.replace("_", " ").title()} (ms)', fontsize=12)
                    ax.set_title(f'{operation.title()} {metric.replace("_", " ").title()}: gRPC vs REST', fontsize=14, fontweight='bold')
                    ax.set_xticks(x)
                    ax.set_xticklabels(scenarios, rotation=45, ha='right')
                    ax.legend(fontsize=11)
                    ax.grid(True, alpha=0.3)
                    
                    # Add value labels on bars
                    for bar in bars1:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                               f'{height:.3f}', ha='center', va='bottom', fontsize=10)
                    
                    for bar in bars2:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                               f'{height:.3f}', ha='center', va='bottom', fontsize=10)
                    
                    # Create filename
                    filename = f'latency_{operation}_{metric}_comparison'
                    plt.tight_layout()
                    plt.savefig(os.path.join(self.output_dir, 'latency_comparison', f'{filename}.png'), 
                               dpi=300, bbox_inches='tight')
                    plt.close()
                    
                    print(f"    ✅ Created: latency_comparison/{filename}.png")
    
    def create_infrastructure_comparison_charts(self):
        """Create separate infrastructure metrics comparison charts"""
        print("  📊 Creating infrastructure metrics charts...")
        
        metrics_to_plot = [
            ('cpu_utilization', 'CPU Utilization (%)', 'infrastructure_cpu_comparison'),
            ('memory_utilization', 'Memory Utilization (%)', 'infrastructure_memory_comparison'),
            ('network_rx_bytes', 'Network RX (bytes)', 'infrastructure_network_rx_comparison'),
            ('network_tx_bytes', 'Network TX (bytes)', 'infrastructure_network_tx_comparison')
        ]
        
        for metric, title, filename in metrics_to_plot:
            # Prepare data
            grpc_values = []
            rest_values = []
            scenarios = []
            
            for scenario in self.test_scenarios:
                grpc_scenario_data = self.metrics_data.get('grpc', {}).get(scenario, {})
                rest_scenario_data = self.metrics_data.get('rest', {}).get(scenario, {})
                
                if ('infrastructure' in grpc_scenario_data and 'order' in grpc_scenario_data['infrastructure'] and
                    'infrastructure' in rest_scenario_data and 'order' in rest_scenario_data['infrastructure']):
                    
                    grpc_value = grpc_scenario_data['infrastructure']['order'].get(metric, {}).get('average_maximum', 0)
                    rest_value = rest_scenario_data['infrastructure']['order'].get(metric, {}).get('average_maximum', 0)
                    
                    if grpc_value > 0 and rest_value > 0:
                        grpc_values.append(grpc_value)
                        rest_values.append(rest_value)
                        scenarios.append(scenario.replace('_', ' ').title())
            
            if grpc_values and rest_values:
                # Create individual chart
                fig, ax = plt.subplots(figsize=(12, 8))
                
                x = np.arange(len(scenarios))
                width = 0.35
                
                bars1 = ax.bar(x - width/2, grpc_values, width, label='gRPC', alpha=0.8, color='#FF6B6B')
                bars2 = ax.bar(x + width/2, rest_values, width, label='REST', alpha=0.8, color='#4ECDC4')
                
                ax.set_xlabel('Test Scenario', fontsize=12)
                ax.set_ylabel(title, fontsize=12)
                ax.set_title(f'Infrastructure {title}: gRPC vs REST', fontsize=14, fontweight='bold')
                ax.set_xticks(x)
                ax.set_xticklabels(scenarios, rotation=45, ha='right')
                ax.legend(fontsize=11)
                ax.grid(True, alpha=0.3)
                
                # Add value labels on bars
                for bar in bars1:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'{height:.2f}', ha='center', va='bottom', fontsize=10)
                
                for bar in bars2:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'{height:.2f}', ha='center', va='bottom', fontsize=10)
                
                plt.tight_layout()
                plt.savefig(os.path.join(self.output_dir, 'infrastructure_overview', f'{filename}.png'), 
                           dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"    ✅ Created: infrastructure_overview/{filename}.png")
    
    def create_per_service_infrastructure_charts(self):
        """Create separate infrastructure metrics comparison charts for each service"""
        print("  📊 Creating per-service infrastructure metrics charts...")
        
        metrics_to_plot = [
            ('cpu_utilization', 'CPU Utilization (%)', 'infrastructure_cpu'),
            ('memory_utilization', 'Memory Utilization (%)', 'infrastructure_memory'),
            ('network_rx_bytes', 'Network RX (bytes)', 'infrastructure_network_rx'),
            ('network_tx_bytes', 'Network TX (bytes)', 'infrastructure_network_tx')
        ]
        
        for service in self.services:
            print(f"    🔧 Processing {service} service...")
            
            for metric, title, metric_prefix in metrics_to_plot:
                # Prepare data
                grpc_values = []
                rest_values = []
                scenarios = []
                
                for scenario in self.test_scenarios:
                    grpc_scenario_data = self.metrics_data.get('grpc', {}).get(scenario, {})
                    rest_scenario_data = self.metrics_data.get('rest', {}).get(scenario, {})
                    
                    if ('infrastructure' in grpc_scenario_data and service in grpc_scenario_data['infrastructure'] and
                        'infrastructure' in rest_scenario_data and service in rest_scenario_data['infrastructure']):
                        
                        grpc_value = grpc_scenario_data['infrastructure'][service].get(metric, {}).get('average_maximum', 0)
                        rest_value = rest_scenario_data['infrastructure'][service].get(metric, {}).get('average_maximum', 0)
                        
                        if grpc_value > 0 and rest_value > 0:
                            grpc_values.append(grpc_value)
                            rest_values.append(rest_value)
                            scenarios.append(scenario.replace('_', ' ').title())
                
                if grpc_values and rest_values:
                    # Create individual chart
                    fig, ax = plt.subplots(figsize=(12, 8))
                    
                    x = np.arange(len(scenarios))
                    width = 0.35
                    
                    bars1 = ax.bar(x - width/2, grpc_values, width, label='gRPC', alpha=0.8, color='#FF6B6B')
                    bars2 = ax.bar(x + width/2, rest_values, width, label='REST', alpha=0.8, color='#4ECDC4')
                    
                    ax.set_xlabel('Test Scenario', fontsize=12)
                    ax.set_ylabel(title, fontsize=12)
                    ax.set_title(f'{service.title()} Service - {title}: gRPC vs REST', fontsize=14, fontweight='bold')
                    ax.set_xticks(x)
                    ax.set_xticklabels(scenarios, rotation=45, ha='right')
                    ax.legend(fontsize=11)
                    ax.grid(True, alpha=0.3)
                    
                    # Add value labels on bars
                    for bar in bars1:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                               f'{height:.2f}', ha='center', va='bottom', fontsize=10)
                    
                    for bar in bars2:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                               f'{height:.2f}', ha='center', va='bottom', fontsize=10)
                    
                    # Create filename
                    filename = f'{service}_{metric_prefix}_comparison'
                    plt.tight_layout()
                    plt.savefig(os.path.join(self.output_dir, 'per_service_infrastructure', service, f'{filename}.png'), 
                               dpi=300, bbox_inches='tight')
                    plt.close()
                    
                    print(f"      ✅ Created: per_service_infrastructure/{service}/{filename}.png")
    
    def create_per_service_logs_charts(self):
        """Create separate logs metrics comparison charts for each service"""
        print("  📊 Creating per-service logs metrics charts...")
        
        operations = ['serialize', 'deserialize']
        metrics = ['latency_avg', 'latency_p95', 'latency_p99', 'total_requests']
        
        for service in self.services:
            print(f"    🔧 Processing {service} service...")
            
            for operation in operations:
                for metric in metrics:
                    # Prepare data
                    grpc_values = []
                    rest_values = []
                    scenarios = []
                    
                    for scenario in self.test_scenarios:
                        grpc_scenario_data = self.metrics_data.get('grpc', {}).get(scenario, {})
                        rest_scenario_data = self.metrics_data.get('rest', {}).get(scenario, {})
                        
                        if ('logs' in grpc_scenario_data and service in grpc_scenario_data['logs'] and
                            'logs' in rest_scenario_data and service in rest_scenario_data['logs']):
                            
                            grpc_value = grpc_scenario_data['logs'][service].get(operation, {}).get(metric, 0)
                            rest_value = rest_scenario_data['logs'][service].get(operation, {}).get(metric, 0)
                            
                            if grpc_value > 0 and rest_value > 0:
                                grpc_values.append(grpc_value)
                                rest_values.append(rest_value)
                                scenarios.append(scenario.replace('_', ' ').title())
                    
                    if grpc_values and rest_values:
                        # Create individual chart
                        fig, ax = plt.subplots(figsize=(12, 8))
                        
                        x = np.arange(len(scenarios))
                        width = 0.35
                        
                        bars1 = ax.bar(x - width/2, grpc_values, width, label='gRPC', alpha=0.8, color='#FF6B6B')
                        bars2 = ax.bar(x + width/2, rest_values, width, label='REST', alpha=0.8, color='#4ECDC4')
                        
                        ax.set_xlabel('Test Scenario', fontsize=12)
                        ax.set_ylabel(f'{operation.title()} {metric.replace("_", " ").title()}', fontsize=12)
                        ax.set_title(f'{service.title()} Service - {operation.title()} {metric.replace("_", " ").title()}: gRPC vs REST', fontsize=14, fontweight='bold')
                        ax.set_xticks(x)
                        ax.set_xticklabels(scenarios, rotation=45, ha='right')
                        ax.legend(fontsize=11)
                        ax.grid(True, alpha=0.3)
                        
                        # Add value labels on bars
                        for bar in bars1:
                            height = bar.get_height()
                            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                                   f'{height:.3f}', ha='center', va='bottom', fontsize=10)
                        
                        for bar in bars2:
                            height = bar.get_height()
                            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                                   f'{height:.3f}', ha='center', va='bottom', fontsize=10)
                        
                        # Create filename
                        filename = f'{service}_{operation}_{metric}_comparison'
                        plt.tight_layout()
                        plt.savefig(os.path.join(self.output_dir, 'per_service_logs', service, f'{filename}.png'), 
                                   dpi=300, bbox_inches='tight')
                        plt.close()
                        
                        print(f"      ✅ Created: per_service_logs/{service}/{filename}.png")
    
    def create_service_performance_charts(self):
        """Create separate service-specific performance comparison charts"""
        print("  📊 Creating service performance charts...")
        
        # Use order service data for comparison across all scenarios
        metrics_to_plot = [
            ('latency_avg', 'Average Latency (ms)', 'service_latency_avg_comparison'),
            ('latency_p95', 'P95 Latency (ms)', 'service_latency_p95_comparison'),
            ('latency_p99', 'P99 Latency (ms)', 'service_latency_p99_comparison'),
            ('total_requests', 'Total Requests', 'service_total_requests_comparison')
        ]
        
        for metric, title, filename in metrics_to_plot:
            # Prepare data for serialize operation
            grpc_serialize = []
            rest_serialize = []
            grpc_deserialize = []
            rest_deserialize = []
            scenarios = []
            
            for scenario in self.test_scenarios:
                grpc_scenario_data = self.metrics_data.get('grpc', {}).get(scenario, {})
                rest_scenario_data = self.metrics_data.get('rest', {}).get(scenario, {})
                
                if ('logs' in grpc_scenario_data and 'order' in grpc_scenario_data['logs'] and
                    'logs' in rest_scenario_data and 'order' in rest_scenario_data['logs']):
                    
                    # Get serialize metrics
                    grpc_ser = grpc_scenario_data['logs']['order'].get('serialize', {}).get(metric, 0)
                    rest_ser = rest_scenario_data['logs']['order'].get('serialize', {}).get(metric, 0)
                    
                    # Get deserialize metrics
                    grpc_des = grpc_scenario_data['logs']['order'].get('deserialize', {}).get(metric, 0)
                    rest_des = rest_scenario_data['logs']['order'].get('deserialize', {}).get(metric, 0)
                    
                    if all(v > 0 for v in [grpc_ser, rest_ser, grpc_des, rest_des]):
                        grpc_serialize.append(grpc_ser)
                        rest_serialize.append(rest_ser)
                        grpc_deserialize.append(grpc_des)
                        rest_deserialize.append(rest_des)
                        scenarios.append(scenario.replace('_', ' ').title())
            
            if grpc_serialize and rest_serialize:
                # Create individual chart
                fig, ax = plt.subplots(figsize=(14, 8))
                
                x = np.arange(len(scenarios))
                width = 0.2
                
                bars1 = ax.bar(x - 1.5*width, grpc_serialize, width, label='gRPC Serialize', alpha=0.8, color='#FF6B6B')
                bars2 = ax.bar(x - 0.5*width, rest_serialize, width, label='REST Serialize', alpha=0.8, color='#4ECDC4')
                bars3 = ax.bar(x + 0.5*width, grpc_deserialize, width, label='gRPC Deserialize', alpha=0.8, color='#45B7D1')
                bars4 = ax.bar(x + 1.5*width, rest_deserialize, width, label='REST Deserialize', alpha=0.8, color='#96CEB4')
                
                ax.set_xlabel('Test Scenario', fontsize=12)
                ax.set_ylabel(title, fontsize=12)
                ax.set_title(f'Service Performance {title}: gRPC vs REST (Order Service)', fontsize=14, fontweight='bold')
                ax.set_xticks(x)
                ax.set_xticklabels(scenarios, rotation=45, ha='right')
                ax.legend(fontsize=11)
                ax.grid(True, alpha=0.3)
                
                # Add value labels on bars
                for bar in bars1:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'{height:.3f}', ha='center', va='bottom', fontsize=9)
                
                for bar in bars2:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'{height:.3f}', ha='center', va='bottom', fontsize=9)
                
                for bar in bars3:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'{height:.3f}', ha='center', va='bottom', fontsize=9)
                
                for bar in bars4:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'{height:.3f}', ha='center', va='bottom', fontsize=9)
                
                plt.tight_layout()
                plt.savefig(os.path.join(self.output_dir, 'service_performance', f'{filename}.png'), 
                           dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"    ✅ Created: service_performance/{filename}.png")
    
    def create_line_graph_comparisons(self):
        """Create line graphs showing trends across test scenarios"""
        print("  📊 Creating line graph comparisons...")
        
        # Create line graphs for key metrics
        self.create_k6_line_graphs()
        self.create_latency_line_graphs()
        self.create_infrastructure_line_graphs()
        self.create_service_line_graphs()
        
        print("    ✅ Line graph comparisons created successfully!")
    
    def create_k6_line_graphs(self):
        """Create line graphs for K6 metrics across scenarios"""
        print("    📈 Creating K6 line graphs...")
        
        metrics_to_plot = [
            ('throughput_requests_per_second', 'Throughput (req/s)', 'k6_throughput_trend'),
            ('request_duration_avg', 'Avg Request Duration (ms)', 'k6_avg_duration_trend'),
            ('request_duration_p95', 'P95 Request Duration (ms)', 'k6_p95_duration_trend'),
            ('data_sent_count', 'Data Sent (bytes)', 'k6_data_sent_trend'),
            ('data_received_count', 'Data Received (bytes)', 'k6_data_received_trend'),
            ('vus_max', 'Max Virtual Users', 'k6_vus_max_trend')
        ]
        
        for metric, title, filename in metrics_to_plot:
            # Prepare data
            grpc_values = []
            rest_values = []
            scenarios = []
            
            for scenario in self.test_scenarios:
                if (scenario in self.metrics_data.get('grpc', {}) and 
                    'k6' in self.metrics_data['grpc'][scenario] and
                    metric in self.metrics_data['grpc'][scenario]['k6']):
                    
                    grpc_values.append(self.metrics_data['grpc'][scenario]['k6'][metric])
                    rest_values.append(self.metrics_data['rest'][scenario]['k6'][metric])
                    scenarios.append(scenario.replace('_', ' ').title())
            
            if grpc_values and rest_values:
                # Create line graph
                fig, ax = plt.subplots(figsize=(12, 8))
                
                x = range(len(scenarios))
                
                # Plot lines with markers
                ax.plot(x, grpc_values, 'o-', linewidth=3, markersize=8, label='gRPC', 
                       color='#FF6B6B', alpha=0.8)
                ax.plot(x, rest_values, 's-', linewidth=3, markersize=8, label='REST', 
                       color='#4ECDC4', alpha=0.8)
                
                ax.set_xlabel('Test Scenario', fontsize=12)
                ax.set_ylabel(title, fontsize=12)
                ax.set_title(f'K6 {title}: gRPC vs REST Trends', fontsize=14, fontweight='bold')
                ax.set_xticks(x)
                ax.set_xticklabels(scenarios, rotation=45, ha='right')
                ax.legend(fontsize=11)
                ax.grid(True, alpha=0.3)
                
                # Add value labels on points
                for i, (grpc_val, rest_val) in enumerate(zip(grpc_values, rest_values)):
                    ax.annotate(f'{grpc_val:.2f}', (i, grpc_val), textcoords="offset points", 
                               xytext=(0,10), ha='center', fontsize=9, color='#FF6B6B')
                    ax.annotate(f'{rest_val:.2f}', (i, rest_val), textcoords="offset points", 
                               xytext=(0,-15), ha='center', fontsize=9, color='#4ECDC4')
                
                plt.tight_layout()
                plt.savefig(os.path.join(self.output_dir, 'line_graphs', f'{filename}.png'), 
                           dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"      ✅ Created: line_graphs/{filename}.png")
    
    def create_latency_line_graphs(self):
        """Create line graphs for latency metrics across scenarios"""
        print("    📈 Creating latency line graphs...")
        
        operations = ['serialize', 'deserialize']
        metrics = ['latency_avg', 'latency_p95', 'latency_p99']
        
        for operation in operations:
            for metric in metrics:
                # Prepare data
                grpc_values = []
                rest_values = []
                scenarios = []
                
                for scenario in self.test_scenarios:
                    grpc_scenario_data = self.metrics_data.get('grpc', {}).get(scenario, {})
                    rest_scenario_data = self.metrics_data.get('rest', {}).get(scenario, {})
                    
                    if ('logs' in grpc_scenario_data and 'order' in grpc_scenario_data['logs'] and
                        'logs' in rest_scenario_data and 'order' in rest_scenario_data['logs']):
                        
                        grpc_latency = grpc_scenario_data['logs']['order'].get(operation, {}).get(metric, 0)
                        rest_latency = rest_scenario_data['logs']['order'].get(operation, {}).get(metric, 0)
                        
                        if grpc_latency > 0 and rest_latency > 0:
                            grpc_values.append(grpc_latency)
                            rest_values.append(rest_latency)
                            scenarios.append(scenario.replace('_', ' ').title())
                
                if grpc_values and rest_values:
                    # Create line graph
                    fig, ax = plt.subplots(figsize=(12, 8))
                    
                    x = range(len(scenarios))
                    
                    # Plot lines with markers
                    ax.plot(x, grpc_values, 'o-', linewidth=3, markersize=8, label='gRPC', 
                           color='#FF6B6B', alpha=0.8)
                    ax.plot(x, rest_values, 's-', linewidth=3, markersize=8, label='REST', 
                           color='#4ECDC4', alpha=0.8)
                    
                    ax.set_xlabel('Test Scenario', fontsize=12)
                    ax.set_ylabel(f'{operation.title()} {metric.replace("_", " ").title()} (ms)', fontsize=12)
                    ax.set_title(f'{operation.title()} {metric.replace("_", " ").title()}: gRPC vs REST Trends', 
                               fontsize=14, fontweight='bold')
                    ax.set_xticks(x)
                    ax.set_xticklabels(scenarios, rotation=45, ha='right')
                    ax.legend(fontsize=11)
                    ax.grid(True, alpha=0.3)
                    
                    # Add value labels on points
                    for i, (grpc_val, rest_val) in enumerate(zip(grpc_values, rest_values)):
                        ax.annotate(f'{grpc_val:.3f}', (i, grpc_val), textcoords="offset points", 
                                   xytext=(0,10), ha='center', fontsize=9, color='#FF6B6B')
                        ax.annotate(f'{rest_val:.3f}', (i, rest_val), textcoords="offset points", 
                                   xytext=(0,-15), ha='center', fontsize=9, color='#4ECDC4')
                    
                    # Create filename
                    filename = f'latency_{operation}_{metric}_trend'
                    plt.tight_layout()
                    plt.savefig(os.path.join(self.output_dir, 'line_graphs', f'{filename}.png'), 
                               dpi=300, bbox_inches='tight')
                    plt.close()
                    
                    print(f"      ✅ Created: line_graphs/{filename}.png")
    
    def create_infrastructure_line_graphs(self):
        """Create line graphs for infrastructure metrics across scenarios"""
        print("    📈 Creating infrastructure line graphs...")
        
        metrics_to_plot = [
            ('cpu_utilization', 'CPU Utilization (%)', 'infrastructure_cpu_trend'),
            ('memory_utilization', 'Memory Utilization (%)', 'infrastructure_memory_trend'),
            ('network_rx_bytes', 'Network RX (bytes)', 'infrastructure_network_rx_trend'),
            ('network_tx_bytes', 'Network TX (bytes)', 'infrastructure_network_tx_trend')
        ]
        
        for metric, title, filename in metrics_to_plot:
            # Prepare data
            grpc_values = []
            rest_values = []
            scenarios = []
            
            for scenario in self.test_scenarios:
                grpc_scenario_data = self.metrics_data.get('grpc', {}).get(scenario, {})
                rest_scenario_data = self.metrics_data.get('rest', {}).get(scenario, {})
                
                if ('infrastructure' in grpc_scenario_data and 'order' in grpc_scenario_data['infrastructure'] and
                    'infrastructure' in rest_scenario_data and 'order' in rest_scenario_data['infrastructure']):
                    
                    grpc_value = grpc_scenario_data['infrastructure']['order'].get(metric, {}).get('average_maximum', 0)
                    rest_value = rest_scenario_data['infrastructure']['order'].get(metric, {}).get('average_maximum', 0)
                    
                    if grpc_value > 0 and rest_value > 0:
                        grpc_values.append(grpc_value)
                        rest_values.append(rest_value)
                        scenarios.append(scenario.replace('_', ' ').title())
            
            if grpc_values and rest_values:
                # Create line graph
                fig, ax = plt.subplots(figsize=(12, 8))
                
                x = range(len(scenarios))
                
                # Plot lines with markers
                ax.plot(x, grpc_values, 'o-', linewidth=3, markersize=8, label='gRPC', 
                       color='#FF6B6B', alpha=0.8)
                ax.plot(x, rest_values, 's-', linewidth=3, markersize=8, label='REST', 
                       color='#4ECDC4', alpha=0.8)
                
                ax.set_xlabel('Test Scenario', fontsize=12)
                ax.set_ylabel(title, fontsize=12)
                ax.set_title(f'Infrastructure {title}: gRPC vs REST Trends', fontsize=14, fontweight='bold')
                ax.set_xticks(x)
                ax.set_xticklabels(scenarios, rotation=45, ha='right')
                ax.legend(fontsize=11)
                ax.grid(True, alpha=0.3)
                
                # Add value labels on points
                for i, (grpc_val, rest_val) in enumerate(zip(grpc_values, rest_values)):
                    ax.annotate(f'{grpc_val:.2f}', (i, grpc_val), textcoords="offset points", 
                               xytext=(0,10), ha='center', fontsize=9, color='#FF6B6B')
                    ax.annotate(f'{rest_val:.2f}', (i, rest_val), textcoords="offset points", 
                               xytext=(0,-15), ha='center', fontsize=9, color='#4ECDC4')
                
                plt.tight_layout()
                plt.savefig(os.path.join(self.output_dir, 'line_graphs', f'{filename}.png'), 
                           dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"      ✅ Created: line_graphs/{filename}.png")
    
    def create_service_line_graphs(self):
        """Create line graphs for service performance metrics across scenarios"""
        print("    📈 Creating service performance line graphs...")
        
        metrics_to_plot = [
            ('latency_avg', 'Average Latency (ms)', 'service_latency_avg_trend'),
            ('latency_p95', 'P95 Latency (ms)', 'service_latency_p95_trend'),
            ('latency_p99', 'P99 Latency (ms)', 'service_latency_p99_trend'),
            ('total_requests', 'Total Requests', 'service_total_requests_trend')
        ]
        
        for metric, title, filename in metrics_to_plot:
            # Prepare data
            grpc_values = []
            rest_values = []
            scenarios = []
            
            for scenario in self.test_scenarios:
                grpc_scenario_data = self.metrics_data.get('grpc', {}).get(scenario, {})
                rest_scenario_data = self.metrics_data.get('rest', {}).get(scenario, {})
                
                if ('logs' in grpc_scenario_data and 'order' in grpc_scenario_data['logs'] and
                    'logs' in rest_scenario_data and 'order' in rest_scenario_data['logs']):
                    
                    grpc_value = grpc_scenario_data['logs']['order'].get('serialize', {}).get(metric, 0)
                    rest_value = rest_scenario_data['logs']['order'].get('serialize', {}).get(metric, 0)
                    
                    if grpc_value > 0 and rest_value > 0:
                        grpc_values.append(grpc_value)
                        rest_values.append(rest_value)
                        scenarios.append(scenario.replace('_', ' ').title())
            
            if grpc_values and rest_values:
                # Create line graph
                fig, ax = plt.subplots(figsize=(12, 8))
                
                x = range(len(scenarios))
                
                # Plot lines with markers
                ax.plot(x, grpc_values, 'o-', linewidth=3, markersize=8, label='gRPC', 
                       color='#FF6B6B', alpha=0.8)
                ax.plot(x, rest_values, 's-', linewidth=3, markersize=8, label='REST', 
                       color='#4ECDC4', alpha=0.8)
                
                ax.set_xlabel('Test Scenario', fontsize=12)
                ax.set_ylabel(title, fontsize=12)
                ax.set_title(f'Service Performance {title}: gRPC vs REST Trends', fontsize=14, fontweight='bold')
                ax.set_xticks(x)
                ax.set_xticklabels(scenarios, rotation=45, ha='right')
                ax.legend(fontsize=11)
                ax.grid(True, alpha=0.3)
                
                # Add value labels on points
                for i, (grpc_val, rest_val) in enumerate(zip(grpc_values, rest_values)):
                    ax.annotate(f'{grpc_val:.3f}', (i, grpc_val), textcoords="offset points", 
                               xytext=(0,10), ha='center', fontsize=9, color='#FF6B6B')
                    ax.annotate(f'{rest_val:.3f}', (i, rest_val), textcoords="offset points", 
                               xytext=(0,-15), ha='center', fontsize=9, color='#4ECDC4')
                
                plt.tight_layout()
                plt.savefig(os.path.join(self.output_dir, 'line_graphs', f'{filename}.png'), 
                           dpi=300, bbox_inches='tight')
                plt.close()
                
                print(f"      ✅ Created: line_graphs/{filename}.png")
    
    def create_summary_dashboard(self):
        """Create a summary dashboard with key metrics"""
        print("📈 Creating summary dashboard...")
        
        # Create a comprehensive summary table
        summary_data = []
        
        for protocol in self.protocols:
            for scenario in self.test_scenarios:
                if scenario in self.metrics_data.get(protocol, {}):
                    scenario_data = self.metrics_data[protocol][scenario]
                    
                    # K6 metrics
                    k6_metrics = scenario_data.get('k6', {})
                    throughput = k6_metrics.get('throughput_requests_per_second', 0)
                    avg_duration = k6_metrics.get('request_duration_avg', 0)
                    p95_duration = k6_metrics.get('request_duration_p95', 0)
                    
                    # Latency metrics (order service)
                    logs_metrics = scenario_data.get('logs', {}).get('order', {})
                    serialize_avg = logs_metrics.get('serialize', {}).get('latency_avg', 0)
                    deserialize_avg = logs_metrics.get('deserialize', {}).get('latency_avg', 0)
                    
                    # Infrastructure metrics (order service)
                    infra_metrics = scenario_data.get('infrastructure', {}).get('order', {})
                    cpu_util = infra_metrics.get('cpu_utilization', {}).get('average_maximum', 0)
                    memory_util = infra_metrics.get('memory_utilization', {}).get('average_maximum', 0)
                    
                    summary_data.append({
                        'Protocol': protocol.upper(),
                        'Test Scenario': scenario.replace('_', ' ').title(),
                        'Throughput (req/s)': f"{throughput:.2f}",
                        'Avg Duration (ms)': f"{avg_duration:.2f}",
                        'P95 Duration (ms)': f"{p95_duration:.2f}",
                        'Serialize Latency (ms)': f"{serialize_avg:.3f}",
                        'Deserialize Latency (ms)': f"{deserialize_avg:.3f}",
                        'CPU Utilization (%)': f"{cpu_util:.2f}",
                        'Memory Utilization (%)': f"{memory_util:.2f}"
                    })
        
        # Create summary table
        if summary_data:
            df = pd.DataFrame(summary_data)
            
            fig, ax = plt.subplots(figsize=(16, 8))
            ax.axis('tight')
            ax.axis('off')
            
            table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1.2, 1.5)
            
            # Style the table
            for i in range(len(df.columns)):
                table[(0, i)].set_facecolor('#4ECDC4')
                table[(0, i)].set_text_props(weight='bold', color='white')
            
            plt.title('Performance Metrics Summary Dashboard', fontsize=16, fontweight='bold', pad=20)
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, 'summary_dashboard.png'), 
                       dpi=300, bbox_inches='tight')
            plt.close()
            
            # Save summary as CSV
            csv_path = os.path.join(self.output_dir, 'performance_summary.csv')
            df.to_csv(csv_path, index=False)
            print(f"  📁 Summary dashboard saved to: {os.path.join(self.output_dir, 'summary_dashboard.png')}")
            print(f"  📁 Summary CSV saved to: {csv_path}")
    
    def generate_all_visualizations(self):
        """Generate all visualization types"""
        print("🎨 Starting visualization generation...")
        
        try:
            # Create protocol comparison charts
            self.create_protocol_comparison_charts()
            
            # Create summary dashboard
            self.create_summary_dashboard()
            
            print(f"\n✅ All visualizations generated successfully!")
            print(f"📁 Output directory: {self.output_dir}")
            print(f"📊 Generated charts organized in folders:")
            print(f"   📁 k6_performance/")
            print(f"     - k6_throughput_comparison.png")
            print(f"     - k6_avg_duration_comparison.png")
            print(f"     - k6_p95_duration_comparison.png")
            print(f"     - k6_data_sent_comparison.png")
            print(f"     - k6_data_received_comparison.png")
            print(f"     - k6_vus_max_comparison.png")
            print(f"   📁 latency_comparison/")
            print(f"     - latency_serialize_latency_avg_comparison.png")
            print(f"     - latency_serialize_latency_p95_comparison.png")
            print(f"     - latency_serialize_latency_p99_comparison.png")
            print(f"     - latency_deserialize_latency_avg_comparison.png")
            print(f"     - latency_deserialize_latency_p95_comparison.png")
            print(f"     - latency_deserialize_latency_p99_comparison.png")
            print(f"   📁 infrastructure_overview/")
            print(f"     - infrastructure_cpu_comparison.png")
            print(f"     - infrastructure_memory_comparison.png")
            print(f"     - infrastructure_network_rx_comparison.png")
            print(f"     - infrastructure_network_tx_comparison.png")
            print(f"   📁 service_performance/")
            print(f"     - service_latency_avg_comparison.png")
            print(f"     - service_latency_p95_comparison.png")
            print(f"     - service_latency_p99_comparison.png")
            print(f"     - service_total_requests_comparison.png")
            print(f"   📁 per_service_infrastructure/")
            print(f"     📁 order/")
            print(f"       - order_infrastructure_cpu_comparison.png")
            print(f"       - order_infrastructure_memory_comparison.png")
            print(f"       - order_infrastructure_network_rx_comparison.png")
            print(f"       - order_infrastructure_network_tx_comparison.png")
            print(f"     📁 product/")
            print(f"       - product_infrastructure_cpu_comparison.png")
            print(f"       - product_infrastructure_memory_comparison.png")
            print(f"       - product_infrastructure_network_rx_comparison.png")
            print(f"       - product_infrastructure_network_tx_comparison.png")
            print(f"     📁 user/")
            print(f"       - user_infrastructure_cpu_comparison.png")
            print(f"       - user_infrastructure_memory_comparison.png")
            print(f"       - user_infrastructure_network_rx_comparison.png")
            print(f"       - user_infrastructure_network_tx_comparison.png")
            print(f"     📁 payment/")
            print(f"       - payment_infrastructure_cpu_comparison.png")
            print(f"       - payment_infrastructure_memory_comparison.png")
            print(f"       - payment_infrastructure_network_rx_comparison.png")
            print(f"       - payment_infrastructure_network_tx_comparison.png")
            print(f"   📁 per_service_logs/")
            print(f"     📁 order/")
            print(f"       - order_serialize_latency_avg_comparison.png")
            print(f"       - order_serialize_latency_p95_comparison.png")
            print(f"       - order_serialize_latency_p99_comparison.png")
            print(f"       - order_serialize_total_requests_comparison.png")
            print(f"       - order_deserialize_latency_avg_comparison.png")
            print(f"       - order_deserialize_latency_p95_comparison.png")
            print(f"       - order_deserialize_latency_p99_comparison.png")
            print(f"       - order_deserialize_total_requests_comparison.png")
            print(f"     📁 product/")
            print(f"       - product_serialize_latency_avg_comparison.png")
            print(f"       - product_serialize_latency_p95_comparison.png")
            print(f"       - product_serialize_latency_p99_comparison.png")
            print(f"       - product_serialize_total_requests_comparison.png")
            print(f"       - product_deserialize_latency_avg_comparison.png")
            print(f"       - product_deserialize_latency_p95_comparison.png")
            print(f"       - product_deserialize_latency_p99_comparison.png")
            print(f"       - product_deserialize_total_requests_comparison.png")
            print(f"     📁 user/")
            print(f"       - user_serialize_latency_avg_comparison.png")
            print(f"       - user_serialize_latency_p95_comparison.png")
            print(f"       - user_serialize_latency_p99_comparison.png")
            print(f"       - user_serialize_total_requests_comparison.png")
            print(f"       - user_deserialize_latency_avg_comparison.png")
            print(f"       - user_deserialize_latency_p95_comparison.png")
            print(f"       - user_deserialize_latency_p99_comparison.png")
            print(f"       - user_deserialize_total_requests_comparison.png")
            print(f"     📁 payment/")
            print(f"       - payment_serialize_latency_avg_comparison.png")
            print(f"       - payment_serialize_latency_p95_comparison.png")
            print(f"       - payment_serialize_latency_p99_comparison.png")
            print(f"       - payment_serialize_total_requests_comparison.png")
            print(f"       - payment_deserialize_latency_avg_comparison.png")
            print(f"       - payment_deserialize_latency_p95_comparison.png")
            print(f"       - payment_deserialize_latency_p99_comparison.png")
            print(f"       - payment_deserialize_total_requests_comparison.png")
            print(f"   📁 line_graphs/")
            print(f"     - k6_throughput_trend.png")
            print(f"     - k6_avg_duration_trend.png")
            print(f"     - k6_p95_duration_trend.png")
            print(f"     - k6_data_sent_trend.png")
            print(f"     - k6_data_received_trend.png")
            print(f"     - k6_vus_max_trend.png")
            print(f"     - latency_serialize_latency_avg_trend.png")
            print(f"     - latency_serialize_latency_p95_trend.png")
            print(f"     - latency_serialize_latency_p99_trend.png")
            print(f"     - latency_deserialize_latency_avg_trend.png")
            print(f"     - latency_deserialize_latency_p95_trend.png")
            print(f"     - latency_deserialize_latency_p99_trend.png")
            print(f"     - infrastructure_cpu_trend.png")
            print(f"     - infrastructure_memory_trend.png")
            print(f"     - infrastructure_network_rx_trend.png")
            print(f"     - infrastructure_network_tx_trend.png")
            print(f"     - service_latency_avg_trend.png")
            print(f"     - service_latency_p95_trend.png")
            print(f"     - service_latency_p99_trend.png")
            print(f"     - service_total_requests_trend.png")
            print(f"   📁 Summary files (root):")
            print(f"     - summary_dashboard.png")
            print(f"     - performance_summary.csv")
            
        except Exception as e:
            print(f"❌ Error generating visualizations: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate performance comparison visualizations')
    parser.add_argument('--metrics-dir', default='extracted_metrics', 
                       help='Directory containing extracted metrics (default: extracted_metrics)')
    parser.add_argument('--output-dir', default='visualizations', 
                       help='Directory to save generated charts (default: visualizations)')
    
    args = parser.parse_args()
    
    # Check if metrics directory exists
    if not os.path.exists(args.metrics_dir):
        print(f"❌ Error: Metrics directory '{args.metrics_dir}' not found")
        print("Please run the extraction scripts first to generate metrics data.")
        sys.exit(1)
    
    print(f"🚀 Starting visualization generation...")
    print(f"📂 Metrics directory: {args.metrics_dir}")
    print(f"📁 Output directory: {args.output_dir}")
    
    # Create visualizer and generate charts
    visualizer = MetricsVisualizer(args.metrics_dir, args.output_dir)
    visualizer.generate_all_visualizations()


if __name__ == "__main__":
    main()
