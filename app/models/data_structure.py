from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Range:
    min: int
    max: int

@dataclass
class Item:
    name: str
    range: Optional[Range]

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