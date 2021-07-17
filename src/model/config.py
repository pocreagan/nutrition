from dataclasses import dataclass, field
from typing import Any
from typing import Dict
from typing import List

__all__ = [
    'Model',
]


@dataclass
class Model:
    USDA_MISSES_MAX_QTY: int
    PERCENT_OF_DAILY_SAFE: float
    USDA_foods_of_interest: List[int] = field(default_factory=list, repr=False)
    nutrients_of_interest: List[str] = field(default_factory=list, repr=False)
    limits_by_region: Dict[str, Any] = field(default_factory=dict, repr=False)
    foods: Dict = field(default_factory=dict, repr=False)
