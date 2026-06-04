# userbotJeffa/loader.py
import importlib.util
from pathlib import Path
from telethon import events
from loguru import logger

MODULES_DIR = Path(__file__).parent / "modules"
commands = {}
handlers = []

# ========== КЛАСС ДЛЯ СОВМЕСТИМОСТИ С HIKKA ==========
class Module:
    """Базовый класс для Hikka-модулей"""
    strings = {"name": "Module"}
    
    def __init__(self):
        self.client = None
        self.db = None
        self.inline = None
        self.allmodules = None
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db

# ========== УТИЛИТЫ ДЛЯ HIKKA-МОДУЛЕЙ ==========
class Utils:
    @staticmethod
    def get_args_raw(message):
        """Возвращает аргументы команды (как в Hikka)"""
        text = message.raw_text
        if ' ' in text:
            return text.split(' ', 1)[1].strip()
        return ""
    
    @staticmethod
    async def answer(message, text):
        """Отправляет ответ (как в Hikka)"""
        return await message.reply(text)

utils = Utils()

# ========== ЗАГРУЗЧИК МОДУЛЕЙ ==========
async def load_modules(client, commands_registry):
    global commands, handlers
    commands = commands_registry
    handlers.clear()
    
    for py_file in MODULES_DIR.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        
        module_name = py_file.stem
        try:
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Hikka-совместимая загрузка
            if hasattr(module, "Mod"):
                # Создаём экземпляр модуля
                mod_instance = module.Mod()
                mod_instance.client = client
                mod_instance.db = {}  # Простая БД в памяти
                mod_instance.allmodules = commands
                
                # Регистрируем команды (если есть метод client_ready)
                if hasattr(mod_instance, "client_ready"):
                    await mod_instance.client_ready(client, {})
                
                # Собираем команды из методов, начинающихся с "inly"
                for method_name in dir(mod_instance):
                    if method_name.startswith("inly"):
                        cmd_name = method_name[4:]  # убираем "inly"
                        commands[cmd_name] = getattr(mod_instance, method_name)
                        logger.info(f"📝 Зарегистрирована команда: {cmd_name}")
                
                logger.info(f"✅ Загружен модуль: {module_name}")
            
            # Альтернативная загрузка (через __setup__)
            elif hasattr(module, "__setup__"):
                await module.__setup__(client, commands, handlers)
                logger.info(f"✅ Загружен модуль: {module_name}")
                
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
