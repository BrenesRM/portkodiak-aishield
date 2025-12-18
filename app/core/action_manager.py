import logging
import psutil
import threading
from typing import Optional
from app.common.models import Alert
from app.common.database import SessionLocal

logger = logging.getLogger(__name__)

class ActionManager:
    """
    Manages mitigation actions for detected anomalies.
    Interacts with WFP Agent for network blocking and OS for process termination.
    """
    def __init__(self, wfp_agent=None):
        self.wfp_agent = wfp_agent # Reference to WfpManager instance

    def set_agent(self, agent):
        """Sets the WFP agent instance if not provided at init."""
        self.wfp_agent = agent

    def start_polling(self, interval=5):
        """Starts a background thread to poll for pending actions."""
        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, args=(interval,), daemon=True)
        self.thread.start()

    def _poll_loop(self, interval):
        while self.running:
            self.process_queue()
            import time
            time.sleep(interval)

    def process_queue(self):
        """Checks DB for pending actions and executes them."""
        if not SessionLocal:
            return

        try:
            with SessionLocal() as db:
                # Find alerts with PENDING status
                pending_alerts = db.query(Alert).filter(Alert.status.like("PENDING_%")).all()
                
                for alert in pending_alerts:
                    success = False
                    msg = "Failed"
                    
                    if alert.status == "PENDING_BLOCK":
                        success, msg = self.block_connection(alert.id, alert.remote_ip, alert.remote_port)
                    elif alert.status == "PENDING_KILL":
                        success, msg = self.terminate_process(alert.id, alert.process_path)
                    
                    # Update status if action attempted
                    if not success:
                         # Update to FAILED only if logic ran
                         # (block_connection returns False if agent unavailable)
                         alert.status = "FAILED"
                         alert.action_taken = msg
                         logger.warning(f"Action failed for Alert {alert.id}: {msg}")
                    else:
                        # block_connection already updates DB to 'Actioned'
                        # But we should ensure consistency if it didn't commit yet or if we reused session
                        # Actually block_connection uses its OWN session. 
                        # This might cause a race or DetachedInstanceError if we try to modify 'alert' here.
                        # Since 'alert' is attached to 'db' session here, let's refresh or rely on block_connection.
                        pass
                        
                # Commit any failed status updates
                db.commit()
        except Exception as e:
            logger.error(f"Action Queue processing failed: {e}")

    def block_connection(self, alert_id: int, remote_ip: str, remote_port: int):
        """
        Blocks traffic to the specified remote port (and potentially IP in future).
        Updates the Alert status in the database.
        """
        if not self.wfp_agent:
            logger.error("WFP Agent not available for blocking.")
            return False, "Agent unavailable"

        try:
            # 1. Apply Block Rule via WFP
            rule_id = self.wfp_agent.add_block_rule(remote_port, name=f"AutoBlock Alert {alert_id}")
            logger.info(f"Blocked port {remote_port} for Alert {alert_id}. Rule ID: {rule_id}")

            # 2. Update Alert in DB - We do this in a separate session inside _update_alert_status
            # BUT: If called from process_queue, we might want to use the passed DB session provided by context?
            # To allow standalone usage, we keep internal session.
            self._update_alert_status(alert_id, "BLOCKED", f"Blocked Port {remote_port}")
            return True, f"Blocked Port {remote_port}"

        except Exception as e:
            logger.error(f"Failed to block connection: {e}")
            return False, str(e)

    def terminate_process(self, alert_id: int, process_path: str):
        """
        Terminates the process associated with the alert.
        """
        try:
            killed = False
            for proc in psutil.process_iter(['pid', 'exe']):
                try:
                    if proc.info['exe'] == process_path:
                        proc.kill()
                        killed = True
                        logger.info(f"Killed process {proc.info['pid']} ({process_path})")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if killed:
                self._update_alert_status(alert_id, "KILLED", "Process Terminated")
                return True, "Process Terminated"
            else:
                return False, "Process not found"

        except Exception as e:
            logger.error(f"Failed to terminate process: {e}")
            return False, str(e)

    def _update_alert_status(self, alert_id: int, status: str, action: str):
        """Updates the alert record in the database."""
        if not SessionLocal:
            return

        try:
            with SessionLocal() as db:
                alert = db.query(Alert).filter(Alert.id == alert_id).first()
                if alert:
                    alert.status = status
                    alert.action_taken = action
                    db.commit()
        except Exception as e:
            logger.error(f"Failed to update alert status: {e}")
