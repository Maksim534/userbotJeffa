#!/usr/bin/env python3
# userbot/main.py
import asyncio
from telethon import TelegramClient, events
from loguru import logger

from config import API_ID, API_HASH
import loader
from module_manager import MODULES_DIR

logger.add("logs/userbot.log", rotation="1 MB")
logger.info("🚀 UserBot запускается...")

client = TelegramClient("userbot_session", API_ID, API_HASH)

async def main():
    MODULES_DIR.mkdir(exist_ok=True)
    
    commands, handlers = await loader.load_modules(client, {})
    
    @client.on(events.NewMessage(pattern=r"^\."))
    async def command_handler(event):
        message = event.message
        text = message.raw_text
        cmd = text.split()[0][1:]
        if cmd in commands:
            try:
                await commands[cmd](event)
            except Exception as e:
                logger.error(f"Ошибка в {cmd}: {e}")
                await event.reply(f"❌ Ошибка: {e}")
        else:
            await event.reply(f"🤷 Неизвестная команда: {cmd}\nНапиши `.modules` для списка")
    
    for handler in handlers:
        client.add_event_handler(handler)
    
    await client.start()
    logger.success("✅ UserBot запущен!")
    me = await client.get_me()
    logger.info(f"Аккаунт: @{me.username} (ID: {me.id})")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
