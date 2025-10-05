from typing import Optional

from models.chat_state import ChatState
from models.data_structure import Item, Field


class UserCache:
    chat_state: ChatState = ChatState.AWAIT_DISCORD_ID
    operator_username: str
    target_discord_id: Optional[int]
    target_username = Optional[str]
    field: Optional[Field] = None
    item: Optional[Item] = None
    value: Optional[int] = None
 
    def __init__ (self, operator_username: str, target_user_id: Optional[int] = None, target_username: Optional[str] = None):
        if target_user_id is not None:
            self.chat_state = ChatState.AWAIT_FIELDNAME

        self.operator_username = operator_username
        self.target_discord_id = target_user_id
        self.target_username = target_username