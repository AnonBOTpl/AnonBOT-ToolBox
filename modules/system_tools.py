import subprocess
import os
from i18n import tr
from core.registry import set_registry
from core.system import run_cmd, run_visible
from modules.utils import run_in_thread, make_button, restart_explorer


def show_page(window, page_id):
    if "." not in page_id:
        return
    sub = page_id.split(".", 1)[1]
    window.set_page_title("⚙ " + tr("system_tools.title") + " > " + tr(f"system.{sub}"))
    page = window._pages.get(page_id)
    if not page:
        return
    page.clear()
    page.add_section(tr(f"system.{sub}"))
    builder = _BUILDERS.get(sub)
    if builder:
        builder(window, page)
    else:
        window.log(f"Unknown page: {page_id}", "error")


def _b_benchmark(window, page):
    page.add_button_row_section(tr("system.disk_bench"), [
        make_button("system.bench_c", lambda: _benchmark_disk(window, "C")),
        make_button("system.bench_d", lambda: _benchmark_disk(window, "D")),
        make_button("system.bench_custom", lambda: _benchmark_prompt(window)),
    ])


def _b_users(window, page):
    page.add_button_row_section(tr("system.users"), [
        make_button("system.user_accounts", lambda: subprocess.Popen(["control", "userpasswords2"])),
        make_button("system.change_admin", lambda: subprocess.Popen(["mmc.exe", "compmgmt.msc"])),
    ])


def _b_gaming(window, page):
    page.add_button_row_section(tr("system.gaming"), [
        make_button("system.gaming_tweaks", lambda: _gaming_tweaks(window)),
        make_button("system.game_clients", lambda: subprocess.Popen(
            ["start", "https://store.steampowered.com/about/"], shell=True)),
    ])


def _b_audio(window, page):
    page.add_button_row_section(tr("system.audio"), [
        make_button("system.sound_settings", lambda: subprocess.Popen(["start", "ms-settings:sound"], shell=True)),
        make_button("system.volume_mixer", lambda: subprocess.Popen(["sndvol"])),
    ])


def _b_cmd_schemes(window, page):
    page.add_button_row_section(tr("system.cmd_schemes"), [
        make_button("system.cmd_dracula", lambda: _cmd_color_scheme(window, "Dracula.itermcolors")),
        make_button("system.cmd_solarized", lambda: _cmd_color_scheme(window, "solarized_dark.itermcolors")),
        make_button("system.cmd_onehalf", lambda: _cmd_color_scheme(window, "OneHalfDark.itermcolors")),
        make_button("system.cmd_campbell", lambda: _cmd_color_scheme(window, "campbell.ini")),
        make_button("system.cmd_more", lambda: subprocess.Popen(
            ["start", "https://github.com/microsoft/terminal/tree/main/samples/color schemes"], shell=True)),
    ])


def _b_explorer(window, page):
    page.add_button_row_section(tr("system.explorer"), [
        make_button("system.restart_explorer", lambda: _restart_explorer(window)),
        make_button("system.restart_start", lambda: _restart_start(window)),
        make_button("system.cleanmgr", lambda: _run_cleanmgr(window)),
        make_button("system.sfc", lambda: _run_sfc(window)),
        make_button("system.dism", lambda: _run_dism(window)),
    ])


_BUILDERS = {
    "benchmark": _b_benchmark,
    "users": _b_users,
    "gaming": _b_gaming,
    "audio": _b_audio,
    "cmd_schemes": _b_cmd_schemes,
    "explorer": _b_explorer,
}


def _benchmark_disk(window, drive):
    def task(sig):
        sig.log.emit(f"Benchmarking drive {drive}:... (this takes a moment)", "info")
        run_cmd(["winsat", "disk", "-drive", drive], timeout=120)
        sig.log.emit(f"Benchmark for {drive}: completed.", "success")
        notify_done(window, "Benchmark", f"Benchmark for {drive}: completed")
    run_in_thread(task, window=window)


def _benchmark_prompt(window):
    from PyQt6.QtWidgets import QInputDialog
    from i18n import tr
    drive, ok = QInputDialog.getText(window, tr("system.benchmark"), tr("system.enter_drive"))
    if ok and drive and len(drive.strip()) == 1 and drive.strip().isalpha():
        _benchmark_disk(window, drive.strip().upper())


def _gaming_tweaks(window):
    set_registry(r"HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl", "Win32PrioritySeparation", 38)
    set_registry(r"HKCU:\System\GameConfigStore", "GameDVR_Enabled", 1)
    set_registry(r"HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR", "AppCaptureEnabled", 1)
    run_cmd(["powercfg", "-setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"])
    window.log("Gaming tweaks applied. Restart may be needed.", "success")


def _cmd_color_scheme(window, scheme_file):
    ct = os.path.join(os.environ.get("ProgramData", "C:\\ProgramData"), "Microsoft", "colortool", "colortool.exe")
    if not os.path.exists(ct):
        window.log("Colortool not installed. Install from GitHub or Windows Terminal.", "warn")
        return
    run_cmd([ct, "-b", scheme_file])
    window.log(f"CMD color scheme changed to {scheme_file}. Restart CMD.", "success")


def _restart_explorer(window):
    restart_explorer(window)


def _restart_start(window):
    run_cmd(["taskkill", "/f", "/im", "StartMenuExperienceHost.exe"])
    window.log("Start Menu restarted", "success")


def _run_cleanmgr(window):
    subprocess.Popen(["cleanmgr.exe", "/sageset:1"])
    window.log("Disk Cleanup opened", "info")


def _run_sfc(window):
    window.log("Opening SFC /scannow in a new console window...", "info")
    run_visible(["sfc", "/scannow"], "SFC /scannow")


def _run_dism(window):
    window.log("Opening DISM in a new console window...", "info")
    run_visible(["dism", "/online", "/cleanup-image", "/restorehealth"], "DISM RestoreHealth")
