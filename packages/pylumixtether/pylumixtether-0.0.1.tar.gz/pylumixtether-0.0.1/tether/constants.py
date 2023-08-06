from enum import Enum, auto


class LMX_ERROR_CODE(Enum):
    LMX_DEF_ERR_NO_ERROR = 0x00000000  # No error
    LMX_DEF_ERR_FUNC_PARAM = 0x00010000  # Function Argument Related: Argument error
    LMX_DEF_ERR_FUNC_UNKNOWN = auto()  # Function Argument Related: Other error

    LMX_DEF_ERR_CB_INVALID_ID = 0x00020000 # Callback Related: Invalid ID
    LMX_DEF_ERR_CB_INVALID_FUNC = auto()  # Callback Related: Function invalid
    LMX_DEF_ERR_CB_INVALID_PARAM = auto()  # Callback Related: Illegal parameters
    LMX_DEF_ERR_CB_SAME_ID = auto()  # Callback Related: Registered with the same ID (function is different)
    LMX_DEF_ERR_CB_LIMIT = auto()  # Callback Related: Registration limit
    LMX_DEF_ERR_CB_NOT_FIND = auto()  # Callback Related: Specified ID not found
    LMX_DEF_ERR_CB_UNKNOWN = auto()  # Callback Related: Other error

    LMX_DEF_ERR_DEV_DETECT = 0x00030000  # Device Selection Related: Detection error
    LMX_DEF_ERR_DEV_OPEN = auto()  # Device Selection Related: Selected device open error
    LMX_DEF_ERR_DEV_NEED_OPEN = auto()  # Device Selection Related: Not open or disconnected
    LMX_DEF_ERR_DEV_UNKNOWN = auto()  # Device Selection Related: Other error

    LMX_DEF_ERR_COM_INVALID_PARAM = 0x00040000  # Data Transmission Related: Parameter error
    LMX_DEF_ERR_COM_CMD = auto()  # Data Transmission Related: Command transmission error
    LMX_DEF_ERR_COM_DATA_SEND = auto()  # Data Transmission Related: Data transmission error
    LMX_DEF_ERR_COM_DATA_RCV = auto()  # Data Transmission Related: Data reception error
    LMX_DEF_ERR_COM_DATA_BUSY = auto()
    LMX_DEF_ERR_COM_RES = auto()  # Data Transmission Related: Response error
    LMX_DEF_ERR_COM_MEM_ADD = auto()  # Data Transmission Related: Memory allocation error
    LMX_DEF_ERR_COM_UNKNOWN = auto()  # Data Transmission Related: Other error
    LMX_DEF_ERR_COM_THREAD = auto()  # Data Transmission Related: Thread creation failure error
    LMX_DEF_ERR_COM_TIMEOUT = auto()  # Data Transmission Related: Communication timeout error
    LMX_DEF_ERR_COM_TIMEOUT_RECONNECT_OK = auto()  # Data Transmission Related: Reconnect OK
    LMX_DEF_ERR_COM_TIMEOUT_RECONNECT_ERROR = auto()  # Data Transmission Related: Reconnect ERROR

    LMX_DEF_ERR_COM_SESSION_ALREADY_OPENED = 0x00041000  # Session: ERROR already open
    LMX_DEF_ERR_COM_SESSION_NOT_OPENED = auto()  # Session: Not opened yet
    LMX_DEF_ERR_COM_SESSION_NOT_SUPPORT = auto()  # Session: Not supported: Command
    LMX_DEF_ERR_COM_SESSION_NOT_SUPPORT_VERSION = auto()  # Session: Not supported: Version

    LMX_DEF_ERR_EVENT_RCV_UNKNOWN = 0x00050000  # Event Notification Related: Unexpected event reception error
    LMX_DEF_ERR_EVENT_WAIT_TIMEOUT = auto()  # Event Notification Related: Event wait timeout error

    LMX_DEF_ERR_FILE = 0x00060000  # File System Related: File system general error
    LMX_DEF_ERR_FILE_PATH_LEN = auto()  # File System Related: File path length error
    LMX_DEF_ERR_FILE_OPEN = auto()  # File System Related: File open error
    LMX_DEF_ERR_FILE_SIZE = auto()  # File System Related: File size error
    LMX_DEF_ERR_FILE_READ = auto()  # File System Related: File reading error
    LMX_DEF_ERR_FILE_TYPE_FWUP_UNKNOWN = auto()  # File System Related: File format unknown(FWUP)

    LMX_DEF_ERR_MEM = 0x00070000  # Memory System Related: General error
    LMX_DEF_ERR_MEM_CREATE = auto()  # Memory System Related: Creating error

    LMX_DEF_ERR_INTERNAL = 0x000F0000  # Internal Error:
    LMX_DEF_ERR_INTERNAL_EXCEPTION = auto()  # Internal Error: Exception(Including Windows AV)
    LMX_DEF_ERR_DEV_FWUP_NOTREADY = auto()  # Internal Error: FWUP preparation error(battery shortage etc.)
    LMX_DEF_ERR_DEV_FWUP_ERROR = auto()  # Internal Error: FWUP preparation error(battery shortage etc.)
    LMX_DEF_ERR_DEV_FWUP_ERROR_VERSION = auto()  # Internal Error: FWUP preparation error(firmware up complete: failure: version)

    LMX_DEF_ERR_CAM = 0x00100000  # Camera Command Error:
    LMX_DEF_ERR_CAM_INVALID_MODE = 0x00100001  # Camera Command Error: Invalid mode error

    LMX_DEF_ERR_MAX = 0x00100002  # Error: Other


