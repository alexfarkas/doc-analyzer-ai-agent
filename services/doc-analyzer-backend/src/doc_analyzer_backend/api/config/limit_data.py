from enum import Enum

from pydantic import BaseModel


class LimitThresholdMode(str, Enum):
    ABS_VALUE = "abs_value"
    PERCENT = "percent"


class LimitSettings(BaseModel):
    limit_threshold_mode: str
    limit_warning_threshold: int
    limit_warning_threshold_pc: int
