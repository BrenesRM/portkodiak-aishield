import sys
import os
import psutil

# Simple standalone test for parent resolution logic used in wfp_wrapper.py
def test_parent_tracking():
    print("Testing Parent Resolution...")
    
    current_pid = os.getpid()
    print(f"Current PID: {current_pid}")
    
    try:
        p = psutil.Process(current_pid)
        print(f"Current Process: {p.name()}")
        
        parent = p.parent()
        if parent:
            print(f"SUCCESS: Parent Resolved: {parent.name()} (PID: {parent.pid})")
        else:
            print("WARNING: No parent found (orphaned?).")
            
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    test_parent_tracking()
