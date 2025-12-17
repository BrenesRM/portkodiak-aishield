import ctypes
from ctypes import wintypes
import uuid
import hashlib
import socket
import concurrent.futures
import time
import threading
import sys
import os

# Adjust path to allow imports from app if running as script from agent dir
if __name__ == "__main__":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app.common.database import SessionLocal
    from app.common.models import DnsLog, TrafficSample, Alert
except ImportError:
    # Fallback or mock for standalone testing if app not available
    SessionLocal = None
    DnsLog = None
    TrafficSample = None

from agent.policy_engine import PolicyEngine
from ml.inference_engine import InferenceEngine

class DataCollector:
    """Collects traffic samples and writes to DB in batches."""
    def __init__(self, flush_interval=10, batch_size=50):
        self.queue = []
        self.lock = threading.Lock()
        self.flush_interval = flush_interval
        self.batch_size = batch_size
        self.running = True
        self.thread = threading.Thread(target=self._flush_loop, daemon=True)
        self.thread.start()

    def add_sample(self, info):
        """Adds a connection sample to be logged."""
        if not TrafficSample:
            return
            
        with self.lock:
            self.queue.append(info)
            should_flush = len(self.queue) >= self.batch_size
            
        if should_flush:
            self.flush()

    def flush(self):
        """Writes buffered samples to DB."""
        if not SessionLocal or not TrafficSample:
            return
            
        with self.lock:
            if not self.queue:
                return
            to_write = list(self.queue)
            self.queue.clear()
            
        try:
            with SessionLocal() as db:
                for s in to_write:
                    # Avoid logging our own DB connection traffic if possible to prevent loops?
                    # For now just log everything.
                    sample = TrafficSample(
                        process_name=s.get('process_name', 'Unknown'),
                        process_path=s.get('process_path', 'Unknown'),
                        process_hash=s.get('process_hash'),
                        parent_info=s.get('parent_info'),
                        remote_ip=s.get('remote_ip'),
                        remote_port=s.get('remote_port'),
                        remote_hostname=s.get('remote_hostname'),
                        direction=s.get('direction', 'Outbound'),
                        protocol="TCP" # Placeholder as WFP POC uses Connect layer which is mostly TCP
                    )
                    db.add(sample)
                db.commit()
        except Exception as e:
            # print(f"Logging failed: {e}") # Noise reduction
            pass

    def _flush_loop(self):
        while self.running:
            time.sleep(self.flush_interval)
            self.flush()
            
    def shutdown(self):
        self.running = False
        self.flush()

class DnsResolver:
    def __init__(self, cache_ttl=300):
        self._cache = {} # ip -> (hostname, timestamp)
        self._cache_lock = threading.Lock()
        self._ttl = cache_ttl
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
    
    def resolve_ip(self, ip_address):
        """Resolves IP to hostname using cache and background threads (pseudo-async).
        Note: For immediate results this might block or return None if not cached. 
        For this POC, we will block with timeout (bad for performance) or just return 'Resolving...' logic.
        Actually, we can use a Future, but to keep it simple, let's use a quick blocking call with limited timeout 
        or stick to ThreadPool for bulk if needed. 
        
        Better approach for UI: Return cached if valid. If not, trigger resolution and return ip (or 'Pending').
        """
        if ip_address == "IPv6" or ip_address.startswith("0."):
             return ip_address

        with self._cache_lock:
            if ip_address in self._cache:
                hostname, timestamp = self._cache[ip_address]
                if time.time() - timestamp < self._ttl:
                    return hostname
        
        # Cache miss. 
        # Ideally trigger background resolution.
        # But for this POC let's just do it synchronously but safely? 
        # Synchronous gethostbyaddr can block for seconds.
        # We will submit to executor and wait for a SHORT time.
        
        try:
            future = self._executor.submit(self._do_resolve, ip_address)
            # Wait max 0.1s. If timeout, return IP and let cache update for next time
            hostname = future.result(timeout=0.1)
            return hostname
        except concurrent.futures.TimeoutError:
            return ip_address # Return IP while resolving (future continues in background? No, submit usage here waits)
            # Actually executor.submit returns a Future. calling result waits.
            # If we timeout, the task is still running (thread not killed). 
            # We can't cancel gethostbyaddr easily.
            # Let's just return IP.
        except Exception:
            return ip_address
            
    def _do_resolve(self, ip_address):
        hostname = ip_address
        try:
            hostname, _, _ = socket.gethostbyaddr(ip_address)
            with self._cache_lock:
                self._cache[ip_address] = (hostname, time.time())
        except Exception:
            # Resolution failed, hostname remains ip_address
            with self._cache_lock:
                self._cache[ip_address] = (hostname, time.time())

        # Log result regardless of success/fail
        self._log_resolution(ip_address, hostname)
        return hostname

    def _log_resolution(self, ip, hostname):
        """Logs the resolution to database if available."""
        if SessionLocal and DnsLog:
            try:
                # Use a separate ephemeral session for logging to avoid threading issues
                # Note: Ideally this should also be offloaded to executor if DB is slow
                # but sqlite is fast enough for now or we rely on thread pool being size 5
                with SessionLocal() as db:
                    log = DnsLog(ip_address=ip, hostname=hostname)
                    db.add(log)
                    db.commit()
            except Exception as e:
                # Silent failure to not crash WFP
                pass

    def shutdown(self):
        self._executor.shutdown(wait=False)

