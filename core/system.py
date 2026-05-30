import ctypes
import platform
import subprocess
import os
import shutil
import winreg


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def get_os_info():
    version = platform.version()
    edition = platform.win32_edition()
    key = None
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
                             0, winreg.KEY_READ)
        display_version = winreg.QueryValueEx(key, "DisplayVersion")[0]
        current_build = winreg.QueryValueEx(key, "CurrentBuild")[0]
        release_id = winreg.QueryValueEx(key, "ReleaseId")[0]
    except Exception:
        display_version = "Unknown"
        current_build = "0"
        release_id = ""
    finally:
        if key is not None:
            try:
                winreg.CloseKey(key)
            except Exception:
                pass

    is_w11 = int(current_build) >= 22000
    return {
        "os": "Windows 11" if is_w11 else "Windows 10",
        "display_version": display_version,
        "build": current_build,
        "release_id": release_id,
        "arch": platform.machine(),
        "edition": edition or "Unknown",
        "version": version,
    }


def get_env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def run_cmd(args, timeout=120):
    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        return proc.returncode, proc.stdout, proc.stderr
    except Exception:
        return -1, "", ""


def run_powershell(script, timeout=120):
    ps = "pwsh.exe" if shutil.which("pwsh.exe") else "powershell.exe"
    return run_cmd(
        [ps, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        timeout=timeout
    )


def set_service_startup(service_name: str, start_type: str) -> bool:
    start_map = {
        "Auto": "auto",
        "Demand": "demand",
        "Disabled": "disabled",
    }
    mapped = start_map.get(start_type)
    if not mapped:
        return False
    code, _, _ = run_cmd(["sc.exe", "config", service_name, f"start={mapped}"])
    if code == 0 and mapped != "disabled":
        run_cmd(["net.exe", "start", service_name])
    elif mapped == "disabled":
        run_cmd(["net.exe", "stop", service_name])
    return code == 0


def is_dotnet_available(version: str) -> bool:
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             rf"SOFTWARE\Microsoft\NET Framework Setup\NDP\{version}",
                             0, winreg.KEY_READ)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def get_system_drive() -> str:
    return os.environ.get("SystemDrive", "C:")


def run_visible(args, title="Command"):
    try:
        cmd = ["cmd", "/k"] + args
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.lpTitle = title
        return subprocess.Popen(
            cmd,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            startupinfo=startupinfo
        )
    except Exception:
        return None


def notify(title, message):
    import base64
    safe_title = title.replace("'", "''").replace("`", "``").replace("$(", "`$(")
    safe_message = message.replace("'", "''").replace("`", "``").replace("$(", "`$(")
    script = (
        f"Add-Type -AssemblyName System.Windows.Forms; "
        f"$n = New-Object System.Windows.Forms.NotifyIcon; "
        f"$n.Icon = [System.Drawing.SystemIcons]::Information; "
        f"$n.Visible = $true; "
        f"$n.ShowBalloonTip(4000, '{safe_title}', '{safe_message}', "
        f"[System.Windows.Forms.ToolTipIcon]::Info)"
    )
    run_powershell(script)
