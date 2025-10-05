from utils.chat_processor import ChatProcessor
from utils.authorization import autorize_operator

chat_processor: ChatProcessor = ChatProcessor()

# @require_authorization
async def process_message(user_id: int, username: str, message_content: str) -> str:
    if not await autorize_operator(user_id):
        return str()

    return await chat_processor.process_message(user_id, username, message_content)