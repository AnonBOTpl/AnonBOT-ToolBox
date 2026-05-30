import winreg
import ctypes
import os
import json
import datetime
import threading
from typing import Optional


# Registry root key mapping
ROOT_KEYS = {
    "HKLM": winreg.HKEY_LOCAL_MACHINE,
    "HKCU": winreg.HKEY_CURRENT_USER,
    "HKCR": winreg.HKEY_CLASSES_ROOT,
    "HKU":  winreg.HKEY_USERS,
    "HKCC": winreg.HKEY_CURRENT_CONFIG,
}

# Registry value type mapping
VALUE_TYPES = {
    "String": winreg.REG_SZ,
    "ExpandString": winreg.REG_EXPAND_SZ,
    "MultiString": winreg.REG_MULTI_SZ,
    "DWord": winreg.REG_DWORD,
    "QWord": winreg.REG_QWORD,
    "Binary": winreg.REG_BINARY,
}


def _parse_path(full_path):
    path = full_path.replace("/", "\\")
    if ":" in path:
        root_key, subkey = path.split(":", 1)
        root_key = root_key.upper()
    else:
        root_key = "HKLM"
        subkey = path
    subkey = subkey.strip("\\")
    hkey = ROOT_KEYS.get(root_key)
    if hkey is None:
        raise ValueError(f"Unknown root key: {root_key}")
    return hkey, subkey


def _create_path_recursive(hkey, subkey):
    parts = [p for p in subkey.split("\\") if p]
    for i, part in enumerate(parts):
        parent_path = "\\".join(parts[:i]) if i > 0 else ""
        try:
            if parent_path:
                key = winreg.OpenKey(hkey, parent_path, 0, winreg.KEY_READ)
            else:
                key = winreg.OpenKey(hkey, "", 0, winreg.KEY_READ)
            winreg.CloseKey(key)
        except FileNotFoundError:
            if parent_path:
                parent_key = winreg.OpenKey(hkey, parent_path, 0, winreg.KEY_WRITE)
            else:
                parent_key = hkey
            winreg.CreateKey(parent_key, part)
            if parent_path:
                winreg.CloseKey(parent_key)


def set_registry(path: str, name: str, value, type_name: str = "DWord") -> bool:
    if path.upper().startswith("HKCR:"):
        return set_hkcr(path, name, value, type_name)
    try:
        backup_snapshot_entry(path, name)
        hkey, subkey = _parse_path(path)
        reg_type = VALUE_TYPES.get(type_name, winreg.REG_SZ)
        try:
            key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ)
            winreg.CloseKey(key)
        except FileNotFoundError:
            _create_path_recursive(hkey, subkey)
        key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, name, 0, reg_type, value)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        return False


def remove_registry(path: str, name: str) -> bool:
    if path.upper().startswith("HKCR:"):
        return remove_hkcr(path, name)
    try:
        hkey, subkey = _parse_path(path)
        key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_WRITE)
        winreg.DeleteValue(key, name)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def get_registry(path: str, name: str, default=None):
    try:
        hkey, subkey = _parse_path(path)
        key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        return value
    except Exception:
        return default


def _strip_hkcr(path: str) -> str:
    _, subkey = _parse_path(path)
    return subkey


def set_hkcr(path: str, name: str, value, type_name: str = "String") -> bool:
    try:
        backup_snapshot_entry(path, name)
        subkey = _strip_hkcr(path)
        reg_type = VALUE_TYPES.get(type_name, winreg.REG_SZ)
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, subkey)
        winreg.SetValueEx(key, name, 0, reg_type, value)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def remove_hkcr(path: str, name: str) -> bool:
    try:
        subkey = _strip_hkcr(path)
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, subkey, 0, winreg.KEY_WRITE)
        try:
            orig = winreg.QueryValueEx(key, name)
            backup_snapshot_entry(path, name, orig[0], _type_name_for_value(orig[0]))
        except FileNotFoundError:
            pass
        winreg.DeleteValue(key, name)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def delete_hkcr_tree(subkey: str) -> bool:
    try:
        parent_path = "\\".join(subkey.split("\\")[:-1]) if "\\" in subkey else ""
        leaf = subkey.split("\\")[-1]
        if parent_path:
            key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, parent_path, 0, winreg.KEY_WRITE)
        else:
            key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "", 0, winreg.KEY_WRITE)
        winreg.DeleteKey(key, leaf)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


# --- Backup / Restore system ---

_SESSION_BACKUPS = {}
_backup_lock = threading.Lock()


def _type_name_for_value(value):
    if isinstance(value, int):
        return "DWord"
    elif isinstance(value, str):
        return "String"
    elif isinstance(value, bytes):
        return "Binary"
    return "String"


def backup_snapshot_entry(path, name, value=None, type_name=None, module_name=None):
    if module_name is None:
        module_name = _caller_module()
    if value is None:
        value = get_registry(path, name)
        if value is None:
            return
    if type_name is None:
        type_name = _type_name_for_value(value)
    with _backup_lock:
        if module_name not in _SESSION_BACKUPS:
            _SESSION_BACKUPS[module_name] = []
        _SESSION_BACKUPS[module_name].append({
            "path": path, "name": name, "value": value, "type": type_name,
        })


def _caller_module():
    import sys
    try:
        f = sys._getframe(2)
        name = f.f_globals.get("__name__", "")
        if name.startswith("modules.") or name.startswith("core."):
            return name.split(".")[-1]
    except Exception:
        pass
    return "unknown"


def save_snapshot(module):
    with _backup_lock:
        if module not in _SESSION_BACKUPS or not _SESSION_BACKUPS[module]:
            return None
        entries = _SESSION_BACKUPS.pop(module, [])
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")
    os.makedirs(backup_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.join(backup_dir, f"{ts}_{module}.json")
    data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "module": module,
        "entries": entries,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path


def get_snapshots():
    backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")
    if not os.path.exists(backup_dir):
        return []
    snapshots = []
    for fname in sorted(os.listdir(backup_dir), reverse=True):
        if fname.endswith(".json"):
            path = os.path.join(backup_dir, fname)
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                snapshots.append({"file": path, "data": data})
            except Exception:
                pass
    return snapshots


def restore_snapshot(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    restored = 0
    for entry in data["entries"]:
        try:
            set_registry(entry["path"], entry["name"], entry["value"], entry["type"])
            restored += 1
        except Exception:
            pass
    return restored
