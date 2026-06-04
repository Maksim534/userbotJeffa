#!/usr/bin/env python3
# userbot/modules/admin.py
import loader
from module_manager import install_module_from_url, uninstall_module, get_all_modules, get_module_info

__info__ = {
    "name": "admin",
    "version": "1.0",
    "author": "catastrophe",
    "description": "Управление модулями"
}

async def __setup__(client, commands_registry, handlers_registry):
    commands_registry["dlmod"] = dlmod_command
    commands_registry["modules"] = modules_command
    commands_registry["unload"] = unload_command
    commands_registry["reload"] = reload_command

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
