import pytest
import sys
import io

def run_tests():
    # Capture stdout/stderr
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    # Backup original
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    
    sys.stdout = stdout_capture
    sys.stderr = stderr_capture
    
    try:
        ret = pytest.main(["tests/unit/test_service.py", "-vv"])
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
    print("Return Code:", ret)
    output = stdout_capture.getvalue()
    print("STDOUT (Filtered) ----------------")
    for line in output.splitlines():
        if "FAILED" in line or "Error" in line or "E " in line or "Traceback" in line:
            print(line)
        # Also print near the end where summary is
        if "short test summary info" in line:
            print(line)
    
    print("STDERR ----------------")
    print(stderr_capture.getvalue())

if __name__ == "__main__":
    run_tests()
