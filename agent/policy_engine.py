import logging
import threading
import time
import sys
import os

# Adjust path to allow imports from app if running as script from agent dir
if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app.common.database import SessionLocal
    from app.common.models import AppPolicy
except ImportError:
    SessionLocal = None
    AppPolicy = None

logger = logging.getLogger(__name__)

class PolicyEngine:
    def __init__(self, cache_ttl=60):
        self._policies = {} # path -> type
        self._cache_lock = threading.RLock()
        self._last_refresh = 0
        self._ttl = cache_ttl
        self.default_policy = "ALLOW" # Default behavior if no rule matches
        
        # Initial load
        self.refresh_policies()

    def refresh_policies(self):
        """Reloads policies from the database."""
        if not SessionLocal or not AppPolicy:
            return

        try:
            with SessionLocal() as db:
                policies = db.query(AppPolicy).filter(AppPolicy.is_active == True).all()
                
                with self._cache_lock:
                    self._policies.clear()
                    for p in policies:
                        # Normalize path to lower case for case-insensitive matching
                        self._policies[p.process_path.lower()] = p.policy_type
                    self._last_refresh = time.time()
                    
            logger.info(f"Loaded {len(self._policies)} policies.")
        except Exception as e:
            logger.error(f"Failed to refresh policies: {e}")

    def check_connection(self, process_path):
        """
        Checks if the process is allowed to connect.
        Returns: 'ALLOW' or 'BLOCK'
        """
        if not process_path or process_path == "Unknown":
            return self.default_policy

        # Check cache TTL
        if time.time() - self._last_refresh > self._ttl:
            # Trigger refresh (maybe async later, sync for now)
            self.refresh_policies()

        normalized_path = process_path.lower()
        
        with self._cache_lock:
            # Exact Match
            if normalized_path in self._policies:
                return self._policies[normalized_path]
            
            # TODO: Directory matching or regex could go here
            
        return self.default_policy

    def add_policy(self, path, policy_type="BLOCK"):
        """Convenience method to add policy programmatically (mostly for tests/UI hook)."""
        if not SessionLocal:
            return False
            
        try:
            with SessionLocal() as db:
                # Check existing
                existing = db.query(AppPolicy).filter(AppPolicy.process_path == path).first()
                if existing:
                    existing.policy_type = policy_type
                    existing.is_active = True
                else:
                    new_policy = AppPolicy(process_path=path, policy_type=policy_type)
                    db.add(new_policy)
                db.commit()
            
            self.refresh_policies()
            return True
        except Exception as e:
            logger.error(f"Failed to add policy: {e}")
            return False
