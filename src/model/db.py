from typing import Dict
from typing import Type
from typing import Union

from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeMeta

from src.model.enums import FoodSource, NutrientLimitType
from src.model.meta import declarative_base_factory
from src.model.meta import JSONEncodedDict
from src.model.meta import Relationship
from src.model.meta import TableMixin

__all__ = []

Schema: Union[DeclarativeMeta, Type[TableMixin]] = declarative_base_factory('model')

food_to_blob_relationship = Relationship.one_to_one(
    'Food', '_nutrients', 'NutrientData', 'food',
)

region_to_blob_relationship = Relationship.one_to_one(
    'Region', '_nutrients', 'NutrientData', 'region',
)


class Nutrient(Schema):
    """
    Nutrient.id is the key in the NutrientData JSON data
    Nutrient.name is the canonical name for the nutrient
    """
    _repr_fields = ['name']
    name = Column(String(128), nullable=False)
    display_name = Column(String(128), nullable=False)
    display_multiplier = Column(Float, default=1.0)


class HasNutrients:
    _nutrients: 'NutrientData'

    @property
    def nutrients(self) -> Dict[int, Union[NutrientLimitType, float]]:
        return {k: v if isinstance(v, float) else NutrientLimitType[v] for k, v in self._nutrients.data.items()}

    @nutrients.setter
    def nutrients(self, d: Dict[int, float]) -> None:
        self._nutrients = NutrientData(data=d)


class Food(Schema, HasNutrients):
    _repr_fields = ['food_id', 'description', 'source', 'serving_size']
    food_id = Column(String(32), nullable=False, index=True)
    description = Column(String(256), nullable=False)
    source = Column(Enum(FoodSource), nullable=False)
    serving_size = Column(Float, nullable=False)
    _nutrients: 'NutrientData' = food_to_blob_relationship.child


class Region(Schema, HasNutrients):
    _repr_fields = ['name', 'source']
    name = Column(String(64), nullable=False)
    source = Column(String(256), nullable=False)
    _nutrients: 'NutrientData' = region_to_blob_relationship.child


class NutrientData(Schema):
    _repr_fields = []
    data = Column(JSONEncodedDict, nullable=False)
    food_id = Food.id_fk()
    region_id = Region.id_fk()
    food = food_to_blob_relationship.parent
    region = region_to_blob_relationship.parent
