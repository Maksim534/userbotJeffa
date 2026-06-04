# userbotJeffa/loader.py
import importlib.util
from pathlib import Path
from telethon import events
from loguru import logger
import asyncio

MODULES_DIR = Path(__file__).parent / "modules"
commands = {}  # команда -> функция
handlers = []  # watcher'ы
modules_instances = []  # экземпляры модулей для Hikka-совместимости

class Module:
    """Базовый класс для Hikka-модулей"""
    strings = {"name": "Module"}
    
    def __init__(self):
        self.client = None
        self.db = {}
        self.allmodules = commands
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db

class Utils:
    @staticmethod
    def get_args_raw(message):
        text = message.raw_text
        if ' ' in text:
            return text.split(' ', 1)[1].strip()
        return ""
    
    @staticmethod
    async def answer(message, text):
        return await message.reply(text)

utils = Utils()

async def load_modules(client):
    global commands, handlers, modules_instances
    commands.clear()
    handlers.clear()
    modules_instances.clear()
    
    for py_file in MODULES_DIR.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        
        module_name = py_file.stem
        try:
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Способ 1: Hikka-модуль (класс Mod)
            if hasattr(module, "Mod"):
                mod_instance = module.Mod()
                mod_instance.client = client
                mod_instance.db = {}
                mod_instance.allmodules = commands
                
                if hasattr(mod_instance, "client_ready"):
                    await mod_instance.client_ready(client, {})
                
                # Регистрируем методы, начинающиеся с inly
                for method_name in dir(mod_instance):
                    if method_name.startswith("inly"):
                        cmd_name = method_name[4:]
                        commands[cmd_name] = getattr(mod_instance, method_name)
                        logger.info(f"📝 Команда: {cmd_name}")
                
                modules_instances.append(mod_instance)
                logger.info(f"✅ Hikka-модуль: {module_name}")
            
            # Способ 2: простой модуль с __setup__
            elif hasattr(module, "__setup__"):
                await module.__setup__(client, commands, handlers)
                logger.info(f"✅ Простой модуль: {module_name}")
            
            # Способ 3: модуль с командами напрямую
            else:
                for attr_name in dir(module):
                    if attr_name.endswith("_command") and callable(getattr(module, attr_name)):
                        cmd_name = attr_name.replace("_command", "")
                        commands[cmd_name] = getattr(module, attr_name)
                        logger.info(f"📝 Команда: {cmd_name}")
                logger.info(f"✅ Модуль: {module_name}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка {module_name}: {e}")
    
    logger.info(f"📦 Всего команд: {len(commands)}")
    return commands, handlers

async def reload_all_modules(client):
    import sys
    global commands, handlers, modules_instances
    modules_to_reload = [name for name in sys.modules if name.startswith("modules.")]
    for mod in modules_to_reload:
        del sys.modules[mod]
    return await load_modules(client)
