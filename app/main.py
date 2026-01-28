import discord
from discord.ext import commands
from discord import Message
from config.settings import settings
import service
import database
import logging


logging.basicConfig(filename='logs/bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logging.info(f'Бот запущен как {bot.user}')
    await database.prepare_data_service()

@bot.event
async def on_message(msg: Message):
    try:
        if msg.author.bot or msg.content.startswith('/'):
            return
        
        user_id = msg.author.id
        username = msg.author.name
        reply_text = await service.process_message(user_id, username, msg.content)
        if reply_text:
            await msg.channel.send(reply_text)

    except Exception as ex:
        logging.error(f"Произошла ошибка: {ex}")
        await msg.channel.send("Произошла ошибка. Для подробностей проверьте log файл")

bot.run(settings.discord_bot_token)