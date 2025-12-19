import socket
import time
import argparse
import random
import threading
import sys

def connect_target(ip, port, timeout=1):
    """Attempts to connect to a target IP/Port."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((ip, port))
        s.send(b"HEAD / HTTP/1.1\r\nHost: example.com\r\n\r\n")
        s.recv(1024)
        s.close()
        return True, "Connected"
    except Exception as e:
        return False, str(e)

def simulate_normal():
    """Simulates normal web browsing traffic."""
    print("[*] Simulating Normal Traffic...")
    # Common HTTP/HTTPS ports
    targets = [
        ("8.8.8.8", 53),
        ("1.1.1.1", 53),
        ("142.250.190.46", 80), # Google
    ]
    
    for ip, port in targets:
        success, msg = connect_target(ip, port)
        print(f" -> {ip}:{port} - {msg}")
        time.sleep(random.uniform(0.5, 2.0))

def simulate_anomaly(target_ip="127.0.0.1"):
    """Simulates a port scan (Anomaly)."""
    print(f"[*] Simulating Anomaly (Port Scan) on {target_ip}...")
    
    # Rapidly connect to range of ports
    ports = [80, 443, 8080, 22, 21, 23, 3389, 445, 139, 135]
    
    for port in ports:
        print(f" -> Scanning {target_ip}:{port}")
        # Use a short timeout to fail fast
        connect_target(target_ip, port, timeout=0.1)
        # Very short sleep to mimic automated scan
        time.sleep(0.05) 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PortKodiak Traffic Simulator")
    parser.add_argument("--type", choices=["normal", "anomaly"], required=True, help="Type of traffic to generate")
    parser.add_argument("--target", default="127.0.0.1", help="Target IP for anomaly test")
    
    args = parser.parse_args()
    
    if args.type == "normal":
        simulate_normal()
    elif args.type == "anomaly":
        simulate_anomaly(args.target)
