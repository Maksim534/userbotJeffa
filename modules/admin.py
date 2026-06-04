#!/usr/bin/env python3
# userbot/modules/admin.py
import loader
from module_manager import install_module_from_url, uninstall_module, get_all_modules, get_module_info

__info__ = {
    "name": "admin",
    "version": "1.0",
    "author": "Alpha",
    "description": "Управление модулями и справка"
}

# Словарь с описаниями команд для .help
COMMANDS_INFO = {
    "ping": "Проверка работы бота и аптайм",
    "dlmod": "Скачать и установить модуль по ссылке",
    "modules": "Список установленных модулей",
    "unload": "Удалить модуль по имени",
    "reload": "Перезагрузить все модули",
    "help": "Показать справку по командам или модулю"
}

async def __setup__(client, commands_registry, handlers_registry):
    commands_registry["ping"] = ping_command
    commands_registry["dlmod"] = dlmod_command
    commands_registry["modules"] = modules_command
    commands_registry["unload"] = unload_command
    commands_registry["reload"] = reload_command
    commands_registry["help"] = help_command
    
    print("✅ Админ-модуль загружен")

async def help_command(event):
    """Показывает справку по командам"""
    args = event.message.text.split()
    
    # Если указан конкретный модуль: .help ping
    if len(args) > 1:
        module_name = args[1].lower()
        if module_name in COMMANDS_INFO:
            await event.reply(f"📖 **{module_name}**\n└ {COMMANDS_INFO[module_name]}")
        else:
            await event.reply(f"❌ Модуль `{module_name}` не найден")
        return
    
    # Общая справка: список всех команд
    msg = "📚 **Справка по командам**\n\n"
    
    for cmd, desc in COMMANDS_INFO.items():
        msg += f"• **{cmd}** — {desc}\n"
    
    msg += "\n📌 **Примеры использования:**\n"
    msg += "• `.help ping` — подробно о команде ping\n"
    msg += "• `.dlmod https://ссылка` — установить модуль\n"
    msg += "• `.modules` — список модулей"
    
    await event.reply(msg)

# Остальные команды без изменений
async def ping_command(event):
    import time
    from datetime import datetime
    start_time = time.time()
    msg = await event.reply("🏓 Измеряю пинг...")
    end_time = time.time()
    ping_ms = int((end_time - start_time) * 1000)
    await msg.edit(f"🏓 **Pong!**\n📡 Пинг: `{ping_ms} мс`\n⏱️ Аптайм: бот работает")

async def dlmod_command(event):
    args = event.message.text.split()
    if len(args) < 2:
        await event.reply("❌ Укажи ссылку\nПример: `.dlmod https://...`")
        return
    url = args[1]
    await event.reply("📥 Скачиваю...")
    result = install_module_from_url(url)
    if result["success"]:
        await event.reply(f"✅ Установлено!\n🔄 Введи `.reload` для активации")
    else:
        await event.reply(f"❌ Ошибка: {result.get('error')}")

async def modules_command(event):
    modules = get_all_modules()
    if not modules:
        await event.reply("📦 Нет модулей")
        return
    msg = "📦 **Установленные модули:**\n\n"
    for mod in modules:
        info = get_module_info(mod)
        msg += f"• `{mod}` v{info.get('version', '1.0')}\n"
    await event.reply(msg)

async def unload_command(event):
    args = event.message.text.split()
    if len(args) < 2:
        await event.reply("❌ Укажи имя модуля\nПример: `.unload ping`")
        return
    if uninstall_module(args[1]):
        await event.reply(f"✅ Модуль `{args[1]}` удалён\n🔄 Введи `.reload`")
    else:
        await event.reply("❌ Модуль не найден")

async def reload_command(event):
    await event.reply("🔄 Перезагружаю...")
    await loader.reload_all_modules(event.client, loader.commands)
    await event.reply(f"✅ Перезагружено {len(loader.commands)} команд!")
