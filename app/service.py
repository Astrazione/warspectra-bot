from utils.chat_processor import ChatProcessor
from utils.authorization import autorize_operator

chat_processor: ChatProcessor = ChatProcessor()

def parse_args(args: list) -> bool:
    """
    Парсит аргументы команды и проверяет их корректность.
    """
    if len(args) != 4:
        return False

    try:
        int(args[0])  # user_id
        int(args[3])  # value
    except ValueError:
        return False
    return True

# @require_authorization
async def process_message(user_id: int, message_content: str) -> str:
    if not await autorize_operator(user_id):
        return str()
    
    return await chat_processor.process_message(user_id, message_content)