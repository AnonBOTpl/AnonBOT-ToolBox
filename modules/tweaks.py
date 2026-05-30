import os
import subprocess
from i18n import tr
from core.registry import set_registry
from core.system import run_cmd, set_service_startup, get_env
from modules.utils import run_in_thread, make_button, confirm, notify_done, restart_explorer


def show_page(window, page_id):
    if "." not in page_id:
        return
    sub = page_id.split(".", 1)[1]
    window.set_page_title("🔧 " + tr("tweaks.title") + " > " + tr(f"tweaks.{sub}"))
    page = window._pages.get(page_id)
    if not page:
        return
    page.clear()
    page.add_section(tr(f"tweaks.{sub}"))
    builder = _BUILDERS.get(sub)
    if builder:
        builder(window, page)
    else:
        window.log(f"Unknown page: {page_id}", "error")
        return
    window.log(f"{tr(f'tweaks.{sub}')} page loaded")


def _b_action_center(window, page):
    page.add_button_row_section(tr("tweaks.action_center"), [
        make_button("tweaks.action_center_enable", lambda: _action_center(window, True)),
        make_button("tweaks.action_center_disable", lambda: _action_center(window, False)),
        make_button("tweaks.spooler_enable", lambda: set_service_startup("Spooler", "Auto")),
        make_button("tweaks.spooler_disable", lambda: set_service_startup("Spooler", "Disabled")),
    ])


def _b_hibernation(window, page):
    page.add_button_row_section(tr("tweaks.hibernation"), [
        make_button("tweaks.hibernation_disable", lambda: _hibernation(window, False)),
        make_button("tweaks.hibernation_enable", lambda: _hibernation(window, True)),
        make_button("tweaks.sysmain_disable", lambda: set_service_startup("Sysmain", "Disabled")),
        make_button("tweaks.sysmain_enable", lambda: set_service_startup("Sysmain", "Auto")),
    ])


def _b_pagefile(window, page):
    page.add_button_row_section(tr("tweaks.pagefile"), [
        make_button("tweaks.pagefile_none", lambda: _pagefile(window, "none")),
        make_button("tweaks.pagefile_256", lambda: _pagefile(window, 256)),
        make_button("tweaks.pagefile_3gb", lambda: _pagefile(window, 3000)),
        make_button("tweaks.pagefile_4gb", lambda: _pagefile(window, 4000)),
        make_button("tweaks.pagefile_8gb", lambda: _pagefile(window, 8000)),
        make_button("tweaks.pagefile_16gb", lambda: _pagefile(window, 16000)),
        make_button("tweaks.pagefile_system", lambda: _pagefile(window, "system")),
    ])


def _b_taskbar(window, page):
    page.add_button_row_section(tr("tweaks.taskbar"), [
        make_button("tweaks.transparency_enable", lambda: _transparency(window, True)),
        make_button("tweaks.transparency_disable", lambda: _transparency(window, False)),
    ])


def _b_w11(window, page):
    page.add_button_row_section(tr("tweaks.w11"), [
        make_button("tweaks.copilot_disable", lambda: _disable_copilot(window)),
        make_button("tweaks.recall_disable", lambda: _disable_recall(window)),
        make_button("tweaks.widgets_disable", lambda: _disable_widgets(window)),
        make_button("tweaks.chat_disable", lambda: _disable_chat(window)),
        make_button("tweaks.taskbar_left", lambda: _taskbar_align(window, 0)),
        make_button("tweaks.taskbar_center", lambda: _taskbar_align(window, 1)),
        make_button("tweaks.start_ads_disable", lambda: _disable_start_ads(window)),
        make_button("tweaks.bing_disable", lambda: _disable_bing_search(window)),
    ])


def _b_windows_update(window, page):
    page.add_button_row_section(tr("tweaks.windows_update"), [
        make_button("tweaks.updates_pause", lambda: _pause_updates(window)),
        make_button("tweaks.driver_updates", lambda: _disable_driver_updates(window)),
        make_button("tweaks.defer_features", lambda: _defer_feature_updates(window)),
        make_button("tweaks.pause_quality", lambda: _pause_quality_updates(window)),
    ])


