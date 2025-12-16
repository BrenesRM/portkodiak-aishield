import csv
import sys
import os
import argparse
from datetime import datetime

# Path setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.common.database import SessionLocal
from app.common.models import TrafficSample

def export_traffic_data(output_file=None):
    """Exports TrafficSample table to CSV."""
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"traffic_export_{timestamp}.csv"

    print(f"Exporting traffic data to {output_file}...")
    
    try:
        with SessionLocal() as db:
            samples = db.query(TrafficSample).all()
            
            if not samples:
                print("No samples found in database.")
                return

            # Open CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Header
                header = [
                    "timestamp", "process_name", "process_path", "process_hash",
                    "parent_info", "remote_ip", "remote_port", "remote_hostname",
                    "protocol", "direction", "is_malicious"
                ]
                writer.writerow(header)
                
                # Rows
                count = 0
                for s in samples:
                    writer.writerow([
                        s.timestamp, s.process_name, s.process_path, s.process_hash,
                        s.parent_info, s.remote_ip, s.remote_port, s.remote_hostname,
                        s.protocol, s.direction, s.is_malicious
                    ])
                    count += 1
            
            print(f"Successfully exported {count} records to {output_file}")
            
    except Exception as e:
        print(f"Export failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export traffic training data.")
    parser.add_argument("-o", "--output", help="Output CSV file path")
    args = parser.parse_args()
    
    export_traffic_data(args.output)
