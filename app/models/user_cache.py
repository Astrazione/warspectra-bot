from dataclasses import dataclass
from typing import Optional

from models.chat_state import ChatState
from models.data_structure import Item, Field


class UserCache:
    chat_state: ChatState = ChatState.AWAIT_DISCORD_ID
    target_discord_id: Optional[int]
    field: Optional[Field] = None
    item: Optional[Item] = None
    value: Optional[int] = None
 
    def __init__ (self, target_user_id: Optional[int] = None):
        if target_user_id is not None:
            self.chat_state = ChatState.AWAIT_FIELDNAME
        self.target_discord_id = target_user_id