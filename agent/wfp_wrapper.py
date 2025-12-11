import ctypes
from ctypes import wintypes
import uuid

# Constants
RPC_C_AUTHN_WINNT = 10
RPC_C_AUTHN_LEVEL_DEFAULT = 0
FWPM_SESSION_FLAG_DYNAMIC = 0x00000001
FWP_IP_VERSION_V4 = 0
FWP_IP_VERSION_V6 = 1
FWP_DIRECTION_OUTBOUND = 0
FWP_DIRECTION_INBOUND = 1

# Load WFP library
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

class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", ctypes.c_ulong),
        ("Data2", ctypes.c_ushort),
        ("Data3", ctypes.c_ushort),
        ("Data4", ctypes.c_ubyte * 8)
    ]

    def __str__(self):
        return f"{{{self.Data1:08x}-{self.Data2:04x}-{self.Data3:04x}-{self.Data4[0]:02x}{self.Data4[1]:02x}-{self.Data4[2]:02x}{self.Data4[3]:02x}{self.Data4[4]:02x}{self.Data4[5]:02x}{self.Data4[6]:02x}{self.Data4[7]:02x}}}"

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

class WfpManager:
    def __init__(self):
        self._engine_handle = HANDLE()
        self._is_open = False

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
                
                connections.append({
                    "id": conn.connectionId,
                    "process_id": conn.processId,
                    "local_port": conn.localPort,
                    "remote_port": conn.remotePort,
                    "direction": "Outbound" if conn.direction == FWP_DIRECTION_OUTBOUND else "Inbound"
                })
                
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