def _b_winre(window, page):
    from PyQt6.QtWidgets import QLabel
    info = QLabel(
        "WinRE allows you to boot into recovery mode to repair Windows.\n\n"
        "Use reagentc /info to check current status."
    )
    info.setWordWrap(True)
    info.setStyleSheet("font-size: 13px; padding: 0 0 16px 0;")
    page.add_widget(info)
    page.add_button_row_section("WinRE", [
        make_button("tweaks.winre_page", lambda: _check_winre(window)),
        make_button("tweaks.winre_download", lambda: _download_winre(window)),
        make_button("tweaks.dotnet_35_enable", lambda: _enable_netfx35_standalone(window)),
    ])


def _b_dotnet(window, page):
    page.add_button_row_section(tr("tweaks.dotnet"), [
        make_button("tweaks.dotnet_35_enable", lambda: _enable_netfx35(window)),
        make_button("tweaks.dotnet_force4", lambda: _netfx_force4(window, True)),
        make_button("tweaks.dotnet_allow35", lambda: _netfx_force4(window, False)),
    ])


_BUILDERS = {
    "action_center": _b_action_center,
    "hibernation": _b_hibernation,
    "pagefile": _b_pagefile,
    "taskbar": _b_taskbar,
    "w11": _b_w11,
    "windows_update": _b_windows_update,
    "winre": _b_winre,
    "dotnet": _b_dotnet,
}


def _action_center(window, enable):
    if enable:
        set_registry("HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\PushNotifications", "ToastEnabled", 1)
        set_service_startup("WerSvc", "Demand")
        set_service_startup("WpnService", "Auto")
        set_service_startup("WpnUserService", "Auto")
        set_service_startup("SENS", "Auto")
        set_registry("HKCU:\\Software\\Policies\\Microsoft\\Windows\\Explorer", "DisableNotificationCenter", 0)
        window.log("Action Center enabled. Restart required.", "success")
    else:
        set_registry("HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\PushNotifications", "ToastEnabled", 0)
        set_service_startup("WpnService", "Disabled")
        set_service_startup("SENS", "Disabled")
        set_registry("HKCU:\\Software\\Policies\\Microsoft\\Windows\\Explorer", "DisableNotificationCenter", 1)
        window.log("Action Center disabled. Restart required.", "success")


def _hibernation(window, enable):
    if enable:
        run_cmd(["powercfg", "/h", "on"])
        run_cmd(["powercfg", "/h", "/type", "full"])
        window.log("Hibernation enabled", "success")
    else:
        run_cmd(["powercfg", "/h", "off"])
        window.log("Hibernation disabled", "success")


def _pagefile(window, size):
    if size == "none" and not confirm(window, "Disable pagefile entirely? This may cause instability on low RAM systems."):
        return
    path = r"HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
    if size == "none":
        set_registry(path, "PagingFiles", ["C:\\pagefile.sys 1 1"], "MultiString")
        window.log("Pagefile disabled. Restart required.", "warn")
    elif size == "system":
        set_registry(path, "PagingFiles", ["C:\\pagefile.sys 0 0"], "MultiString")
        window.log("Pagefile set to system managed. Restart required.", "success")
    else:
        set_registry(path, "PagingFiles", [f"C:\\pagefile.sys {size} {size}"], "MultiString")
        window.log(f"Pagefile set to {size}MB. Restart required.", "success")


