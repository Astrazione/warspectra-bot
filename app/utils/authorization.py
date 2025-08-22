from functools import wraps
import database

async def autorize_operator(discord_id: int) -> bool:
    """
    Проверяет, является ли пользователь оператором.
    Возвращает True, если discord_id есть в таблице operators, иначе False.
    """
    if database.data_service is None:
        raise RuntimeError("DataService не проинициализирован. Выполните prepare_data_service() перед использованием.")
    
    return await database.data_service.is_operator(discord_id)
    
async def require_authorization(func):
    @wraps(func)
    async def wrapper(user_id: int, *args, **kwargs):
        if not await autorize_operator(user_id):
            return str()
        return await func(user_id, *args, **kwargs)
    return wrapper