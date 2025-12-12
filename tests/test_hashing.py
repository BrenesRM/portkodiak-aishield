import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent.wfp_wrapper import WfpManager

def test_hashing():
    print("Testing Hashing...")
    # Test with current script file
    current_file = __file__
    print(f"Hashing: {current_file}")
    hash_val = WfpManager.calculate_file_hash(current_file)
    print(f"Hash: {hash_val}")
    
    if hash_val and len(hash_val) == 64:
        print("SUCCESS: Hashing returned valid SHA256 string.")
    else:
        print("FAILURE: Hashing failed.")

if __name__ == "__main__":
    test_hashing()
