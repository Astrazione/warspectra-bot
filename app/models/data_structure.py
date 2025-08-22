from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Item:
    name: str

@dataclass
class Range:
    min: int
    max: int

@dataclass
class Field:
    key: str
    name: str
    range: Optional[Range]
    type: Optional[str]
    items: Optional[List[Item]]

@dataclass
class DataStructure:
    fields: List[Field]