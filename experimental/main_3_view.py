import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from dataclasses import dataclass
from typing import List, Optional
from app.models.data_structure import Field
from app.utils.yaml_config_parser import YamlConfigParser


# SAMPLE_DATA = DataStructure(fields=[
#     Field(key="weapons", name="Оружие", items=[Item("Меч"), Item("Лук"), Item("Посох")]),
#     Field(key="armor", name="Броня", items=[Item("Щит"), Item("Кольчуга")]),
#     Field(key="accessories", name="Аксессуары", items=None)
# ])

SAMPLE_DATA = YamlConfigParser.parse('./app/config/data_structure.yaml')

# Кэш для хранения промежуточных данных формы
form_cache = {}

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class FormModal(discord.ui.Modal):
    def __init__(self, title: str, field_name: str, min_length: int = 1, max_length: int = 50):
        super().__init__(title=title)
        self.field_name = field_name
        self.text_input = discord.ui.TextInput(
            label=title,
            min_length=min_length,
            max_length=max_length,
        )
        self.add_item(self.text_input)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        form_cache.setdefault(user_id, {})[self.field_name] = self.text_input.value
        await self.next_step(interaction)

    async def next_step(self, interaction: discord.Interaction):
        """Метод должен быть реализован в дочерних классах"""
        raise NotImplementedError

class DiscordIDModal(FormModal):
    def __init__(self):
        super().__init__("Введите Discord ID", "discord_id", min_length=17, max_length=20)

    async def next_step(self, interaction: discord.Interaction):
        view = FieldSelectView(interaction.user.id)
        await interaction.response.send_message(
            "Выберите категорию:", 
            view=view, 
            ephemeral=True
        )

class NumberModal(FormModal):
    def __init__(self, user_id: int):
        super().__init__("Введите число", "number", min_length=1, max_length=10)
        self.user_id = user_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            form_cache[self.user_id]["number"] = int(self.text_input.value)
            await self.finalize(interaction)
        except ValueError:
            await interaction.response.send_message(
                "Ошибка: введите корректное число", 
                ephemeral=True
            )

    async def finalize(self, interaction: discord.Interaction):
        data = form_cache[self.user_id]
        result = (
            f"✅ Значение успешно установлено!\n"
            f"**Discord ID:** {data['discord_id']}\n"
            f"**Категория:** {data['field'].name}\n"
            f"**Элемент:** {data.get('item', 'Не выбран')}\n"
            f"**Значение:** {data['number']}"
        )
        await interaction.response.send_message(result, ephemeral=True)
        del form_cache[self.user_id]

class FieldSelectView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id
        
        options = [
            discord.SelectOption(
                label=field.name, 
                value=field.key
            )
            for field in SAMPLE_DATA.fields
        ]
        
        self.select = discord.ui.Select(
            placeholder="Выберите категорию...",
            options=options
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        selected_key = self.select.values[0]
        field = next(f for f in SAMPLE_DATA.fields if f.key == selected_key)
        form_cache[self.user_id]["field"] = field

        if field.items:
            view = ItemSelectView(self.user_id, field)
            await interaction.response.edit_message(
                content="Выберите элемент:", 
                view=view
            )
        else:
            modal = NumberModal(self.user_id)
            await interaction.response.send_modal(modal)

class ItemSelectView(discord.ui.View):
    def __init__(self, user_id: int, field: Field):
        super().__init__()
        self.user_id = user_id
        self.field = field
        
        options = [
            discord.SelectOption(
                label=item.name, 
                value=item.name
            )
            for item in field.items or []  # Пустой список, если items нет
        ]
        
        self.select = discord.ui.Select(
            placeholder="Выберите элемент...",
            options=options
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        form_cache[self.user_id]["item"] = self.select.values[0]
        modal = NumberModal(self.user_id)
        await interaction.response.send_modal(modal)

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")

@bot.command()
async def form(ctx: Context):
    """Запустить форму для заполнения данных"""
    if ctx.author.id in form_cache:
        await ctx.send("Вы уже заполняете форму!", delete_after=5)
        return
        
    # Для prefix-команд нужно отправить сообщение с кнопкой,
    # которая запустит interaction для модального окна
    class StartFormButton(discord.ui.View):
        def __init__(self, user_id):
            super().__init__()
            self.user_id = user_id

        @discord.ui.button(label="Заполнить форму", style=discord.ButtonStyle.primary)
        async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("Это не ваша форма!", ephemeral=True)
                return
                
            modal = DiscordIDModal()
            await interaction.response.send_modal(modal)

    view = StartFormButton(ctx.author.id)
    await ctx.send("Форма для установки значений в базе данных Warspectra. Нажмите кнопку ниже, чтобы заполнить форму:", view=view)

# Запуск бота
bot.run("TOKEN")