import sys
import os
import time

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.common.database import init_db, SessionLocal
from agent.policy_engine import PolicyEngine

def test_policy_engine():
    print("Testing Policy Engine...")
    
    # 1. Initialize DB
    init_db()
    
    # 2. Setup Engine
    engine = PolicyEngine(cache_ttl=1) # Short TTL for testing
    
    # 3. Test Default (ALLOW)
    path_unknown = "c:\\program files\\unknown_app.exe"
    decision = engine.check_connection(path_unknown)
    print(f"Default Check ({path_unknown}): {decision}")
    
    if decision != "ALLOW":
        print("FAILURE: Default should be ALLOW")
        return

    # 4. Add Block Policy
    path_bad = "c:\\program files\\malware.exe"
    print(f"\nAdding BLOCK policy for {path_bad}...")
    engine.add_policy(path_bad, "BLOCK")
    
    # 5. Test Block
    decision = engine.check_connection(path_bad)
    print(f"Check ({path_bad}): {decision}")
    
    if decision == "BLOCK":
        print("SUCCESS: Policy match confirmed.")
    else:
        print(f"FAILURE: Expected BLOCK, got {decision}")

    # 6. Test Case Insensitivity
    path_bad_upper = "C:\\PROGRAM FILES\\MALWARE.EXE"
    decision = engine.check_connection(path_bad_upper)
    print(f"Check Case-Insensitive ({path_bad_upper}): {decision}")
     
    if decision == "BLOCK":
        print("SUCCESS: Case-insensitivity confirmed.")
    else:
        print(f"FAILURE: Expected BLOCK for uppercase path, got {decision}")

if __name__ == "__main__":
    test_policy_engine()
