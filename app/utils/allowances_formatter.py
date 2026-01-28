import re
from typing import Dict
from app.config.settings import settings
from app.models.data_structure import Field


class AllowancesFormatter:
    @staticmethod
    def get_allowances_str(player_info: Dict[str, str]):
        displayed_allowances = ["pCYP", "pBTV", "pRP", "pKMB", "pBoss", "pSkill", "pAdmin"]
        return "\n".join([AllowancesFormatter.get_allowance_type_str(allowance_type, player_info) for allowance_type in displayed_allowances])
        
    @staticmethod
    def get_allowance_type_str(allowance_type: str, player_info: Dict[str, str]) -> str:
        allowance_field: Field

        for field in settings.data_structure.fields:
            if field.key == allowance_type:
                allowance_field = field
                break
        
        allowances_arr = player_info[allowance_type]
        allowances = re.sub(r"[\[\] ]", '', allowances_arr).split(',')
        allowance_names = ", ".join([allowance_field.items[allowance_index] for allowance_index in range(len(allowances)) if allowances[allowance_index] == "1"]) # type: ignore

        return f"{allowance_field.name}({allowance_type}): {allowance_names}" # type: ignore