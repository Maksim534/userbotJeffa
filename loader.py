#!/usr/bin/env python3
# userbot/loader.py
import importlib.util
from pathlib import Path
from loguru import logger
from module_manager import MODULES_DIR, load_installed_modules, save_installed_modules

commands = {}
handlers = []

async def load_modules(client, commands_registry):
    global commands, handlers
    commands = commands_registry
    handlers.clear()
    
    installed = load_installed_modules()
    
    for py_file in MODULES_DIR.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        module_name = py_file.stem
        try:
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "__setup__"):
                await module.__setup__(client, commands_registry, handlers)
                logger.info(f"✅ Загружен модуль: {module_name}")
                if module_name not in installed:
                    info = getattr(module, "__info__", {"name": module_name})
                    installed[module_name] = info
                    save_installed_modules(installed)
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки {module_name}: {e}")
    
    logger.info(f"📦 Загружено модулей: {len(commands)}")
    return commands, handlers

async def reload_all_modules(client, commands_registry):
    import sys
    global commands, handlers
    modules_to_reload = [name for name in sys.modules if name.startswith("modules.")]
    for mod in modules_to_reload:
        del sys.modules[mod]
    commands.clear()
    handlers.clear()
    return await load_modules(client, commands_registry)