# ... (Previous imports)

# ... (Previous constants/classes)

    # ... (existing methods)


RPC_C_AUTHN_WINNT = 10
RPC_C_AUTHN_LEVEL_DEFAULT = 0
FWPM_SESSION_FLAG_DYNAMIC = 0x00000001
FWP_IP_VERSION_V4 = 0
FWP_IP_VERSION_V6 = 1
FWP_DIRECTION_OUTBOUND = 0
FWP_DIRECTION_INBOUND = 1

# GUIDs
class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", ctypes.c_ulong),
        ("Data2", ctypes.c_ushort),
        ("Data3", ctypes.c_ushort),
        ("Data4", ctypes.c_ubyte * 8)
    ]

    def __str__(self):
        return f"{{{self.Data1:08x}-{self.Data2:04x}-{self.Data3:04x}-{self.Data4[0]:02x}{self.Data4[1]:02x}-{self.Data4[2]:02x}{self.Data4[3]:02x}{self.Data4[4]:02x}{self.Data4[5]:02x}{self.Data4[6]:02x}{self.Data4[7]:02x}}}"

def DEFINE_GUID(l, w1, w2, b1, b2, b3, b4, b5, b6, b7, b8):
    return GUID(l, w1, w2, (ctypes.c_ubyte * 8)(b1, b2, b3, b4, b5, b6, b7, b8))

FWPM_LAYER_ALE_AUTH_CONNECT_V4 = DEFINE_GUID(0xc38d57d1, 0x1317, 0x4076, 0x97, 0xca, 0xd5, 0x14, 0xc7, 0xc5, 0x85, 0x96)
FWPM_CONDITION_IP_REMOTE_PORT = DEFINE_GUID(0x0c1ba1af, 0x5765, 0x453f, 0xaf, 0x22, 0xa8, 0xf7, 0x91, 0xac, 0x77, 0x5b)

# Match Types
FWP_MATCH_EQUAL = 0

# Data Types
FWP_UINT16 = 2
FWP_UINT64 = 4

# Action Types
FWP_ACTION_BLOCK = 0x00001001 # (0x00000001 | 0x00001000)
FWP_ACTION_PERMIT = 0x00001002

class FWP_VALUE0(ctypes.Structure):
    class _U(ctypes.Union):
        _fields_ = [
             ("uint16", ctypes.c_ushort),
             ("uint32", ctypes.c_uint32),
             ("uint64", ctypes.c_uint64),
        ]
    _fields_ = [
        ("type", ctypes.c_int), # FWP_DATA_TYPE
        ("u", _U) # union
    ]

class FWPM_FILTER_CONDITION0(ctypes.Structure):
    _fields_ = [
        ("fieldKey", GUID),
        ("matchType", ctypes.c_int), # FWP_MATCH_TYPE
        ("conditionValue", FWP_VALUE0)
    ]

