import sys
import os
import time

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.common.database import init_db, SessionLocal
from app.common.models import TrafficSample
from agent.wfp_wrapper import DataCollector

def test_data_collection():
    print("Testing Data Collection...")
    
    # 1. Initialize DB
    init_db()
    
    # 2. Setup Collector (flush interval 1s)
    collector = DataCollector(flush_interval=1, batch_size=5)
    
    # 3. Add Samples
    print("Adding 3 samples...")
    for i in range(3):
        sample = {
            "process_name": f"test_proc_{i}.exe",
            "process_path": f"C:\\Windows\\test_proc_{i}.exe",
            "remote_ip": f"10.0.0.{i}",
            "remote_port": 80,
            "direction": "Outbound"
        }
        collector.add_sample(sample)
        
    print("Waiting for flush...")
    time.sleep(2) # Wait for flush interval
    
    collector.shutdown()
    
    # 4. Verify DB
    try:
        with SessionLocal() as db:
            count = db.query(TrafficSample).count()
            print(f"DB Row Count: {count}")
            
            # Since we just added 3, and existing DB might have more, just check if >= 3
            if count >= 3:
                # Check for our specific sample
                last = db.query(TrafficSample).filter(TrafficSample.process_name == "test_proc_0.exe").first()
                if last:
                    print(f"Found sample: {last}")
                    print("SUCCESS: Data collected.")
                else:
                     print("FAILURE: Specific sample not found.")
            else:
                print("FAILURE: DB count too low.")
                
    except Exception as e:
        print(f"DB Error: {e}")

if __name__ == "__main__":
    test_data_collection()
