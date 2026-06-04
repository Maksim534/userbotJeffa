# userbotJeffa/modules/admin.py
import time
import loader
from module_manager import get_all_modules, get_module_info

__version__ = (1, 0, 0)

class Mod(loader.Module):
    strings = {"name": "Admin"}
    
    async def client_ready(self, client, db):
        self.start_time = time.time()
    
    async def inlyhelp(self, message):
        """Показать справку по командам"""
        args = loader.utils.get_args_raw(message)
        
        if args:
            cmd_name = args.lower()
            if cmd_name in loader.commands:
                await loader.utils.answer(message, f"📖 **{cmd_name}**\n└ Команда доступна")
            else:
                await loader.utils.answer(message, f"❌ Команда `{cmd_name}` не найдена")
            return
        
        # Группируем команды по модулям
        modules_cmds = {}
        for cmd in loader.commands:
            modules_cmds.setdefault("Core", []).append(cmd)
        
        result = f"🌘 {len(modules_cmds)} mods available, {len(loader.commands)} commands:\n\n"
        for mod_name, cmds in modules_cmds.items():
            result += f"▪️ {mod_name}: ( " + " | ".join([f".{c}" for c in cmds]) + " )\n"
        
        await loader.utils.answer(message, result)
    
    async def inlyping(self, message):
        """Проверить пинг и аптайм"""
        start = time.time()
        msg = await loader.utils.answer(message, "🏓 Понг...")
        end = time.time()
        
        ping_ms = int((end - start) * 1000)
        uptime_seconds = time.time() - self.start_time
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        secs = int(uptime_seconds % 60)
        
        uptime_str = f"{hours:02d}:{minutes:02d}:{secs:02d}"
        
        await msg.edit(f"⚡️ Telegram ping: {ping_ms} ms\n🚀 Uptime: {uptime_str}")
    
    async def inlyreload(self, message):
        """Перезагрузить все модули"""
        await loader.utils.answer(message, "🔄 Перезагрузка...")
        await loader.reload_all_modules(self.client)
        await message.reply(f"✅ Перезагружено {len(loader.commands)} команд!")
    
    async def inlymodules(self, message):
        """Список установленных модулей"""
        modules = get_all_modules()
        if not modules:
            await loader.utils.answer(message, "📦 Нет модулей")
            return
        result = "📦 **Модули:**\n\n"
        for mod in modules:
            result += f"• `{mod}`\n"
        await loader.utils.answer(message, result)
