#!/usr/bin/env python3
# userbot/modules/ping.py
import time
from datetime import datetime
from loguru import logger

# Время запуска модуля (установится при загрузке)
start_time = time.time()

__info__ = {
    "name": "ping",
    "version": "1.0",
    "author": "catastrophe",
    "description": "Проверка работы бота с аптаймом"
}

async def __setup__(client, commands_registry, handlers_registry):
    global start_time
    start_time = time.time()  # Обновляем время при загрузке модуля
    commands_registry["ping"] = ping_command
    logger.info("Модуль ping загружен (с аптаймом)")

def format_uptime(seconds):
    """Форматирует время работы в человеческий вид"""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if days > 0:
        return f"{days}д {hours}ч {minutes}м {secs}с"
    elif hours > 0:
        return f"{hours}ч {minutes}м {secs}с"
    elif minutes > 0:
        return f"{minutes}м {secs}с"
    else:
        return f"{secs}с"

async def ping_command(event):
    global start_time
    
    # Время работы
    uptime_seconds = time.time() - start_time
    uptime_str = format_uptime(uptime_seconds)
    
    # Замеряем пинг (отправляем сообщение и засекаем время)
    start_ping = time.time()
    msg = await event.reply("🏓 Измеряю пинг...")
    end_ping = time.time()
    ping_ms = int((end_ping - start_ping) * 1000)
    
    # Редактируем сообщение с результатами
    await msg.edit(
        f"🏓 **Pong!**\n\n"
        f"⏱️ **Аптайм:** `{uptime_str}`\n"
        f"📡 **Пинг:** `{ping_ms} мс`\n"
        f"🤖 **Статус:** ✅ Работаю\n"
        f"📅 **Запуск:** `{datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}`"
    )
