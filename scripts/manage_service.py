"""
Script to manage the PortKodiakAIShield Windows Service.
Handles installation, removal, starting, stopping, and status checks.
Ensures actions are performed with Administrator privileges.
"""

import sys
import os
import ctypes
import subprocess
import argparse
from pathlib import Path

def is_admin():
    """Check if the script is running with Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Re-launch the script with Administrator privileges."""
    # Get the Python executable and script path
    python_exe = sys.executable
    script = os.path.abspath(sys.argv[0])
    params = " ".join([script] + sys.argv[1:])
    
    # Execute with "runas" verb to request elevation
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", python_exe, params, None, 1
    )

def get_service_script_path():
    """Get the absolute path to the service script."""
    # This assumes the script is run from project root or scripts/ dir
    # We want to point to app/service/main.py
    # But wait, pywin32 service installation usually expects a physical .py file path to register correctly
    
    # More robust: find the package location
    # Since we are using uv/virtualenv, the python interpreter used to run this script 
    # should be the one in .venv/Scripts/python.exe (if run correctly).
    
    # We will invoke pywin32 service logic via: python -m app.service.main [cmd]
    # But for 'install', pywin32 requires the path to the script class file.
    
    # Let's try to resolve it from this script's location
    # scripts/manage_service.py -> ../app/service/main.py
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent
    service_script = project_root / "app" / "service" / "main.py"
    
    if not service_script.exists():
        print(f"Error: Could not find service script at {service_script}")
        sys.exit(1)
        
    return str(service_script)

def manage_service(action):
    """Execute the service management action."""
    service_script = get_service_script_path()
    python_exe = sys.executable
    
    # Arguments for the service script
    cmd = [python_exe, service_script]
    
    if action == "install":
        # Startup auto means automatic startup
        cmd.extend(["install", "--startup", "auto"])
        print("Installing service...")
    elif action == "remove":
        cmd.append("remove")
        print("Removing service...")
    elif action == "start":
        cmd.append("start")
        print("Starting service...")
    elif action == "stop":
        cmd.append("stop")
        print("Stopping service...")
    elif action == "status":
        # pywin32 service framework doesn't have a simple 'status' command 
        # handled by HandleCommandLine essentially directly.
        # usually 'debug' runs it inline
        print("Checking status via sc query...")
        subprocess.run(["sc", "query", "PortKodiakAIShield"], shell=True)
        return
    elif action == "debug":
        cmd.append("debug")
        print("Running service in debug mode (Ctrl+C to stop)...")
    else:
        print(f"Unknown action: {action}")
        return

    # Execute the command
    try:
        subprocess.check_call(cmd)
        print(f"Action '{action}' completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during '{action}': {e}")
        # Don't exit here, let the user interpret the error
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Manage PortKodiakAIShield Service")
    parser.add_argument(
        "action", 
        choices=["install", "remove", "start", "stop", "status", "debug"],
        help="Action to perform"
    )
    args = parser.parse_args()
    
    if not is_admin():
        print("Requesting Administrator privileges...")
        run_as_admin()
        return

    # Ensure we are identifying the correct service script before running
    # Also good to be in project root for imports to work nicely if PYTHONPATH matches
    project_root = Path(__file__).resolve().parent.parent
    os.chdir(project_root)
    # Add project root to sys.path so app module can be found by the spawned python process
    # Actually, spawning 'python app/service/main.py' adds app/service/ to path, not root.
    # So we need to ensure PYTHONPATH includes project root.
    os.environ["PYTHONPATH"] = str(project_root) + os.pathsep + os.environ.get("PYTHONPATH", "")

    manage_service(args.action)

if __name__ == "__main__":
    main()
