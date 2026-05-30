import subprocess
from i18n import tr
from core.registry import set_registry
from core.system import run_cmd
from modules.utils import make_button


def show_page(window, page_id):
    if "." not in page_id:
        return
    sub = page_id.split(".", 1)[1]
    window.set_page_title("🎮 " + tr("uwp.title") + " > " + tr(f"uwp.{sub}"))
    page = window._pages.get(page_id)
    if not page:
        return
    page.clear()
    page.add_section(tr(f"uwp.{sub}"))
    builder = _BUILDERS.get(sub)
    if builder:
        builder(window, page)
    else:
        window.log(f"Unknown page: {page_id}", "error")


def _b_xbox(window, page):
    page.add_button_row_section(tr("cleaner.event_clear").replace("Clear All Event Logs", "Xbox & Gaming"), [
        make_button("uwp.xbox_install", lambda: _install_xbox_gamebar(window)),
        make_button("uwp.xbox_remove", lambda: _remove_xbox_gamebar(window)),
        make_button("uwp.gamepass", lambda: _install_gamepass(window)),
    ])


def _b_microsoft(window, page):
    page.add_button_row_section(tr("installer.onedrive"), [
        make_button("uwp.yourphone", lambda: _install_your_phone(window)),
    ])


def _b_clipboard(window, page):
    page.add_button_row_section(tr("cleaner.update").replace("Windows Update", "Clipboard & Touch"), [
        make_button("uwp.clipboard_enable", lambda: _clipboard(window, True)),
        make_button("uwp.clipboard_disable", lambda: _clipboard(window, False)),
        make_button("uwp.touch_keyboard", lambda: _touch_keyboard(window)),
    ])


def _b_miracast(window, page):
    page.add_button_row_section(tr("sidebar.system"), [
        make_button("uwp.miracast", lambda: _install_miracast(window)),
    ])


_BUILDERS = {
    "xbox": _b_xbox,
    "microsoft": _b_microsoft,
    "clipboard": _b_clipboard,
    "miracast": _b_miracast,
}


def _install_xbox_gamebar(window):
    run_cmd(["powershell", "-NoProfile", "-Command",
             "Get-AppxPackage -AllUsers *XboxGamingOverlay* | "
             "Add-AppxPackage -Register \"$( $_.InstallLocation )\\AppxManifest.xml\" -DisableDevelopmentMode"])
    window.log("Xbox Game Bar registered (or opened Store link)", "success")


def _remove_xbox_gamebar(window):
    run_cmd(["powershell", "-NoProfile", "-Command",
             "Get-AppxPackage '*XboxGamingOverlay*' | Remove-AppxPackage"])
    window.log("Xbox Game Bar removed", "success")


def _install_gamepass(window):
    subprocess.Popen(["start", "https://www.microsoft.com/en-us/p/xbox-game-pass-for-pc-beta/cfq7ttc0kgq8"],
                     shell=True)
    window.log("Xbox Game Pass page opened", "info")


def _install_your_phone(window):
    subprocess.Popen(["start", "ms-windows-store://pdp/?productid=9NMPJ99VJBWV"], shell=True)
    window.log("Your Phone opened in Store", "info")


def _clipboard(window, enable):
    set_registry(r"HKLM:\SYSTEM\CurrentControlSet\Services\cbdhsvc", "Start", 2 if enable else 4)
    window.log(f"Clipboard {'enabled' if enable else 'disabled'}. Restart required.", "success")


def _touch_keyboard(window):
    set_registry(r"HKLM:\SYSTEM\CurrentControlSet\Services\TabletInputService", "Start", 3)
    set_registry(r"HKLM:\SYSTEM\CurrentControlSet\Services\WpnService", "Start", 3)
    set_registry(r"HKCU:\Software\Policies\Microsoft\Windows\Explorer", "DisableNotificationCenter", 0)
    window.log("Touch Keyboard enabled. Restart required.", "success")


def _install_miracast(window):
    window.log("Open Settings > System > Optional Features > Add 'Wireless Display'.", "warn")
    subprocess.Popen(["start", "ms-settings:optionalfeatures"], shell=True)
