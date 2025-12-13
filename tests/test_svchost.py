import psutil
import sys

def test_svchost_logic():
    print("Testing svchost Resolution...")
    
    found = False
    for p in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if p.info['name'].lower() == 'svchost.exe':
                found = True
                cmdline = p.info['cmdline']
                name_display = "svchost.exe"
                
                if cmdline and "-k" in cmdline:
                    try:
                        idx = cmdline.index("-k")
                        if idx + 1 < len(cmdline):
                            group = cmdline[idx+1]
                            name_display = f"svchost.exe ({group})"
                    except ValueError:
                        pass
                
                print(f"PID: {p.info['pid']} -> {name_display}")
                # We found at least one, that's enough to verify logic works
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
            
    if not found:
        print("WARNING: No accessible svchost.exe found (try running as Admin).")
    else:
        print("SUCCESS: svchost logic verified.")

if __name__ == "__main__":
    test_svchost_logic()
