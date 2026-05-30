import subprocess
from i18n import tr
from core.registry import set_hkcr, set_registry, delete_hkcr_tree
from core.system import run_cmd
from modules.utils import make_button, confirm, restart_explorer


def show_page(window, page_id):
    if "." not in page_id:
        return
    sub = page_id.split(".", 1)[1]
    window.set_page_title("📋 " + tr("context_menu.title") + " > " + tr(f"context.{sub}"))
    page = window._pages.get(page_id)
    if not page:
        return
    page.clear()
    page.add_section(tr(f"context.{sub}"))
    builder = _BUILDERS.get(sub)
    if builder:
        builder(window, page)
    else:
        window.log(f"Unknown page: {page_id}", "error")


def _b_ownership(window, page):
    page.add_button_row_section(tr("context.ownership"), [
        make_button("context.ownership_add", lambda: _add_take_ownership(window)),
        make_button("context.ownership_remove", lambda: _remove_take_ownership(window)),
    ])


def _b_shortcuts(window, page):
    page.add_button_row_section(tr("context.shortcuts"), [
        make_button("context.cmd_add", lambda: _add_open_cmd(window)),
        make_button("context.cmd_remove", lambda: _remove_open_cmd(window)),
        make_button("context.copypath_add", lambda: _add_copy_path(window)),
        make_button("context.notepad_add", lambda: _add_notepad(window)),
        make_button("context.shortcuts_remove", lambda: _remove_shortcuts(window)),
    ])


def _b_w11_menu(window, page):
    page.add_button_row_section(tr("context.w11_menu"), [
        make_button("context.classic", lambda: _classic_menu(window)),
        make_button("context.default", lambda: _default_menu(window)),
    ])


_BUILDERS = {
    "ownership": _b_ownership,
    "shortcuts": _b_shortcuts,
    "w11_menu": _b_w11_menu,
}


def _add_take_ownership(window):
    cmd = 'cmd.exe /c takeown /f "%1" && icacls "%1" /grant administrators:F'
    cmd_dir = 'cmd.exe /c takeown /f "%1" /r /d y && icacls "%1" /grant administrators:F /t'
    set_hkcr(r"HKCR:\*\shell\runas", "", "Take Ownership", "String")
    set_hkcr(r"HKCR:\*\shell\runas\command", "", cmd, "String")
    set_hkcr(r"HKCR:\Directory\shell\runas", "", "Take Ownership", "String")
    set_hkcr(r"HKCR:\Directory\shell\runas\command", "", cmd_dir, "String")
    window.log("Take Ownership added to context menu", "success")


def _remove_take_ownership(window):
    for path in [r"*\shell\runas", r"Directory\shell\runas"]:
        try:
            delete_hkcr_tree(path)
        except Exception:
            pass
    window.log("Take Ownership removed from context menu", "success")


def _add_open_cmd(window):
    cmd = 'cmd.exe /s /k pushd "%V"'
    for base in [r"HKCR:\Directory\shell\OpenCmdHere",
                  r"HKCR:\Directory\Background\shell\OpenCmdHere",
                  r"HKCR:\Drive\shell\OpenCmdHere"]:
        set_hkcr(base, "", "Open Command Prompt Here", "String")
        set_hkcr(base + r"\command", "", cmd, "String")
    window.log("Open CMD Here added to context menu", "success")


def _remove_open_cmd(window):
    for path in ["Directory\\shell\\OpenCmdHere", "Directory\\Background\\shell\\OpenCmdHere",
                  "Drive\\shell\\OpenCmdHere"]:
        try:
            delete_hkcr_tree(path)
        except Exception:
            pass
    window.log("Open CMD Here removed from context menu", "success")


def _add_copy_path(window):
    set_hkcr(r"HKCR:\*\shell\copyaspath", "", "Copy as Path", "String")
    set_hkcr(r"HKCR:\*\shell\copyaspath\command", "",
             'powershell.exe -NoProfile -Command "set-clipboard \"%1\""', "String")
    window.log("Copy as Path added to context menu", "success")


def _add_notepad(window):
    set_hkcr(r"HKCR:\*\shell\openwithnotepad", "", "Open with Notepad", "String")
    set_hkcr(r"HKCR:\*\shell\openwithnotepad\command", "", 'notepad.exe "%1"', "String")
    window.log("Open with Notepad added to context menu", "success")


def _remove_shortcuts(window):
    for path in ["*\\shell\\copyaspath", "*\\shell\\openwithnotepad",
                  "Directory\\shell\\OpenCmdHere", "Directory\\Background\\shell\\OpenCmdHere",
                  "Drive\\shell\\OpenCmdHere"]:
        try:
            delete_hkcr_tree(path)
        except Exception:
            pass
    window.log("Shortcuts removed from context menu", "success")


def _classic_menu(window):
    if not confirm(window, "Switch to classic (Windows 10) context menu? Restart required."):
        return
    import winreg
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
            r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32")
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "")
        winreg.CloseKey(key)
    except Exception:
        pass
    window.log("Classic (W10) context menu enabled. Restart Explorer.", "success")
    restart_explorer(window)


def _default_menu(window):
    if not confirm(window, "Restore default (Windows 11) context menu? Restart required."):
        return
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32",
                             0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, "")
        winreg.CloseKey(key)
    except Exception:
        pass
    window.log("Default (W11) context menu restored. Restart Explorer.", "success")
    restart_explorer(window)