class FWPM_ACTION0(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_uint32), # FWP_ACTION_TYPE
        ("filterType", GUID)
    ]

try:
    fwpuclnt = ctypes.windll.fwpuclnt
except AttributeError:
    raise ImportError("fwpuclnt.dll not found. This code must run on Windows.")

# Types
UINT32 = ctypes.c_uint32
UINT64 = ctypes.c_uint64
UINT8 = ctypes.c_uint8
HANDLE = wintypes.HANDLE
LPWSTR = wintypes.LPWSTR


class FWPM_DISPLAY_DATA0(ctypes.Structure):
    _fields_ = [
        ("name", LPWSTR),
        ("description", LPWSTR)
    ]

class FWPM_SESSION0(ctypes.Structure):
    _fields_ = [
        ("sessionKey", GUID),
        ("displayData", FWPM_DISPLAY_DATA0),
        ("flags", UINT32),
        ("txnWaitTimeoutInMSec", UINT32),
        ("processId", UINT32),
        ("sid", ctypes.c_void_p),
        ("username", LPWSTR),
        ("kernelMode", wintypes.BOOL)
    ]

class FWPM_FILTER0(ctypes.Structure):
    # Partial definition for enumeration
    _fields_ = [
        ("filterKey", GUID),
        ("displayData", FWPM_DISPLAY_DATA0),
        ("flags", UINT32),
        ("providerKey", ctypes.POINTER(GUID)),
        ("providerData", ctypes.c_void_p), # FWP_BYTE_BLOB
        ("layerKey", GUID),
        ("subLayerKey", GUID),
        ("weight", ctypes.c_void_p), # FWP_VALUE0 (union)
        ("numFilterConditions", UINT32),
        ("filterCondition", ctypes.c_void_p), # FWPM_FILTER_CONDITION0*
        ("action", ctypes.c_void_p), # FWPM_ACTION0
        ("context", UINT64), # union
        ("reserved", ctypes.c_void_p), # GUID*
        ("filterId", UINT64),
        ("effectiveWeight", ctypes.c_void_p) # FWP_VALUE0 (union)
    ]

class FWPM_CONNECTION0(ctypes.Structure):
    class _U1(ctypes.Union):
        _fields_ = [("localV4Address", UINT32), ("localV6Address", UINT8 * 16)]
    class _U2(ctypes.Union):
        _fields_ = [("remoteV4Address", UINT32), ("remoteV6Address", UINT8 * 16)]
        
    _anonymous_ = ("_u1", "_u2")
    _fields_ = [
        ("connectionId", UINT64),
        ("ipVersion", ctypes.c_int), # FWP_IP_VERSION enum
        ("_u1", _U1),
        ("_u2", _U2),
        ("localPort", ctypes.c_ushort),
        ("remotePort", ctypes.c_ushort),
        ("direction", ctypes.c_int), # FWP_DIRECTION enum
        ("processId", UINT64),
        ("startTime", UINT64), # Approx
    ]

# Function Prototypes
fwpuclnt.FwpmEngineOpen0.argtypes = [
    LPWSTR,
    UINT32,
    ctypes.c_void_p,
    ctypes.POINTER(FWPM_SESSION0),
    ctypes.POINTER(HANDLE)
]
fwpuclnt.FwpmEngineOpen0.restype = UINT32

fwpuclnt.FwpmEngineClose0.argtypes = [HANDLE]
fwpuclnt.FwpmEngineClose0.restype = UINT32

fwpuclnt.FwpmFilterCreateEnumHandle0.argtypes = [
    HANDLE,
    ctypes.c_void_p, # const FWPM_FILTER_ENUM_TEMPLATE0*
    ctypes.POINTER(HANDLE)
]
fwpuclnt.FwpmFilterCreateEnumHandle0.restype = UINT32

