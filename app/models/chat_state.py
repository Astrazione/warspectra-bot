from enum import Enum, auto


class ChatState(Enum):
    CHAT_END = auto(),
    AWAIT_DISCORD_ID = auto(),
    AWAIT_FIELDNAME = auto(),
    AWAIT_OPTION = auto(),
    AWAIT_VALUE = auto(),