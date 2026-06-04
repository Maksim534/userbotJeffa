#!/usr/bin/env python3
# userbot/module_manager.py
import os
import json
import importlib.util
import requests
import shutil
import zipfile
import tempfile
from pathlib import Path
from loguru import logger

MODULES_DIR = Path(__file__).parent / "modules"
INSTALLED_FILE = Path(__file__).parent / "installed_modules.json"
TEMP_DIR = Path(__file__).parent / "temp"

MODULES_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)

def load_installed_modules():
    if INSTALLED_FILE.exists():
        with open(INSTALLED_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_installed_modules(modules_dict):
    with open(INSTALLED_FILE, 'w') as f:
        json.dump(modules_dict, f, indent=2)

def get_module_info(module_name):
    module_path = MODULES_DIR / f"{module_name}.py"
    if not module_path.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, "__info__", {"name": module_name, "version": "1.0", "author": "Unknown"})
    except:
        return {"name": module_name, "version": "1.0", "author": "Unknown"}

def install_module_from_url(url):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        if url.endswith('.py'):
            filename = url.split('/')[-1]
            if not filename.endswith('.py'):
                filename += '.py'
            filepath = MODULES_DIR / filename
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return {"success": True, "filename": filename, "type": "single"}
        
        elif url.endswith('.zip'):
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
            with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                zip_ref.extractall(TEMP_DIR)
            extracted = list(Path(TEMP_DIR).glob("*.py"))
            if not extracted:
                extracted = list(Path(TEMP_DIR).glob("*/*.py"))
            installed = []
            for py_file in extracted:
                dest = MODULES_DIR / py_file.name
                shutil.move(str(py_file), dest)
                installed.append(py_file.name)
            shutil.rmtree(TEMP_DIR)
            os.unlink(tmp_path)
            return {"success": True, "filenames": installed, "type": "archive"}
        else:
            return {"success": False, "error": "Неподдерживаемый тип файла"}
    except Exception as e:
        logger.error(f"Ошибка установки: {e}")
        return {"success": False, "error": str(e)}

def uninstall_module(module_name):
    module_path = MODULES_DIR / f"{module_name}.py"
    if module_path.exists():
        module_path.unlink()
        return True
    return False

def get_all_modules():
    modules = []
    for py_file in MODULES_DIR.glob("*.py"):
        if py_file.name != "__init__.py":
            modules.append(py_file.stem)
    return modules
