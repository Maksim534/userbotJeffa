#!/usr/bin/env python3
# userbot/main.py
import asyncio
from telethon import TelegramClient, events
from loguru import logger

# Импортируем настройки и загрузчик модулей
from config import API_ID, API_HASH, BOT_TOKEN  # Пока не трогаем, создадим позже
import loader

logger.add("logs/userbot.log", rotation="1 MB")
logger.info("🚀 UserBot запускается...")

# Создаем клиента (именно с ним ты будешь работать)
client = TelegramClient("userbot_session", API_ID, API_HASH)

async def main():
    # 1. Загружаем все модули из папки modules/
    await loader.load_modules(client)
    
    # 2. Регистрируем универсальный обработчик команд
    @client.on(events.NewMessage(pattern=r"^\.")
    async def handler(event):
        message = event.message
        text = message.raw_text
        cmd = text.split()[0][1:]  # Убираем точку, получаем "ping"
        
        # Ищем команду в загруженных модулях
        if cmd in loader.commands:
            try:
                # Выполняем функцию из модуля, передавая ей event
                await loader.commands[cmd](event)
            except Exception as e:
                logger.error(f"Ошибка в команде {cmd}: {e}")
                await event.reply(f"❌ Ошибка: {e}")
        else:
            await event.reply(f"🤷 Неизвестная команда: {cmd}. Напиши .help")

    # 3. Запускаем клиента
    await client.start()
    logger.success("✅ UserBot запущен!")
    logger.info(f"Аккаунт: {(await client.get_me()).username}")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
