import logging
import os
from typing import Optional

from app.models.player_ranks import PlayerRanks
from models.data_structure import DataStructure
from utils.yaml_config_parser import YamlConfigParser

class Settings:
    def __init__(self):
        self.db_host = self.get_env_variable('DB_HOST', 'localhost')
        self.db_port = int(self.get_env_variable('DB_PORT', '3306'))
        self.db_user = self.get_env_variable('DB_USER', 'user')
        self.db_password = self.get_env_variable('DB_PASSWORD', 'password')
        self.db_name = self.get_env_variable('DB_NAME', 'warspectra')
        self.data_structure: DataStructure = YamlConfigParser.parse('./app/config/data_structure.yaml')
        self.discord_bot_token = self.get_env_variable('DISCORD_BOT_TOKEN')
        self.player_ranks = PlayerRanks()

    @staticmethod
    def get_env_variable(var_name: str, default: Optional[str] = None) -> str:
        """Получить переменную окружения или значение по умолчанию."""
        env_var: Optional[str] = os.getenv(var_name)
        
        if env_var:
            return env_var
        
        if default:
            logging.warning(f"Переменная окружения {var_name} не установлена, используется значение по умолчанию: {default}")
            return default

        env_error_message = f"Не установлена переменная окружения: {var_name}"
        logging.error(env_error_message)
        raise EnvironmentError(env_error_message)
    
    
settings = Settings()