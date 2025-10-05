import logging
import aiomysql
from typing import Optional, Dict

from config.settings import settings


class DataService:
    def __init__(self, pool: aiomysql.Pool):
        self.pool = pool

    @classmethod
    async def create(cls, host: str, port: int, user: str, password: str, db: str):
        pool = await aiomysql.create_pool(
            host=host,
            port=port,
            user=user,
            password=password,
            db=db,
            autocommit=True
        )
        return cls(pool)

    async def is_operator(self, discord_id: int) -> bool:
        """Проверяет, есть ли discord_id в таблице operators"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1 FROM operators WHERE discord_id = %s", (discord_id,))
                return await cur.fetchone() is not None

    async def get_player_info(self, discord_id: int) -> Optional[Dict[str, str]]:
        """Возвращает информацию об игроке в виде словаря с полями pName, pExp, pCYP, pBTV, pRP, pKMB, pBoss, pSkill"""
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT pName, pExp, pCYP, pBTV, pRP, pKMB, pBoss, pSkill FROM players WHERE DiscID = %s",
                    (discord_id,)
                )
                row = await cur.fetchone()
                if row:
                    return {
                        "pName": row[0],
                        "pExp": row[1],
                        "pCYP": row[2],
                        "pBTV": row[3],
                        "pRP": row[4],
                        "pKMB": row[5],
                        "pBoss": row[6],
                        "pSkill": row[7]
                    }
                return None

    async def update_player_info(self, discord_id: int, field_name: str, value: str = '0', type: Optional[str] = None, item_id: int = -1) -> bool:
        """
        Обновляет значение указанного поля для игрока. Возвращает pName игрока, если значение было изменено
        """
        player_info = await self.get_player_info(discord_id)

        if player_info is None:
            logging.error(f"Игрок с Discord ID {discord_id} не найден в базе данных.")
            return False

        current_value = '0'

        if not type or type not in ['fixed', 'string']:
            current_value = player_info[field_name]

        new_value = None
        set_clause: str

        if type and type == 'string':
            new_value = value
        else:
            try:
                value_number = int(value)

                if item_id == -1:
                    new_value = int(current_value) + value_number
                else:
                    data_index = item_id * 2 + 1
                    new_value = current_value[:data_index] + str(value_number) + current_value[data_index+1:]
            except:
                raise NotImplementedError(f'Некорректные параметры запроса: {field_name}, {item_id}, {value}')

        set_clause = f'{field_name} = %s'
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"UPDATE players SET {set_clause} WHERE DiscID = %s",
                    [new_value, str(discord_id)]
                )
                return cur.rowcount > 0
            

data_service: Optional[DataService] = None

async def prepare_data_service():
    """
    Асинхронно создает экземпляр DataService с подключением к базе данных.
    """
    global data_service
    data_service = await DataService.create(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        db=settings.db_name
    )

    logging.info(f'Подключение к базе данных успешно установлено')