fwpuclnt.FwpmFilterEnum0.argtypes = [
    HANDLE,
    HANDLE,
    UINT32,
    ctypes.POINTER(ctypes.POINTER(ctypes.POINTER(FWPM_FILTER0))),
    ctypes.POINTER(UINT32)
]
fwpuclnt.FwpmFilterEnum0.restype = UINT32

fwpuclnt.FwpmFilterDestroyEnumHandle0.argtypes = [HANDLE, HANDLE]
fwpuclnt.FwpmFilterDestroyEnumHandle0.restype = UINT32

fwpuclnt.FwpmFreeMemory0.argtypes = [ctypes.c_void_p]
fwpuclnt.FwpmFreeMemory0.restype = None

fwpuclnt.FwpmConnectionCreateEnumHandle0.argtypes = [
    HANDLE,
    ctypes.c_void_p,
    ctypes.POINTER(HANDLE)
]
fwpuclnt.FwpmConnectionCreateEnumHandle0.restype = UINT32

fwpuclnt.FwpmConnectionEnum0.argtypes = [
    HANDLE,
    HANDLE,
    UINT32,
    ctypes.POINTER(ctypes.POINTER(ctypes.POINTER(FWPM_CONNECTION0))),
    ctypes.POINTER(UINT32)
]
fwpuclnt.FwpmConnectionEnum0.restype = UINT32

fwpuclnt.FwpmConnectionDestroyEnumHandle0.argtypes = [HANDLE, HANDLE]
fwpuclnt.FwpmConnectionDestroyEnumHandle0.restype = UINT32

fwpuclnt.FwpmFilterAdd0.argtypes = [
    HANDLE,
    ctypes.POINTER(FWPM_FILTER0),
    ctypes.c_void_p, # SECURITY_DESCRIPTOR
    ctypes.POINTER(UINT64) # id
]
fwpuclnt.FwpmFilterAdd0.restype = UINT32

fwpuclnt.FwpmFilterDeleteById0.argtypes = [
    HANDLE,
    UINT64
]
fwpuclnt.FwpmFilterDeleteById0.restype = UINT32

