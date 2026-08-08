#!/usr/bin/env python3
"""
Monitor the progress of the massive Ehlers execution
"""

import time
import psutil
import os
from pathlib import Path

def monitor_execution():
    """Monitor the execution progress"""
    print("EHLERS MASSIVE EXECUTION MONITOR")
    print("=" * 50)
    
    # Find the process
    process = None
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info', 'create_time']):
        try:
            if 'ehlers_massive_execution_fixed.py' in ' '.join(proc.info['cmdline']):
                process = proc
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if process is None:
        print("No Ehlers execution process found")
        return
    
    print(f"Process ID: {process.pid}")
    print(f"Started: {time.ctime(process.create_time())}")
    
    # Monitor for a few iterations
    for i in range(5):
        try:
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            print(f"\nIteration {i+1}:")
            print(f"  CPU Usage: {cpu_percent:.1f}%")
            print(f"  Memory Usage: {memory_mb:.1f} MB")
            print(f"  Runtime: {time.time() - process.create_time():.1f} seconds")
            
            # Check for output files
            output_files = [
                'ehlers_massive_execution_aggregated.json',
                'ehlers_reliance_trades.json',
                'ehlers_massive_execution_report.txt'
            ]
            
            for file in output_files:
                if Path(file).exists():
                    size = Path(file).stat().st_size
                    print(f"  {file}: {size:,} bytes")
                else:
                    print(f"  {file}: Not created yet")
            
            time.sleep(10)  # Wait 10 seconds
            
        except psutil.NoSuchProcess:
            print("Process has completed!")
            break
        except Exception as e:
            print(f"Error monitoring: {e}")
            break

if __name__ == "__main__":
    monitor_execution()
