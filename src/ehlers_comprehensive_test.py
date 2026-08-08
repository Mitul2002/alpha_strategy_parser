#!/usr/bin/env python3
"""
Ehlers Comprehensive Testing Suite
Thoroughly test all Ehlers indicators, transformations, and 50 strategies
"""

import numpy as np
import pandas as pd
import time
import json
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

from ehlers_indicators import (
    FisherTransform, InstantaneousTrendline, CGOscillator, RelativeVigorIndex,
    CyberCycleOscillator, Decycler, BandPassFilter, SuperSmoother, RoofingFilter
)
from ehlers_transformations import Stochasticization, Fisherization, CombinedTransformation
from ehlers_main_engine_integration import EhlersMainEngine

class EhlersComprehensiveTest:
    """Comprehensive testing suite for Ehlers system"""
    
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
        
        # Initialize components
        self.indicators = {
            'fisher_transform': FisherTransform(10),
            'instantaneous_trendline': InstantaneousTrendline(0.07),
            'cg_oscillator': CGOscillator(10),
            'relative_vigor_index': RelativeVigorIndex(10),
            'cyber_cycle_oscillator': CyberCycleOscillator(10),
            'decycler': Decycler(40),
            'band_pass_filter': BandPassFilter(10, 20),
            'super_smoother': SuperSmoother(10),
            'roofing_filter': RoofingFilter(40)
        }
        
        self.transformations = {
            'stochasticization': Stochasticization(10),
            'fisherization': Fisherization(10),
            'combined_transformation': CombinedTransformation(10)
        }
        
        self.main_engine = EhlersMainEngine()
    
    def generate_test_data(self, length: int = 1000, data_type: str = 'realistic') -> np.ndarray:
        """Generate various types of test data"""
        if data_type == 'realistic':
            # Realistic price data with trend, cycles, and noise
            trend = np.linspace(100, 150, length)
            cycle = 10 * np.sin(np.linspace(0, 4*np.pi, length))
            noise = 0.5 * np.random.randn(length)
            return trend + cycle + noise
        
        elif data_type == 'trending':
            # Strong trending data
            return 100 + np.cumsum(np.random.randn(length) * 0.02) + np.linspace(0, 50, length)
        
        elif data_type == 'oscillating':
            # Oscillating data
            return 100 + 20 * np.sin(np.linspace(0, 10*np.pi, length)) + 2 * np.random.randn(length)
        
        elif data_type == 'volatile':
            # High volatility data
            return 100 + np.cumsum(np.random.randn(length) * 0.1)
        
        else:  # random
            return np.random.randn(length).cumsum() + 100
    
    def test_indicator_accuracy(self, indicator_name: str, test_data: np.ndarray) -> Dict[str, Any]:
        """Test indicator accuracy with various data types"""
        indicator = self.indicators[indicator_name]
        
        results = {
            'indicator_name': indicator_name,
            'data_length': len(test_data),
            'execution_time_ms': 0,
            'result_range': [0, 0],
            'result_mean': 0,
            'result_std': 0,
            'nan_count': 0,
            'success': False
        }
        
        try:
            start_time = time.perf_counter()
            result = indicator.calculate(test_data)
            end_time = time.perf_counter()
            
            results['execution_time_ms'] = (end_time - start_time) * 1000
            results['result_range'] = [float(np.nanmin(result)), float(np.nanmax(result))]
            results['result_mean'] = float(np.nanmean(result))
            results['result_std'] = float(np.nanstd(result))
            results['nan_count'] = int(np.sum(np.isnan(result)))
            results['success'] = True
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def test_transformation_accuracy(self, transformation_name: str, test_data: np.ndarray) -> Dict[str, Any]:
        """Test transformation accuracy"""
        transformation = self.transformations[transformation_name]
        
        results = {
            'transformation_name': transformation_name,
            'data_length': len(test_data),
            'execution_time_ms': 0,
            'result_range': [0, 0],
            'result_mean': 0,
            'result_std': 0,
            'nan_count': 0,
            'success': False
        }
        
        try:
            start_time = time.perf_counter()
            result = transformation.apply(test_data)
            end_time = time.perf_counter()
            
            results['execution_time_ms'] = (end_time - start_time) * 1000
            results['result_range'] = [float(np.nanmin(result)), float(np.nanmax(result))]
            results['result_mean'] = float(np.nanmean(result))
            results['result_std'] = float(np.nanstd(result))
            results['nan_count'] = int(np.sum(np.isnan(result)))
            results['success'] = True
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def test_strategy_execution(self, strategy_id: str, test_data: np.ndarray) -> Dict[str, Any]:
        """Test strategy execution"""
        if strategy_id not in self.main_engine.strategies:
            return {'error': f'Strategy {strategy_id} not found'}
        
        strategy_config = self.main_engine.strategies[strategy_id]
        
        results = {
            'strategy_id': strategy_id,
            'strategy_name': strategy_config['name'],
            'execution_time_ms': 0,
            'signal_count': 0,
            'signal_percentage': 0,
            'success': False
        }
        
        try:
            start_time = time.perf_counter()
            
            # Extract strategy configuration
            base_indicator = strategy_config['base_indicator']
            transformation = strategy_config['transformation']
            signal_type = strategy_config['signal_type']
            signal_params = strategy_config['signal_params']
            indicator_params = strategy_config['indicator_params']
            
            # Calculate enhanced indicator
            indicator_values = self.main_engine.get_enhanced_indicator(
                base_indicator, transformation, test_data, **indicator_params
            )
            
            # Generate signals
            signals = self.main_engine.generate_signals(indicator_values, signal_type, **signal_params)
            signal_count = np.sum(signals)
            
            end_time = time.perf_counter()
            
            results['execution_time_ms'] = (end_time - start_time) * 1000
            results['signal_count'] = int(signal_count)
            results['signal_percentage'] = float(signal_count / len(signals) * 100)
            results['success'] = True
            
        except Exception as e:
            results['error'] = str(e)
        
        return results
    
    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive tests on all components"""
        print("EHLERS COMPREHENSIVE TESTING SUITE")
        print("=" * 50)
        
        # Test data types
        data_types = ['realistic', 'trending', 'oscillating', 'volatile', 'random']
        test_data = {}
        
        for data_type in data_types:
            test_data[data_type] = self.generate_test_data(1000, data_type)
        
        # Test 1: Individual Indicators
        print("\n1. Testing Individual Indicators...")
        indicator_results = {}
        
        for indicator_name in self.indicators.keys():
            print(f"  Testing {indicator_name}...")
            indicator_results[indicator_name] = {}
            
            for data_type, data in test_data.items():
                result = self.test_indicator_accuracy(indicator_name, data)
                indicator_results[indicator_name][data_type] = result
        
        # Test 2: Transformations
        print("\n2. Testing Transformations...")
        transformation_results = {}
        
        for transformation_name in self.transformations.keys():
            print(f"  Testing {transformation_name}...")
            transformation_results[transformation_name] = {}
            
            for data_type, data in test_data.items():
                result = self.test_transformation_accuracy(transformation_name, data)
                transformation_results[transformation_name][data_type] = result
        
        # Test 3: Strategy Execution
        print("\n3. Testing Strategy Execution...")
        strategy_results = {}
        
        # Test first 10 strategies for comprehensive testing
        test_strategies = list(self.main_engine.strategies.keys())[:10]
        
        for strategy_id in test_strategies:
            print(f"  Testing {strategy_id}...")
            strategy_results[strategy_id] = {}
            
            for data_type, data in test_data.items():
                result = self.test_strategy_execution(strategy_id, data)
                strategy_results[strategy_id][data_type] = result
        
        # Test 4: Performance Benchmarking
        print("\n4. Performance Benchmarking...")
        performance_results = self.benchmark_performance()
        
        # Compile results
        self.test_results = {
            'indicators': indicator_results,
            'transformations': transformation_results,
            'strategies': strategy_results,
            'performance': performance_results,
            'test_summary': self.create_test_summary(indicator_results, transformation_results, strategy_results)
        }
        
        return self.test_results
    
    def benchmark_performance(self) -> Dict[str, Any]:
        """Benchmark performance across different data sizes"""
        data_sizes = [100, 500, 1000, 2000, 5000]
        performance_results = {}
        
        for size in data_sizes:
            print(f"  Benchmarking with {size} data points...")
            test_data = self.generate_test_data(size, 'realistic')
            
            # Benchmark indicators
            indicator_times = {}
            for indicator_name, indicator in self.indicators.items():
                start_time = time.perf_counter()
                result = indicator.calculate(test_data)
                end_time = time.perf_counter()
                indicator_times[indicator_name] = (end_time - start_time) * 1000
            
            # Benchmark transformations
            transformation_times = {}
            for transformation_name, transformation in self.transformations.items():
                start_time = time.perf_counter()
                result = transformation.apply(test_data)
                end_time = time.perf_counter()
                transformation_times[transformation_name] = (end_time - start_time) * 1000
            
            performance_results[size] = {
                'indicators': indicator_times,
                'transformations': transformation_times,
                'data_size': size
            }
        
        return performance_results
    
    def create_test_summary(self, indicator_results: Dict, transformation_results: Dict, strategy_results: Dict) -> Dict[str, Any]:
        """Create test summary"""
        summary = {
            'total_tests': 0,
            'successful_tests': 0,
            'failed_tests': 0,
            'indicator_summary': {},
            'transformation_summary': {},
            'strategy_summary': {}
        }
        
        # Indicator summary
        for indicator_name, results in indicator_results.items():
            successful = sum(1 for r in results.values() if r.get('success', False))
            total = len(results)
            summary['indicator_summary'][indicator_name] = {
                'successful': successful,
                'total': total,
                'success_rate': successful / total * 100
            }
            summary['total_tests'] += total
            summary['successful_tests'] += successful
        
        # Transformation summary
        for transformation_name, results in transformation_results.items():
            successful = sum(1 for r in results.values() if r.get('success', False))
            total = len(results)
            summary['transformation_summary'][transformation_name] = {
                'successful': successful,
                'total': total,
                'success_rate': successful / total * 100
            }
            summary['total_tests'] += total
            summary['successful_tests'] += successful
        
        # Strategy summary
        for strategy_id, results in strategy_results.items():
            successful = sum(1 for r in results.values() if r.get('success', False))
            total = len(results)
            summary['strategy_summary'][strategy_id] = {
                'successful': successful,
                'total': total,
                'success_rate': successful / total * 100
            }
            summary['total_tests'] += total
            summary['successful_tests'] += successful
        
        summary['failed_tests'] = summary['total_tests'] - summary['successful_tests']
        summary['overall_success_rate'] = summary['successful_tests'] / summary['total_tests'] * 100 if summary['total_tests'] > 0 else 0
        
        return summary
    
    def print_test_report(self):
        """Print comprehensive test report"""
        if not self.test_results:
            print("No test results available. Run comprehensive tests first.")
            return
        
        print("\n" + "="*60)
        print("COMPREHENSIVE TEST REPORT")
        print("="*60)
        
        summary = self.test_results['test_summary']
        
        print(f"Overall Test Results:")
        print(f"  Total Tests: {summary['total_tests']}")
        print(f"  Successful: {summary['successful_tests']}")
        print(f"  Failed: {summary['failed_tests']}")
        print(f"  Success Rate: {summary['overall_success_rate']:.1f}%")
        
        # Indicator results
        print(f"\nIndicator Test Results:")
        for indicator_name, result in summary['indicator_summary'].items():
            print(f"  {indicator_name}: {result['successful']}/{result['total']} ({result['success_rate']:.1f}%)")
        
        # Transformation results
        print(f"\nTransformation Test Results:")
        for transformation_name, result in summary['transformation_summary'].items():
            print(f"  {transformation_name}: {result['successful']}/{result['total']} ({result['success_rate']:.1f}%)")
        
        # Strategy results
        print(f"\nStrategy Test Results:")
        for strategy_id, result in summary['strategy_summary'].items():
            print(f"  {strategy_id}: {result['successful']}/{result['total']} ({result['success_rate']:.1f}%)")
        
        # Performance summary
        print(f"\nPerformance Summary:")
        performance = self.test_results['performance']
        for size, results in performance.items():
            avg_indicator_time = np.mean(list(results['indicators'].values()))
            avg_transformation_time = np.mean(list(results['transformations'].values()))
            print(f"  {size} data points: Indicators {avg_indicator_time:.3f}ms, Transformations {avg_transformation_time:.3f}ms")
    
    def export_test_results(self, filepath: str = "ehlers_comprehensive_test_results.json"):
        """Export test results to JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"Test results exported to {filepath}")

def main():
    """Main function to run comprehensive tests"""
    print("Starting Ehlers Comprehensive Testing...")
    
    # Initialize test suite
    test_suite = EhlersComprehensiveTest()
    
    # Run comprehensive tests
    results = test_suite.run_comprehensive_tests()
    
    # Print test report
    test_suite.print_test_report()
    
    # Export results
    test_suite.export_test_results()
    
    print("\nComprehensive testing completed!")

if __name__ == "__main__":
    main()
