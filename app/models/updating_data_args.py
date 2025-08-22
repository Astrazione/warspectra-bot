
from dataclasses import dataclass


@dataclass
class UpdatingDataArgs:
    """
    Класс для хранения аргументов обновления данных.
    """
    discord_id: int
    field_name: str
    value: int
    arr_index: int = -1
