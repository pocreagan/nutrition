from dataclasses import dataclass, field
from typing import Dict

__all__ = [
    'Model',
]

from typing import List


@dataclass
class Model:
    USDA_MISSES_MAX_QTY: int
    USDA_foods_of_interest: List[int] = field(default_factory=list, repr=False)
    nutrients_of_interest: List[str] = field(default_factory=list, repr=False)
    foods: Dict = field(default_factory=dict, repr=False)
