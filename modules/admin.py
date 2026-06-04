# userbot/modules/admin.py
import time
from datetime import datetime
import loader
from module_manager import get_all_modules, get_module_info, MODULES_DIR

__info__ = {
    "name": "Admin",
    "version": "1.0",
    "author": "Alpha",
    "description": "Управление юзерботом"
}

# Стартовое время для аптайма
START_TIME = time.time()

async def __setup__(client, commands_registry, handlers_registry):
    commands_registry["help"] = help_command
    commands_registry["ping"] = ping_command
    commands_registry["reload"] = reload_command
    commands_registry["modules"] = modules_command
    print("✅ Админ-модуль загружен (как Hikka)")

def format_uptime(seconds):
    """Форматирует аптайм в формат Hikka"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def collect_commands_by_module():
    """Собирает все команды, сгруппированные по модулям"""
    modules_commands = {}
    
    # Проходим по всем загруженным модулям
    for module_name in get_all_modules():
        module_path = MODULES_DIR / f"{module_name}.py"
        if not module_path.exists():
            continue
        
        # Пытаемся получить информацию о командах из модуля
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Если у модуля есть функция get_commands_info
            if hasattr(module, "get_commands_info"):
                commands_info = module.get_commands_info()
                if commands_info:
                    modules_commands[module_name] = commands_info
        except:
            pass
    
    return modules_commands

async def help_command(event):
    """Показывает справку как в Hikka"""
    msg = await event.reply("📚 Загрузка справки...")
    
    modules_commands = collect_commands_by_module()
    
    if not modules_commands:
        await msg.edit("❌ Нет загруженных модулей")
        return
    
    # Подсчёт общего количества команд
    total_commands = sum(len(cmds) for cmds in modules_commands.values())
    
    result = f"🌘 {len(modules_commands)} mods available, {total_commands} commands:\n\n"
    
    for module_name, commands in modules_commands.items():
        # Красивое название модуля
        display_name = module_name.capitalize()
        cmd_list = " | ".join([f".{cmd}" for cmd in commands])
        result += f"▪️ {display_name}: ( {cmd_list} )\n"
    
    await msg.edit(result)

async def ping_command(event):
    """Показывает пинг и аптайм как в Hikka"""
    start = time.time()
    msg = await event.reply("🏓 Понг...")
    end = time.time()
    
    ping_ms = int((end - start) * 1000)
    uptime_str = format_uptime(time.time() - START_TIME)
    
    result = f"⚡️ Telegram ping: {ping_ms} ms\n🚀 Uptime: {uptime_str}"
    await msg.edit(result)

async def reload_command(event):
    """Перезагружает все модули"""
    msg = await event.reply("🔄 Перезагрузка...")
    await loader.reload_all_modules(event.client, loader.commands)
    await msg.edit("✅ Перезагружено!")

async def modules_command(event):
    """Список модулей"""
    modules = get_all_modules()
    if not modules:
        await event.reply("📦 Нет модулей")
        return
    result = "📦 **Модули:**\n\n"
    for mod in modules:
        info = get_module_info(mod)
        version = info.get('version', '1.0')
        result += f"• `{mod}` v{version}\n"
    await event.reply(result)
