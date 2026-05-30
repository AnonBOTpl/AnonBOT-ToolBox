import winreg
from PyQt6.QtWidgets import QTextEdit
from i18n import tr
from core.registry import set_registry
from core.system import run_cmd
from modules.utils import run_in_thread, make_button, confirm


def show_page(window, page_id):
    if "." not in page_id:
        return
    sub = page_id.split(".", 1)[1]
    window.set_page_title("⚡ " + tr("performance.title") + " > " + tr(f"performance.{sub}"))
    page = window._pages.get(page_id)
    if not page:
        return
    page.clear()
    page.add_section(tr(f"performance.{sub}"))
    builder = _BUILDERS.get(sub)
    if builder:
        builder(window, page)
    else:
        window.log(f"Unknown page: {page_id}", "error")


def _b_visual(window, page):
    page.add_button_row_section(tr("performance.visual"), [
        make_button("performance.visual_best", lambda: _visual_best(window)),
        make_button("performance.visual_default", lambda: _visual_default(window)),
    ])


def _b_cpu(window, page):
    page.add_button_row_section(tr("performance.cpu"), [
        make_button("performance.cpu_programs", lambda: _cpu_scheduling(window, 38)),
        make_button("performance.cpu_background", lambda: _cpu_scheduling(window, 24)),
    ])


def _b_power(window, page):
    page.add_button_row_section(tr("performance.power"), [
        make_button("performance.power_high", lambda: _set_power_plan(window, "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c")),
        make_button("performance.power_ultimate", lambda: _set_power_plan(window, "e9a42b02-d5df-448d-aa00-03f14749eb61")),
        make_button("performance.power_balanced", lambda: _set_power_plan(window, "381b4222-f694-41f0-9685-ff5bb260df2f")),
    ])


def _b_startup(window, page):
    page.add_button_row_section(tr("performance.startup"), [
        make_button("performance.startup_list", lambda: _list_startup(window, page)),
        make_button("performance.startup_disable", lambda: _disable_startup(window)),
    ])


def _b_disk(window, page):
    page.add_button_row_section(tr("performance.disk"), [
        make_button("performance.lastaccess", lambda: _disable_lastaccess(window)),
    ])


_BUILDERS = {
    "visual": _b_visual,
    "cpu": _b_cpu,
    "power": _b_power,
    "startup": _b_startup,
    "disk": _b_disk,
}


def _visual_best(window):
    set_registry(r"HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", 2)
    window.log("Visual effects set to 'Adjust for best performance'. Restart required.", "success")


def _visual_default(window):
    set_registry(r"HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", 0)
    window.log("Visual effects restored to defaults. Restart required.", "success")


def _cpu_scheduling(window, val):
    set_registry(r"HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl", "Win32PrioritySeparation", val)
    window.log(f"CPU scheduling optimized for {'programs' if val == 38 else 'background services'}", "success")


def _set_power_plan(window, guid):
    code, out, err = run_cmd(["powercfg", "-setactive", guid])
    window.log("Power plan changed" if code == 0 else f"Failed to set power plan: {err}",
               "success" if code == 0 else "error")


def _disable_startup(window):
    if not confirm(window, "Disable ALL startup entries? This cannot be undone easily."):
        return
    def task(sig):
        paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
        ]
        count = 0
        for root, subkey in paths:
            try:
                key = winreg.OpenKey(root, subkey, 0, winreg.KEY_READ)
                names = []
                i = 0
                while True:
                    try:
                        name, _, _ = winreg.EnumValue(key, i)
                        names.append(name)
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(key)
                path_str = f"{'HKLM' if root == winreg.HKEY_LOCAL_MACHINE else 'HKCU'}:\\{subkey}"
                for name in names:
                    run_cmd(["reg", "delete", path_str.replace(":", "\\"), "/v", name, "/f"])
                    count += 1
            except Exception:
                pass
        sig.log.emit(f"Disabled {count} startup entries. Restart required.", "success")
    run_in_thread(task, window=window)


def _disable_lastaccess(window):
    set_registry(r"HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem", "NtfsDisableLastAccessUpdate", 1)
    window.log("LastAccess timestamp disabled. Restart required.", "success")


# Profile-friendly wrappers
def _cpu_programs(window):
    _cpu_scheduling(window, 38)


def _cpu_background(window):
    _cpu_scheduling(window, 24)


def _set_power_plan_balanced(window):
    _set_power_plan(window, "381b4222-f694-41f0-9685-ff5bb260df2f")


def _list_startup(window, page):
    lines = []
    try:
        paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", "HKLM:Run"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", "HKCU:Run"),
        ]
        for root, subkey, label in paths:
            key = winreg.OpenKey(root, subkey, 0, winreg.KEY_READ)
            i = 0
            entries = []
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    entries.append((name, value))
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
            lines.append(f"--- {label} ({len(entries)}) ---")
            for name, value in entries:
                lines.append(f"  {name}  ->  {value[:100]}")
        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText("\n".join(lines))
        text.setMinimumHeight(300)
        page.add_widget(text)
        window.log(f"Startup entries displayed ({len(lines)} lines)", "info")
    except Exception as e:
        window.log(f"Failed to read startup: {e}", "error")
