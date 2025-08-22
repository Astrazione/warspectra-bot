from dataclasses import dataclass


@dataclass
class ChatProcessorResult:
    result_str: str
    ephemeral: bool = True