import winreg
import subprocess
import webbrowser
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from i18n import tr
from core.registry import set_registry, remove_registry
from core.system import run_cmd
from modules.utils import run_in_thread, make_button, notify_done


def show_page(window, page_id):
    if "." not in page_id:
        return
    sub = page_id.split(".", 1)[1]
    window.set_page_title("🎨 " + tr("personalize.title") + " > " + tr(f"personalize.{sub}"))
    page = window._pages.get(page_id)
    if not page:
        return
    page.clear()
    page.add_section(tr(f"personalize.{sub}"))
    builder = _BUILDERS.get(sub)
    if builder:
        builder(window, page)
    else:
        window.log(f"Unknown page: {page_id}", "error")


def _b_dwm(window, page):
    page.add_button_row_section(tr("personalize.dwm_title"), [
        make_button("personalize.dark_purple_dark", lambda: _dwm_scheme(window, 2)),
        make_button("personalize.dark_purple_white", lambda: _dwm_scheme(window, 3)),
        make_button("personalize.light_purple_white", lambda: _dwm_scheme(window, 4)),
        make_button("personalize.light_purple_dark_taskbar", lambda: _dwm_scheme(window, 5)),
        make_button("personalize.light_purple_dark_explorer_dark", lambda: _dwm_scheme(window, 6)),
        make_button("personalize.light_purple_dark_explorer_white", lambda: _dwm_scheme(window, 7)),
        make_button("personalize.win10_light", lambda: _dwm_scheme(window, 8)),
        make_button("personalize.win10_dark", lambda: _dwm_scheme(window, 9)),
    ])


def _b_themes(window, page):
    page.add_button_row_section(tr("personalize.theme_tools"), [
        make_button("personalize.secure_uxtheme", lambda: _install_theme_tool(window, "secureuxtheme")),
        make_button("personalize.windhawk", lambda: _install_theme_tool(window, "windhawk")),
        make_button("personalize.search_themes", lambda: _open_themes(window)),
    ])
    page.add_section(tr("personalize.theme_inspiration"))
    info_label = QLabel(tr("personalize.theme_info"))
    info_label.setWordWrap(True)
    info_label.setStyleSheet("font-size: 12px; padding: 8px; color: #94a3b8;")
    page.add_widget(info_label)


def _b_wallpapers(window, page):
    page.add_button_row_section(tr("personalize.wallpaper_title"), [
        make_button("personalize.search_wallpapers", lambda: _open_wallpapers(window)),
    ])
    info = QLabel(tr("personalize.wallpaper_soon"))
    info.setWordWrap(True)
    info.setStyleSheet("font-size: 13px; padding: 16px; color: #94a3b8;")
    info.setAlignment(Qt.AlignmentFlag.AlignCenter)
    page.add_widget(info)


_BUILDERS = {
    "dwm": _b_dwm,
    "themes": _b_themes,
    "wallpapers": _b_wallpapers,
}


def _dwm_scheme(window, scheme):
    dwm = r"HKCU:\Software\Microsoft\Windows\DWM"
    theme = r"HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    accent = r"HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Accent"
    purple_accent = 984850
    purple_inactive = 4278452741

    for k in ["Composition", "AccentColorInactive", "ColorizationColor", "ColorizationColorBalance",
              "ColorizationAfterglow", "ColorizationAfterglowBalance", "ColorizationBlurBalance",
              "EnableWindowColorization", "ColorizationGlassAttribute", "AccentColor",
              "ColorPrevalence", "EnableAeroPeek"]:
        remove_registry(dwm, k)
    for k in ["ColorPrevalence", "EnableTransparency", "AppsUseLightTheme", "SystemUsesLightTheme"]:
        remove_registry(theme, k)
    for k in ["StartColorMenu", "AccentColorMenu", "AccentPalette"]:
        remove_registry(accent, k)

    if scheme == 8:
        window.log("Reset to Windows 10 Default Light", "success"); return
    if scheme == 9:
        set_registry(theme, "AppsUseLightTheme", 0); set_registry(theme, "SystemUsesLightTheme", 0)
        window.log("Reset to Windows 10 Default Dark", "success"); return

    set_registry(dwm, "Composition", 1); set_registry(dwm, "ColorPrevalence", 1)
    set_registry(dwm, "EnableAeroPeek", 1); set_registry(theme, "ColorPrevalence", 0)
    set_registry(theme, "EnableTransparency", 1); set_registry(accent, "StartColorMenu", 2164772)
    set_registry(accent, "AccentColorMenu", 4279174930)

    schemes = {
        2: {"AccentColorInactive": purple_inactive, "AccentColor": purple_accent, "AppsUseLightTheme": 0, "SystemUsesLightTheme": 0},
        3: {"AccentColorInactive": purple_inactive, "AccentColor": purple_accent, "AppsUseLightTheme": 0, "SystemUsesLightTheme": 1},
        4: {"AccentColorInactive": purple_accent, "AccentColor": purple_accent, "AppsUseLightTheme": 1, "SystemUsesLightTheme": 1, "AccentColorMenu": 4287768686},
        5: {"AccentColorInactive": 3148067, "AccentColor": purple_accent, "AppsUseLightTheme": 1, "SystemUsesLightTheme": 0, "AccentColorMenu": 4287768686},
        6: {"AccentColorInactive": 3148067, "AccentColor": purple_accent, "AppsUseLightTheme": 0, "SystemUsesLightTheme": 0, "AccentColorMenu": 4287768686},
        7: {"AccentColorInactive": 3148067, "AccentColor": purple_accent, "AppsUseLightTheme": 0, "SystemUsesLightTheme": 1, "AccentColorMenu": 4287768686},
    }
    s = schemes.get(scheme, {})
    for k, v in s.items():
        if k in ("AppsUseLightTheme", "SystemUsesLightTheme"):
            set_registry(theme, k, v)
        elif k in ("AccentColorMenu", "StartColorMenu"):
            set_registry(accent, k, v)
        else:
            set_registry(dwm, k, v)
    window.log(f"Color scheme applied (scheme {scheme})", "success")


def _install_theme_tool(window, tool):
    winget_ids = {"secureuxtheme": "namazso.SecureUXTheme", "windhawk": "RamenSoftware.Windhawk"}
    winget_id = winget_ids.get(tool)
    if not winget_id:
        window.log(f"Unknown theme tool: {tool}", "error")
        return
    def task(sig):
        sig.status.emit(f"Installing {tool}...")
        sig.busy.emit(True, f"Installing {tool}...")
        try:
            subprocess.run(["winget", "install", "--exact", "--silent", winget_id], check=True, timeout=120)
            sig.log.emit(f"{tool} installed successfully!", "success")
            notify_done(window, tool, "installed successfully")
        except Exception as e:
            sig.log.emit(f"Failed to install {tool}: {e}", "error")
        finally:
            sig.busy.emit(False, "")
            sig.status.emit(tr("app.status.ready"))
    run_in_thread(task, window=window)


def _open_themes(window):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
                             0, winreg.KEY_READ)
        dv = winreg.QueryValueEx(key, "DisplayVersion")[0]
        winreg.CloseKey(key)
    except Exception:
        dv = "25H2"
    major = dv[:2] if len(dv) >= 2 else "25"
    tag = f"{major}H2"
    url = f"https://www.deviantart.com/tag/{tag}"
    webbrowser.open(url)
    window.log(f"Opening {url}", "info")


def _open_wallpapers(window):
    url = "https://www.deviantart.com/tag/wallpapers"
    webbrowser.open(url)
    window.log(f"Opening {url}", "info")
