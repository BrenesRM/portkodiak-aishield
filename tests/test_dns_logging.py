import sys
import os
import time
import socket

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.common.database import init_db, SessionLocal
from app.common.models import DnsLog
from agent.wfp_wrapper import DnsResolver

def test_dns_logging():
    print("Testing DNS Logging...")
    
    # 1. Initialize DB (will create tables if not exist)
    init_db()
    
    # 2. Setup Resolver
    resolver = DnsResolver(cache_ttl=0) # No cache to force resolution/logging
    
    # 3. Resolve a known host
    ip = "8.8.8.8"
    print(f"Resolving {ip}...")
    hostname = resolver.resolve_ip(ip)
    print(f"Resolved: {hostname}")
    
    # Give time for background thread log
    time.sleep(1) 
    
    # 4. Check DB
    try:
        with SessionLocal() as db:
            logs = db.query(DnsLog).filter(DnsLog.ip_address == ip).all()
            print(f"Found {len(logs)} logs for {ip}")
            
            if len(logs) > 0:
                print(f"Latest log: {logs[-1]}")
                print("SUCCESS: DNS resolution verified in DB.")
            else:
                print("FAILURE: No logs found in DB.")
                
    except Exception as e:
        print(f"DB Error: {e}")
        
    resolver.shutdown()

if __name__ == "__main__":
    test_dns_logging()
