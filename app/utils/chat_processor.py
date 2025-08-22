import logging
from models.chat_cache import ChatCache
from models.chat_state import ChatState
from models.data_structure import Field
from models.user_cache import UserCache
from config.settings import settings
import database


class ChatProcessor():
    cache = ChatCache()
    reset_strs = ["сброс", "reset", "галя отмена", "галя, отмена"]

    @staticmethod
    def is_discord_id(message: str) -> bool:
        return message.isdigit() and 10 <= len(message) <= 22

    async def process_message(self, operator_id: int, message: str) -> str:
        """
        Обрабатывает входящее сообщение от пользователя.
        Если сообщение начинается с 'set', пытается установить значение поля.
        Иначе возвращает ответ по умолчанию.
        """

        if message.strip().lower() in self.reset_strs:
            if operator_id in self.cache:
                del self.cache[operator_id]
            logging.info('Кэш оператора сброшен')
            return "Кэш оператора сброшен. Для начала работы введите Discord ID игрока"

        if operator_id not in self.cache:
            if ChatProcessor.is_discord_id(message):
                discord_id = int(message)
                self.cache[operator_id] = UserCache(target_user_id=discord_id)
                return ChatProcessor.get_fields_reply()
            
            self.cache[operator_id] = UserCache()
            return "Здравствуйте! Для начала работы ведите Discord ID игрока"
            
            
        match self.cache[operator_id].chat_state:
            case ChatState.AWAIT_DISCORD_ID:
                if ChatProcessor.is_discord_id(message):
                    if database.data_service is not None:
                        player_info = await database.data_service.get_player_info(int(message))

                        if player_info is None:
                            player_not_found_error_text = f"Игрок с Discord ID {message} не найден в базе данных"
                            logging.error(player_not_found_error_text)
                            return f"{player_not_found_error_text} Повторите попытку ввода Discord ID игрока"
                    else:
                        connection_error_text = "Подключение к базе данных отсутствует"
                        logging.error(connection_error_text)
                        return connection_error_text

                    self.cache[operator_id].target_discord_id = int(message)
                    self.cache[operator_id].chat_state = ChatState.AWAIT_FIELDNAME
                    return ChatProcessor.get_fields_reply()
                else:
                    return "Пожалуйста, введите корректный Discord Id"
                
            case ChatState.AWAIT_FIELDNAME:
                if not message.isdigit():
                    return "Пожалуйста, введите число"
                
                fields = settings.data_structure.fields
                field_index = int(message) - 1

                if field_index >= len(fields) or field_index < 0:
                    return "Пожалуйста, введите корректный индекс"
                
                selected_field = fields[field_index]
                self.cache[operator_id].field = selected_field
                self.cache[operator_id].chat_state = ChatState.AWAIT_OPTION
                items_reply = ChatProcessor.get_items_reply(selected_field)

                if not items_reply:
                    self.cache[operator_id].chat_state = ChatState.AWAIT_VALUE
                    if selected_field.type and selected_field.type == "string":
                        return "Введите значение (строка):"
                    else:
                        if selected_field.range:
                            return f"Введите значение от {selected_field.range.min} до {selected_field.range.max}"
                        else:
                            return "Введите значение добавляемое значение (число):"
                
                return items_reply
            
            case ChatState.AWAIT_OPTION:
                if not message.isdigit():
                    return "Пожалуйста, введите индекс элемента"
                
                selected_field = self.cache[operator_id].field

                if selected_field is None or selected_field.items is None:
                    return "Произошла ошибка. Пожалуйста, начните заново."

                items = selected_field.items
                item_index = int(message) - 1

                if item_index >= len(items) or item_index < 0:
                    return "Пожалуйста, введите корректный индекс"

                selected_item = items[item_index]
                self.cache[operator_id].item = selected_item
                self.cache[operator_id].chat_state = ChatState.AWAIT_VALUE
                return f"Теперь выберите значение: \n1. Нет\n2. Есть"
            
            case ChatState.AWAIT_VALUE:
                if database.data_service is None:
                    return "Отсутствует подключение к базе данных."
                
                value = message
                cached_data = self.cache[operator_id]
                field = cached_data.field
                target_discord_id = cached_data.target_discord_id
                item = cached_data.item
                
                if not field or not target_discord_id:
                    return "Произошла неизвестная ошибка. Пожалуйста, начните заново."
                
                if not field.type or field.type != 'string':
                    try:
                        value_number = int(value)

                        if field.range and (value_number < field.range.min or value_number > field.range.max):
                            return f"Некорректный ввод. Пожалуйста, введите число в диапазоне от {field.range.min} до {field.range.max}"

                    except:
                        raise ValueError(f"Пожалуйста, введите {'индекс' if field.items else 'число'}")

                    if field.items and (value_number < 1 or value_number > 2):
                        return f'Пожалуйста, введите корректный индекс' 

                item_id = field.items.index(item) if field.items and item else -1

                if item_id != -1:
                    value = str(int(value) - 1)

                await database.data_service.update_player_info(target_discord_id, field_name=field.key, value=value, type=field.type, item_id=item_id)

                result_str: str = f'установлено/добавлено значение {value} пользователю {target_discord_id} для поля {field.name}({field.key}){f": {item.name}" if item else ""}'

                logging.info(f'Оператором {operator_id} {result_str}')

                del self.cache[operator_id]
                return result_str
        
        return "Неизвестная ошибка. Пожалуйста, попробуйте еще раз."
                    

    @staticmethod
    def get_fields_reply() -> str:
        fields = settings.data_structure.fields
        fields_enumeration_reply = "\n".join([f"{index}. {field.name} ({field.key})" for index, field in enumerate(fields)])
        return f"Выберите поле по индексу:\n{fields_enumeration_reply}"
    
    @staticmethod
    def get_items_reply(field: Field):
        items = field.items
        if not items:
            return None
        fields_enumeration_reply = "\n".join([f"{index}. {item.name}" for index, item in enumerate(items)])
        return f"Выберите поле по индексу:\n{fields_enumeration_reply}"
