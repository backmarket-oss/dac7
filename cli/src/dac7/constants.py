from enum import StrEnum


class Env(StrEnum):
    TEST = "TEST"
    PROD = "PROD"


class FileFormat(StrEnum):
    XML = "XML"
    JSON = "JSON"