class LMX_EVENT_ID(Enum):
    LMX_DEF_LIB_EVENT_ID_ISO = 0x02000020  # Event/Callback registration ID:ISO information
    LMX_DEF_LIB_EVENT_ID_SHUTTER = 0x02000030  # Event/Callback registration ID:ShutterSpeed information
    LMX_DEF_LIB_EVENT_ID_APERTURE = 0x02000040  # Event/Callback registration ID:Apertuer information
    LMX_DEF_LIB_EVENT_ID_WHITEBALANCE = 0x02000050  # Event/Callback registration ID:WhiteBalance information
    LMX_DEF_LIB_EVENT_ID_EXPOSURE = 0x02000060  # Event/Callback registration ID:Exposure
    LMX_DEF_LIB_EVENT_ID_AF_CONFIG = 0x02000070  # Event/Callback registration ID:AF mode/AF area

    LMX_DEF_LIB_EVENT_ID_REC_CTRL_RELEASE = 0x03000010  # Event/Callback registration ID:Shooting operation
    LMX_DEF_LIB_TAG_REC_CTRL_RELEASE_ONESHOT = 0x03000011

    LMX_DEF_LIB_EVENT_ID_REC_CTRL_AFAE = 0x03000020  # Event/Callback registration ID:Shooting operation
    LMX_DEF_LIB_EVENT_ID_REC_CTRL_ZOOM = 0x03000080  # Event/Callback registration ID:Shooting operation
    LMX_DEF_LIB_EVENT_ID_REC_CTRL_LENS = 0x03010010  # Event/Callback registration ID:Lens operation

    LMX_DEF_LIB_EVENT_ID_OBJCT_ADD = 0x10000040  # Event/Callback registration ID:Object related notification:Add object

    LMX_DEF_LIB_EVENT_ID_OBJCT_REQ_TRNSFER = 0x10000043  # Event/Callback registration ID:Object related notification:Transfer request


class LMX_OBJECT_FORMAT(Enum):
    LMX_DEF_OBJ_FORMAT_UNKNOWN = 0
    LMX_DEF_OBJ_FORMAT_JPEG = 1
    LMX_DEF_OBJ_FORMAT_RAW = 2
    LMX_DEF_OBJ_FORMAT_FOLDER = 3
    LMX_DEF_OBJ_FORMAT_MOVIE_MOV = 4
    LMX_DEF_OBJ_FORMAT_MOVIE_MP4 = 5
    LMX_DEF_OBJ_FORMAT_HLG = 6
    LMX_DEF_OBJ_FORMAT_MAX = 7
    LMX_DEF_OBJ_CARDLESS_TRNSFER_HDL = 0x12345678


class LMX_ISO_PARAM(Enum):
    LMX_DEF_ISO_UNKNOWN = 0xFFFFFFFD  # ISO Unknown
    LMX_DEF_ISO_I_ISO = 0xFFFFFFFE  # i_ISO
    LMX_DEF_ISO_AUTO = 0xFFFFFFFF  # ISO Auto


RESPONSE_CODES = {
    0x2000: "Undefined",
    0x2001: "OK",
    0x2002: "General Error",
    0x2003: "Session Not Open",
    0x2004: "Invalid TransactionID",
    0x2005: "Operation Not Supported",
    0x2006: "Parameter Not Supported",
    0x2007: "Incomplete Transfer",
    0x2008: "Invalid StorageID",
    0x2009: "Invalid ObjectHandle",
    0x200A: "DeviceProp Not Supported",
    0x200B: "Invalid ObjectFormatCode",
    0x200C: "Store Full",
    0x200D: "Object WriteProtected",
    0x200E: "Store Read-Only",
    0x200F: "Access Denied",
    0x2010: "No Thumbnail Present",
    0x2011: "SelfTest Failed",
    0x2012: "Partial Deletion",
    0x2013: "Store Not Available",
    0x2014: "Specification By Format Unsupported",
    0x2015: "No Valid ObjectInfo",
    0x2016: "Invalid Code Format",
    0x2017: "Unknown Vendor Code",
    0x2018: "Capture Already Terminated",
    0x2019: "Device Busy",
    0x201A: "Invalid ParentObject",
    0x201B: "Invalid DeviceProp Format",
    0x201C: "Invalid DeviceProp Value",
    0x201D: "Invalid Parameter",
    0x201E: "Session Already Open",
    0x201F: "Transaction Cancelled",
    0x2020: "Specification of Destination Unsupported",
    0x0010: "Reserved",
    0x1010: "Vendor-Extended Response Code",
}

CALLBACK_TYPE = {
    0x02000020: ''
}