class WfpManager:
    def __init__(self):
        self._engine_handle = HANDLE()
        self._is_open = False
        self.dns_resolver = DnsResolver()
        self.policy_engine = PolicyEngine()
        self.collector = DataCollector()
        self.inference_engine = InferenceEngine()
        self.recent_alerts = {} # (path, ip, port) -> timestamp

    def get_filter_id_list(self):
        # Helper usually needed
        return []
    
    @staticmethod
    def calculate_file_hash(filepath):
        """Calculates SHA256 hash of a file."""
        if not filepath or filepath == "Unknown":
            return None
            
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                # Read and update hash string value in blocks of 4K
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except (PermissionError, FileNotFoundError, OSError):
            return "Unverified (Access Denied)"

    # ... (existing methods remain, inserting new ones)

    def add_block_rule(self, remote_port, name="Block Rule"):
        """Adds a blocking rule for a specific remote port."""
        if not self._is_open:
            raise RuntimeError("Session not open")

        # 1. Prepare Condition
        cond = FWPM_FILTER_CONDITION0()
        cond.fieldKey = FWPM_CONDITION_IP_REMOTE_PORT
        cond.matchType = FWP_MATCH_EQUAL
        cond.conditionValue.type = FWP_UINT16
        cond.conditionValue.u.uint16 = remote_port

        # 2. Prepare Filter
        filter_struct = FWPM_FILTER0()
        filter_struct.displayData.name = name
        filter_struct.displayData.description = f"Blocks remote port {remote_port}"
        filter_struct.flags = 0
        filter_struct.layerKey = FWPM_LAYER_ALE_AUTH_CONNECT_V4
        filter_struct.action.type = FWP_ACTION_BLOCK
        filter_struct.weight.type = FWP_UINT64 
        filter_struct.weight.u.uint64 = 0xFFFFFFFFFFFFFFFF # Max weight (approx) -> EMPTY (let WFP assign? No, use Empty if FWP_EMPTY)
        # Actually for FWP_EMPTY type is 0 or FWP_EMPTY (0). CTypes defaults to 0.
        # But for effective blocking we might want a high weight. 
        # Let's try letting system assign (weight.type = FWP_EMPTY = 0).
        
        filter_struct.numFilterConditions = 1
        filter_struct.filterCondition = ctypes.cast(ctypes.byref(cond), ctypes.c_void_p)

        filter_id = UINT64()
        
        res = fwpuclnt.FwpmFilterAdd0(
            self._engine_handle,
            ctypes.byref(filter_struct),
            None,
            ctypes.byref(filter_id)
        )
        
        if res != 0:
            raise WindowsError(f"FwpmFilterAdd0 failed with error: {res}")
            
        return filter_id.value

    def delete_rule(self, filter_id):
        """Deletes a filter by ID."""
        if not self._is_open:
            raise RuntimeError("Session not open")
            
        res = fwpuclnt.FwpmFilterDeleteById0(
            self._engine_handle,
            filter_id
        )
        if res != 0:
            raise WindowsError(f"FwpmFilterDeleteById0 failed with error: {res}")


    def open_session(self):
        """Opens a session to the Filter Engine."""
        session = FWPM_SESSION0()
        session.flags = FWPM_SESSION_FLAG_DYNAMIC
        session.txnWaitTimeoutInMSec = 0
        session.processId = 0
        session.sid = None
        session.username = None
        session.kernelMode = False
        
        # Add basic display data
        display_data = FWPM_DISPLAY_DATA0()
        display_data.name = "PortKodiakAI Shield"
        display_data.description = "WFP Session for AI Shield"
        session.displayData = display_data

        res = fwpuclnt.FwpmEngineOpen0(
            None,
            RPC_C_AUTHN_WINNT,
            None,
            ctypes.byref(session),
            ctypes.byref(self._engine_handle)
        )
        
        if res != 0:
            raise WindowsError(f"FwpmEngineOpen0 failed with error: {res}")
            
        self._is_open = True
        return True

    def close_session(self):
        """Closes the session."""
        if self._is_open:
            fwpuclnt.FwpmEngineClose0(self._engine_handle)
            self._is_open = False

    def get_filters(self):
        """Enumerates all filters."""
        if not self._is_open:
            raise RuntimeError("Session not open")

        enum_handle = HANDLE()
        res = fwpuclnt.FwpmFilterCreateEnumHandle0(
            self._engine_handle,
            None,
            ctypes.byref(enum_handle)
        )
        if res != 0:
             raise WindowsError(f"FwpmFilterCreateEnumHandle0 failed with error: {res}")

        filters_ptr = ctypes.POINTER(ctypes.POINTER(FWPM_FILTER0))()
        num_filters_returned = UINT32()
        
        # Enumerate in batches
        filters = []
        try:
            # Just get the first batch for POC
            res = fwpuclnt.FwpmFilterEnum0(
                self._engine_handle,
                enum_handle,
                100, # Request up to 100
                ctypes.byref(filters_ptr),
                ctypes.byref(num_filters_returned)
            )
            
            if res != 0:
                 raise WindowsError(f"FwpmFilterEnum0 failed with error: {res}")
            
            count = num_filters_returned.value
            for i in range(count):
                flt = filters_ptr[i].contents
                filters.append({
                    "id": flt.filterId,
                    "name": flt.displayData.name,
                    "description": flt.displayData.description
                })
                
            # Free memory provided by WFP
            if filters_ptr:
                 fwpuclnt.FwpmFreeMemory0(ctypes.cast(filters_ptr, ctypes.c_void_p))
                 
        finally:
            fwpuclnt.FwpmFilterDestroyEnumHandle0(self._engine_handle, enum_handle)
            
        return filters

    def get_connections(self):
        """Enumerates active connections."""
        if not self._is_open:
            raise RuntimeError("Session not open")

        enum_handle = HANDLE()
        res = fwpuclnt.FwpmConnectionCreateEnumHandle0(
            self._engine_handle,
            None,
            ctypes.byref(enum_handle)
        )
        if res != 0:
             raise WindowsError(f"FwpmConnectionCreateEnumHandle0 failed with error: {res}")

        conns_ptr = ctypes.POINTER(ctypes.POINTER(FWPM_CONNECTION0))()
        num_conns_returned = UINT32()
        
        connections = []
        try:
            res = fwpuclnt.FwpmConnectionEnum0(
                self._engine_handle,
                enum_handle,
                100,
                ctypes.byref(conns_ptr),
                ctypes.byref(num_conns_returned)
            )
            
            if res != 0:
                 raise WindowsError(f"FwpmConnectionEnum0 failed with error: {res}")
            
            count = num_conns_returned.value
            for i in range(count):
                conn = conns_ptr[i].contents
                
                # Basic parsing
                local_ip = "IPv6" if conn.ipVersion == FWP_IP_VERSION_V6 else str(conn.localV4Address) # Needs proper formatting
                remote_ip = "IPv6" if conn.ipVersion == FWP_IP_VERSION_V6 else str(conn.remoteV4Address)
                
                # Process Resolution
                process_name = "Unknown"
                process_path = "Unknown"
                parent_info = "Unknown"
                try:
                    p = psutil.Process(conn.processId)
                    process_name = p.name()
                    process_path = p.exe()
                    
                    # Special Case: svchost.exe service group
                    if process_name.lower() == "svchost.exe":
                        try:
                            cmdline = p.cmdline()
                            # Look for -k argument
                            if "-k" in cmdline:
                                idx = cmdline.index("-k")
                                if idx + 1 < len(cmdline):
                                    group = cmdline[idx+1]
                                    process_name = f"{process_name} ({group})"
                        except (psutil.AccessDenied, IndexError):
                            pass

                    # Parent Resolution
                    parent = p.parent()
                    if parent:
                        parent_info = f"{parent.name()} (PID: {parent.pid})"
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass

                process_hash = self.calculate_file_hash(process_path)
                
                # DNS Resolution
                remote_hostname = self.dns_resolver.resolve_ip(remote_ip)

                # Policy Check
                policy_action = self.policy_engine.check_connection(process_path)
                
                # Inference (ML)
                ml_score, ml_label = self.inference_engine.predict({
                    "remote_port": conn.remotePort,
                    "process_name": process_name,
                    "process_path": process_path,
                    "direction": "Outbound" if conn.direction == FWP_DIRECTION_OUTBOUND else "Inbound"
                })
                
                # Alert Generation
                if ml_label == "Anomaly" and Alert and SessionLocal:
                    try:
                        alert_key = (process_path, remote_ip, conn.remotePort)
                        now = time.time()
                        last_alert = self.recent_alerts.get(alert_key, 0)
                        
                        if now - last_alert > 60: # 60s cooldown
                            with SessionLocal() as db:
                                alert = Alert(
                                    process_name=process_name,
                                    process_path=process_path,
                                    remote_ip=remote_ip,
                                    remote_port=conn.remotePort,
                                    risk_score=ml_score,
                                    status="New"
                                )
                                db.add(alert)
                                db.commit()
                            self.recent_alerts[alert_key] = now
                    except Exception as e:
                        # print(f"Alert creation failed: {e}")
                        pass

                info = {
                    "id": conn.connectionId,
                    "process_id": conn.processId,
                    "process_name": process_name,
                    "process_path": process_path,
                    "process_hash": process_hash,
                    "parent_info": parent_info,
                    "local_port": conn.localPort,
                    "remote_port": conn.remotePort,
                    "remote_ip": remote_ip,
                    "remote_hostname": remote_hostname,
                    "direction": "Outbound" if conn.direction == FWP_DIRECTION_OUTBOUND else "Inbound",
                    "policy_action": policy_action,
                    "ml_score": ml_score,
                    "ml_label": ml_label
                }

                connections.append(info)
                
                # Collect for ML Training
                self.collector.add_sample(info)
                
            if conns_ptr:
                 fwpuclnt.FwpmFreeMemory0(ctypes.cast(conns_ptr, ctypes.c_void_p))
                 
        finally:
            fwpuclnt.FwpmConnectionDestroyEnumHandle0(self._engine_handle, enum_handle)
            
        return connections

    def __enter__(self):
        self.open_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_session()