def _transparency(window, enable):
    val = 1 if enable else 0
    set_registry(r"HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "UseOLEDTaskbarTransparency", val)
    set_registry(r"HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "EnableTransparency", val)
    window.log("Transparency " + ("enabled" if enable else "disabled"), "success")
    restart_explorer(window)


def _disable_copilot(window):
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot", "TurnOffWindowsCopilot", 1)
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\Explorer", "DisableCopilot", 1)
    window.log("Copilot disabled", "success")


def _disable_recall(window):
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsAI", "AllowRecallEnablement", 0)
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsAI", "DisableAIDataAnalysis", 1)
    window.log("Recall disabled", "success")


def _disable_widgets(window):
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Dsh", "AllowNewsAndInterests", 0)
    window.log("Widgets disabled", "success")


def _disable_chat(window):
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Chat", "ChatIcon", 3)
    window.log("Chat disabled", "success")


def _taskbar_align(window, align):
    set_registry(r"HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "TaskbarAl", align)
    window.log("Restarting Explorer...", "warn")
    restart_explorer(window)


def _disable_start_ads(window):
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\Explorer", "DisableSearchWebResultsInStart", 1)
    window.log("Start ads disabled", "success")


def _disable_bing_search(window):
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\Explorer", "DisableSearchBoxSuggestions", 1)
    window.log("Bing search disabled", "success")


def _pause_updates(window):
    base = r"HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings"
    set_registry(base, "PauseFeatureUpdatesStartTime", "2019-07-28T10:38:56Z", "String")
    set_registry(base, "PauseQualityUpdatesStartTime", "2019-07-28T10:38:56Z", "String")
    set_registry(base, "PauseUpdatesExpiryTime", "2050-01-01T10:38:56Z", "String")
    set_registry(base, "PauseFeatureUpdatesEndTime", "2050-01-01T10:38:56Z", "String")
    set_registry(base, "PauseQualityUpdatesEndTime", "2050-01-01T10:38:56Z", "String")
    pol = r"HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings\UpdatePolicy\Settings"
    set_registry(pol, "PausedFeatureStatus", 1)
    set_registry(pol, "PausedQualityStatus", 1)
    window.log("Windows Update paused until 2050!", "success")


def _disable_driver_updates(window):
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\Device Metadata", "PreventDeviceMetadataFromNetwork", 1)
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\DriverSearching", "SearchOrderConfig", 0)
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\DriverSearching", "DriverSearchPromptSelection", "NeverCheck")
    window.log("Driver updates via Windows Update disabled", "success")


def _defer_feature_updates(window):
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate", "DeferFeatureUpdates", 1)
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate", "DeferFeatureUpdatesPeriodInDays", 365)
    window.log("Feature updates deferred for 365 days", "success")


def _pause_quality_updates(window):
    set_registry(r"HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings", "PauseQualityUpdatesStartTime", "2026-06-01T00:00:00Z", "String")
    set_registry(r"HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings", "PauseQualityUpdatesEndTime", "2050-01-01T00:00:00Z", "String")
    window.log("Quality updates paused until 2050", "success")


def _netfx_force4(window, enable):
    val = 1 if enable else 0
    set_registry(r"HKLM:\SOFTWARE\Microsoft\.NETFramework", "OnlyUseLatestCLR", val)
    set_registry(r"HKLM:\SOFTWARE\WOW6432Node\Microsoft\.NETFramework", "OnlyUseLatestCLR", val)
    window.log(f".NET Framework forced to 4.x = {enable}. Restart required.", "success")


def _enable_netfx35(window):
    def task(sig):
        sig.status.emit("downloading .NET 3.5...")
        sig.log.emit("Downloading .NET 3.5...", "info")
        code, out, err = run_cmd([
            "dism", "/online", "/enable-feature",
            "/featurename:NetFX3", "/All",
            "/Source:windows", "/LimitAccess", "/quiet"
        ], timeout=300)
        if code == 0:
            _netfx_force4(window, False)
            sig.log.emit(".NET 3.5 enabled. Restart required.", "success")
        else:
            sig.log.emit(f".NET 3.5 install failed: {err}", "error")
        notify_done(window, ".NET Framework", ".NET 3.5 installation completed")
    run_in_thread(task, window=window)


def _enable_netfx35_standalone(window):
    _enable_netfx35(window)


def _check_winre(window):
    code, out, err = run_cmd(["reagentc", "/info"])
    window.log("WinRE Status:", "info")
    for line in out.split("\n"):
        if line.strip():
            window.log(line.strip(), "info")


def _download_winre(window):
    def task(sig):
        sig.status.emit("Checking WinRE...")
        import winreg as wr
        try:
            key = wr.OpenKey(wr.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
            build, _ = wr.QueryValueEx(key, "CurrentBuild")
            wr.CloseKey(key)
        except Exception:
            sig.log.emit("Cannot read build number", "error")
            return
        temp_dir = os.path.join(get_env("TEMP", os.path.expanduser("~\\Temp")), "ghost_winre")
        os.makedirs(temp_dir, exist_ok=True)
        try:
            sig.log.emit(f"Running reagentc /enable for build {build}...", "info")
            run_cmd(["reagentc", "/enable"])
            sig.log.emit("WinRE checked. Use DISM /Export-Image from install.wim if needed.", "success")
        except Exception as e:
            sig.log.emit(f"WinRE operation failed: {e}", "error")
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
    run_in_thread(task, window=window)
