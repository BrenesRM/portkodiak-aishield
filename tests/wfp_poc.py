import sys
import os
import ctypes

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent.wfp_wrapper import WfpManager

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def test_wfp_connection():
    print("Testing WFP Connection...")
    
    if not is_admin():
        print("WARNING: Not running as Administrator. WFP calls will likely fail.")
        
    try:
        with WfpManager() as wfp:
            print("Successfully opened WFP engine session.")
            
            print("Enumerating filters...")
            filters = wfp.get_filters()
            print(f"Retrieved {len(filters)} filters.")
            
            if filters:
                print("\nSample filters:")
                for i, f in enumerate(filters[:5]):
                    print(f"  {i+1}. [{f['id']}] {f['name']}")

            print("\nEnumerating active connections...")
            try:
                connections = wfp.get_connections()
                print(f"Retrieved {len(connections)} connections.")
                
                if connections:
                    print("\nSample connections:")
                    for i, c in enumerate(connections[:5]):
                        print(f"  {i+1}. [{c['process_name']}] (PID: {c['process_id']}) | {c['direction']} | {c['local_port']} -> {c['remote_port']}")
            except Exception as e:
                print(f"Connection enumeration failed: {e}")

            if is_admin():
                print("\nTesting Block Rule...")
                try:
                    port_to_block = 8888
                    print(f"Adding rule to block remote port {port_to_block}...")
                    rule_id = wfp.add_block_rule(port_to_block, "Test Block Rule")
                    print(f"Rule added with ID: {rule_id}")
                    
                    # Verify
                    print("Verifying rule existence...")
                    filters_after = wfp.get_filters()
                    found = False
                    for f in filters_after:
                        if f['id'] == rule_id:
                            print(f"Confirmed: Rule {rule_id} exists ({f['name']}).")
                            found = True
                            break
                    if not found:
                        print(f"ERROR: Rule {rule_id} not found in enumeration!")

                    # Cleanup
                    print(f"Deleting rule {rule_id}...")
                    wfp.delete_rule(rule_id)
                    print("Rule deleted successfully.")
                    
                except Exception as e:
                    print(f"Block rule test failed: {e}")
            else:
                 print("\nSkipping Block Rule test (Requires Administrator privileges).")


                    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_wfp_connection()
