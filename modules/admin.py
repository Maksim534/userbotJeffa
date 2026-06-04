#!/usr/bin/env python3
# userbot/modules/admin.py
import os
import zipfile
import tempfile
from pathlib import Path
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
    "version": "1.1",
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
    
    print("✅ Админ-модуль загружен (с поддержкой реплая на файл)")

async def install_module_from_file(file_path, filename):
    """Устанавливает модуль из загруженного файла"""
    try:
        dest_path = MODULES_DIR / filename
        with open(file_path, 'rb') as src:
            with open(dest_path, 'wb') as dst:
                dst.write(src.read())
        return {"success": True, "filename": filename, "type": "file"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def dlmod_command(event):
    """Скачивает и устанавливает модуль по ссылке или из реплая на файл"""
    
    # Проверяем, есть ли реплай на файл
    reply = await event.get_reply_message()
    
    # Случай 1: Реплай на файл (.py)
    if reply and reply.file and reply.file.name and reply.file.name.endswith('.py'):
        await event.reply(f"📥 Скачиваю модуль из файла `{reply.file.name}`...")
        
        # Скачиваем файл
        file_path = await reply.download_media()
        
        result = await install_module_from_file(file_path, reply.file.name)
        
        # Удаляем временный файл
        try:
            os.unlink(file_path)
        except:
            pass
        
        if result["success"]:
            await event.reply(f"✅ Модуль `{result['filename']}` установлен из файла!\n🔄 Введи `.reload` для активации")
        else:
            await event.reply(f"❌ Ошибка установки из файла: {result.get('error')}")
        return
    
    # Случай 2: Реплай на архив (.zip)
    if reply and reply.file and reply.file.name and reply.file.name.endswith('.zip'):
        await event.reply(f"📦 Устанавливаю модули из архива `{reply.file.name}`...")
        
        # Скачиваем архив
        zip_path = await reply.download_media()
        
        # Распаковываем
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)
            
            # Ищем .py файлы
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
        
        # Удаляем архив
        try:
            os.unlink(zip_path)
        except:
            pass
        
        if installed:
            await event.reply(f"✅ Установлены модули из архива:\n" + "\n".join([f"• `{m}`" for m in installed]) + f"\n\n🔄 Введи `.reload` для активации")
        else:
            await event.reply("❌ В архиве не найдено .py файлов")
        return
    
    # Случай 3: Обычная ссылка
    args = event.message.text.split()
    if len(args) < 2:
        await event.reply(
            "❌ **Как использовать .dlmod:**\n\n"
            "1️⃣ По ссылке:\n"
            "   `.dlmod https://raw.githubusercontent.com/.../module.py`\n\n"
            "2️⃣ Из файла:\n"
            "   Отправь `.py` файл в чат, сделай реплай на него и напиши `.dlmod`\n\n"
            "3️⃣ Из архива:\n"
            "   Отправь `.zip` с модулями, сделай реплай и напиши `.dlmod`"
        )
        return
    
    url = args[1]
    await event.reply("📥 Скачиваю модуль по ссылке...")
    result = install_module_from_url(url)
    
    if result["success"]:
        if result["type"] == "single":
            await event.reply(f"✅ Модуль `{result['filename']}` установлен!\n🔄 Введи `.reload` для активации")
        else:
            await event.reply(f"✅ Установлены модули: {', '.join(result.get('filenames', []))}\n🔄 Введи `.reload` для активации")
    else:
        await event.reply(f"❌ Ошибка установки: {result.get('error')}")

# Остальные команды без изменений
async def help_command(event):
    args = event.message.text.split()
    if len(args) > 1:
        module_name = args[1].lower()
        if module_name in COMMANDS_INFO:
            await event.reply(f"📖 **{module_name}**\n└ {COMMANDS_INFO[module_name]}")
        else:
            await event.reply(f"❌ Модуль `{module_name}` не найден")
        return
    
    msg = "📚 **Справка по командам**\n\n"
    for cmd, desc in COMMANDS_INFO.items():
        msg += f"• **{cmd}** — {desc}\n"
    
    msg += "\n📌 **Примеры использования:**\n"
    msg += "• `.help ping` — подробно о команде ping\n"
    msg += "• `.dlmod https://ссылка` — установить модуль по ссылке\n"
    msg += "• _Пришли .py файл, сделай реплай и напиши `.dlmod`_ — установить из файла\n"
    msg += "• `.modules` — список модулей"
    
    await event.reply(msg)

async def ping_command(event):
    import time
    from datetime import datetime
    start_time = time.time()
    msg = await event.reply("🏓 Измеряю пинг...")
    end_time = time.time()
    ping_ms = int((end_time - start_time) * 1000)
    await msg.edit(f"🏓 **Pong!**\n📡 Пинг: `{ping_ms} мс`\n⏱️ Аптайм: бот работает")

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
