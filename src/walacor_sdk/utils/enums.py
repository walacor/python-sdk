from enum import Enum


class FieldType(str, Enum):
    """Field Type Enum"""

    INTEGER = "INTEGER"
    TEXT = "TEXT"
    DECIMAL = "DECIMAL"
    BOOLEAN = "BOOLEAN"
    DATETIME_EPOCH = "DATETIME(EPOCH)"
    ARRAY = "ARRAY"
    CRON = "CRON"


class RequestType(str, Enum):
    """"""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class SystemEnvelopeType(int, Enum):
    OrgId = 5
    User = 10
    UserAddress = 11
    Role = 15
    UserRole = 16
    StorageLocation = 40
    ScheduleJobs = 41
    HashingSignature = 42
    Schema = 50
    BPMAction = 51
    BPMCode = 100
    BMPApproval = 105
    BPMCodeShare = 11
