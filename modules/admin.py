#!/usr/bin/env python3
# userbot/modules/admin.py
import os
import zipfile
import tempfile
from pathlib import Path
import time
from datetime import datetime
import loader
from module_manager import (
    install_module_from_url, 
    uninstall_module, 
    get_all_modules, 
    get_module_info,
    MODULES_DIR
)

__info__ = {
    "name": "admin",
    "version": "1.2",
    "author": "Alpha",
    "description": "Управление модулями и справка"
}

COMMANDS_INFO = {
    "ping": "Проверка работы бота и аптайм",
    "dlmod": "Скачать и установить модуль по ссылке или из реплая на файл",
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
    print("✅ Админ-модуль загружен (режим редактирования)")

async def edit_or_reply(event, text):
    """Отправляет новое сообщение или редактирует существующее"""
    if hasattr(event, 'message') and event.message.out:
        # Если это наше сообщение — редактируем
        return await event.edit(text)
    else:
        # Иначе отправляем новое
        return await event.reply(text)

async def install_module_from_file(file_path, filename):
    dest_path = MODULES_DIR / filename
    with open(file_path, 'rb') as src:
        with open(dest_path, 'wb') as dst:
            dst.write(src.read())
    return {"success": True, "filename": filename}

async def dlmod_command(event):
    msg = await edit_or_reply(event, "📥 Обработка...")
    
    reply = await event.get_reply_message()
    
    # Реплай на файл .py
    if reply and reply.file and reply.file.name and reply.file.name.endswith('.py'):
        await msg.edit(f"📥 Скачиваю модуль из файла `{reply.file.name}`...")
        file_path = await reply.download_media()
        result = await install_module_from_file(file_path, reply.file.name)
        try:
            os.unlink(file_path)
        except:
            pass
        if result["success"]:
            await msg.edit(f"✅ Модуль `{result['filename']}` установлен!\n🔄 Введи `.reload`")
        else:
            await msg.edit(f"❌ Ошибка: {result.get('error')}")
        return
    
    # Реплай на архив .zip
    if reply and reply.file and reply.file.name and reply.file.name.endswith('.zip'):
        await msg.edit(f"📦 Устанавливаю из архива `{reply.file.name}`...")
        zip_path = await reply.download_media()
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)
            extracted = list(Path(tmpdir).glob("*.py"))
            if not extracted:
                extracted = list(Path(tmpdir).glob("*/*.py"))
            installed = []
            for py_file in extracted:
                dest = MODULES_DIR / py_file.name
                with open(py_file, 'rb') as src:
                    with open(dest, 'wb') as dst:
                        dst.write(src.read())
                installed.append(py_file.name)
        try:
            os.unlink(zip_path)
        except:
            pass
        if installed:
            await msg.edit(f"✅ Установлены:\n" + "\n".join([f"• `{m}`" for m in installed]) + f"\n\n🔄 Введи `.reload`")
        else:
            await msg.edit("❌ В архиве нет .py файлов")
        return
    
    # Обычная ссылка
    args = event.message.text.split()
    if len(args) < 2:
        await msg.edit("❌ Укажи ссылку или отправь .py файл с реплаем")
        return
    
    url = args[1]
    await msg.edit("📥 Скачиваю по ссылке...")
    result = install_module_from_url(url)
    if result["success"]:
        if result["type"] == "single":
            await msg.edit(f"✅ Модуль `{result['filename']}` установлен!\n🔄 Введи `.reload`")
        else:
            await msg.edit(f"✅ Установлены: {', '.join(result.get('filenames', []))}\n🔄 Введи `.reload`")
    else:
        await msg.edit(f"❌ Ошибка: {result.get('error')}")

async def help_command(event):
    msg = await edit_or_reply(event, "📚 Загрузка справки...")
    args = event.message.text.split()
    if len(args) > 1:
        module_name = args[1].lower()
        if module_name in COMMANDS_INFO:
            await msg.edit(f"📖 **{module_name}**\n└ {COMMANDS_INFO[module_name]}")
        else:
            await msg.edit(f"❌ Модуль `{module_name}` не найден")
        return
    
    help_text = "📚 **Справка по командам**\n\n"
    for cmd, desc in COMMANDS_INFO.items():
        help_text += f"• **{cmd}** — {desc}\n"
    help_text += "\n📌 **Примеры:**\n"
    help_text += "• `.help ping`\n"
    help_text += "• `.dlmod https://ссылка`\n"
    help_text += "• _реплай на .py файл + .dlmod_"
    await msg.edit(help_text)

async def modules_command(event):
    msg = await edit_or_reply(event, "📦 Загрузка списка модулей...")
    modules = get_all_modules()
    if not modules:
        await msg.edit("📦 Нет установленных модулей")
        return
    text = "📦 **Установленные модули:**\n\n"
    for mod in modules:
        info = get_module_info(mod)
        text += f"• `{mod}` v{info.get('version', '1.0')}\n"
    await msg.edit(text)

async def unload_command(event):
    msg = await edit_or_reply(event, "⏳ Удаление...")
    args = event.message.text.split()
    if len(args) < 2:
        await msg.edit("❌ Укажи имя модуля\nПример: `.unload ping`")
        return
    if uninstall_module(args[1]):
        await msg.edit(f"✅ Модуль `{args[1]}` удалён\n🔄 Введи `.reload`")
    else:
        await msg.edit("❌ Модуль не найден")

async def reload_command(event):
    msg = await edit_or_reply(event, "🔄 Перезагрузка...")
    await loader.reload_all_modules(event.client, loader.commands)
    await msg.edit(f"✅ Перезагружено {len(loader.commands)} команд!")

async def ping_command(event):
    msg = await edit_or_reply(event, "🏓 Измеряю пинг...")
    start_time = time.time()
    end_time = time.time()
    ping_ms = int((end_time - start_time) * 1000)
    
    uptime_seconds = time.time() - start_time
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    secs = int(uptime_seconds % 60)
    
    if days > 0:
        uptime_str = f"{days}д {hours}ч {minutes}м {secs}с"
    elif hours > 0:
        uptime_str = f"{hours}ч {minutes}м {secs}с"
    elif minutes > 0:
        uptime_str = f"{minutes}м {secs}с"
    else:
        uptime_str = f"{secs}с"
    
    await msg.edit(
        f"🏓 **Pong!**\n\n"
        f"📡 **Пинг:** `{ping_ms} мс`\n"
        f"⏱️ **Аптайм:** `{uptime_str}`\n"
        f"💖 **Статус:** ✅ Работаю"
    )
