import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent.wfp_wrapper import DnsResolver

def test_dns_resolver():
    print("Testing DnsResolver...")
    resolver = DnsResolver(cache_ttl=10)
    
    # 1. Test Known IP (Google DNS)
    ip_google = "8.8.8.8"
    print(f"\nResolving {ip_google}...")
    start = time.time()
    hostname = resolver.resolve_ip(ip_google)
    duration = time.time() - start
    print(f"Result: {hostname} (Took {duration:.4f}s)")
    
    # 2. Test Cache Hit
    print(f"\nResolving {ip_google} (Again)...")
    start = time.time()
    hostname_cached = resolver.resolve_ip(ip_google)
    duration = time.time() - start
    print(f"Result: {hostname_cached} (Took {duration:.4f}s)")
    
    if duration < 0.01:
        print("SUCCESS: Cache hit confirmed (very fast).")
    else:
        print("WARNING: Cache might not be working or first call didn't cache?")

    # 3. Test Invalid IP
    ip_invalid = "192.0.2.255" # Test-Net-1, usually won't resolve
    print(f"\nResolving {ip_invalid} (Should fail/timeout)...")
    hostname_invalid = resolver.resolve_ip(ip_invalid)
    print(f"Result: {hostname_invalid}")
    
    resolver.shutdown()

if __name__ == "__main__":
    test_dns_resolver()
