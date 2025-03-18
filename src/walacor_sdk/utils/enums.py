from enum import Enum


class FieldTypeEnum(str, Enum):
    INTEGER = "INTEGER"
    TEXT = "TEXT"
    DECIMAL = "DECIMAL"
    BOOLEAN = "BOOLEAN"
    DATETIME_EPOCH = "DATETIME(EPOCH)"
    ARRAY = "ARRAY"
    CRON = "CRON"
