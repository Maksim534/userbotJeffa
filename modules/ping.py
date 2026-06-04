#!/usr/bin/env python3
# userbot/modules/ping.py
from loguru import logger

__info__ = {
    "name": "ping",
    "version": "1.0",
    "author": "catastrophe",
    "description": "Проверка работы бота"
}

async def __setup__(client, commands_registry, handlers_registry):
    commands_registry["ping"] = ping_command
    logger.info("Модуль ping загружен")

async def ping_command(event):
    await event.reply("🏓 Pong! Бот работает, Альфа!")
