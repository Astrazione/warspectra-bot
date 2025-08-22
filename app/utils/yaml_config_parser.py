import os
from typing import Optional
import yaml
from models.data_structure import DataStructure, Field, Item, Range


class YamlConfigParser:
    @staticmethod
    def parse(config_path: str) -> DataStructure:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"YAML файл не найден: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)

        if data is None:
            raise ValueError("YAML файл пуст")

        if 'fields' not in data:
            raise ValueError("YAML файл должен содержать ключ 'fields'")

        fields_list = []
        
        for field_key, field_data in data['fields'].items():
            items: Optional[list[Item]] = None
            range: Optional[Range] = None

            if 'items' in field_data:
                items = [Item(name=item['name']) for item in field_data['items']]

            if 'range' in field_data:
                if len(field_data['range']) != 2:
                    raise ValueError(f'Диапазон для поля {field_key} указан неверно')

                range = Range(field_data['range'][0], field_data['range'][1])

            field = Field(
                key=field_key,
                name=field_data['name'],
                type=field_data['type'] if 'type' in field_data else None,
                items=items,
                range=range
            )
            fields_list.append(field)
        
        return DataStructure(fields=fields_list)