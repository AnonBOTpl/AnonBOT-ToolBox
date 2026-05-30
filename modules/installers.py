import os
import json
import subprocess
import shutil
import urllib.request
import urllib.error
from i18n import tr
from core.system import run_cmd, get_env
from core.download import DownloadThread
from modules.utils import make_button, run_in_thread, notify_done


def _get_software_config():
    base = os.path.dirname(os.path.dirname(__file__))
    urls_path = os.path.join(base, "urls.json")
    try:
        with open(urls_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def show_page(window, page_id):
    if "." not in page_id:
        return
    sub = page_id.split(".", 1)[1]
    window.set_page_title("📦 " + tr("installers.title") + " > " + tr(f"installer.{sub}"))
    page = window._pages.get(page_id)
    if not page:
        return
    page.clear()
    page.add_section(tr(f"installer.{sub}"))
    builder = _BUILDERS.get(sub)
    if builder:
        builder(window, page)
    else:
        window.log(f"Unknown page: {page_id}", "error")


def _b_browsers(window, page):
    page.add_button_row_section(tr("installer.section.browsers"), [
        make_button("installer.chrome", lambda: _install_software(window, "googleChrome")),
        make_button("installer.firefox", lambda: _install_software(window, "firefox")),
        make_button("installer.brave", lambda: _install_software(window, "brave")),
        make_button("installer.edge", lambda: _install_software(window, "edgeChromium")),
    ])


def _b_media(window, page):
    page.add_button_row_section(tr("installer.section.media"), [
        make_button("installer.potplayer", lambda: _install_software(window, "potplayer")),
        make_button("installer.ytdlp", lambda: _install_software(window, "ytDlp")),
    ])

def _b_utilities(window, page):
    page.add_button_row_section(tr("installer.section.utilities"), [
        make_button("installer.everything", lambda: _install_software(window, "everything")),
        make_button("installer.treesize", lambda: _install_software(window, "treesize")),
        make_button("installer.crystaldiskinfo", lambda: _install_software(window, "crystalDiskInfo")),
        make_button("installer.hwinfo", lambda: _install_software(window, "hwinfo")),
        make_button("installer.notepadpp", lambda: _install_software(window, "notepadpp")),
        make_button("installer.windirstat", lambda: _install_software(window, "windirstat")),
        make_button("installer.7zip", lambda: _install_software(window, "7zip")),
    ])


def _b_drivers(window, page):
    page.add_button_row_section(tr("installer.section.drivers"), [
        make_button("installer.drivereasy", lambda: _install_software(window, "driverEasy")),
        make_button("installer.iobit", lambda: _install_software(window, "iobitDriverBooster")),
    ])


def _b_microsoft(window, page):
    page.add_button_row_section(tr("installer.section.microsoft"), [
        make_button("installer.vcredist", lambda: _install_software(window, "vcredistAIO")),
        make_button("installer.directx", lambda: _install_software(window, "directX")),
        make_button("installer.onedrive", lambda: _install_software(window, "oneDrive")),
    ])


def _b_devtools(window, page):
    page.add_button_row_section(tr("installer.section.devtools"), [
        make_button("installer.git", lambda: _install_software(window, "git")),
        make_button("installer.vscode", lambda: _install_software(window, "vscode")),
        make_button("installer.python313", lambda: _install_software(window, "python313")),
        make_button("installer.nodejs", lambda: _install_software(window, "nodejs")),
        make_button("installer.windowsTerminal", lambda: _install_software(window, "windowsTerminal")),
        make_button("installer.postman", lambda: _install_software(window, "postman")),
    ])

def _b_gaming(window, page):
    page.add_button_row_section(tr("installer.section.gaming"), [
        make_button("installer.steam", lambda: _install_software(window, "steam")),
        make_button("installer.epicGames", lambda: _install_software(window, "epicGames")),
        make_button("installer.gogGalaxy", lambda: _install_software(window, "gogGalaxy")),
        make_button("installer.discord", lambda: _install_software(window, "discord")),
        make_button("installer.msiAfterburner", lambda: _install_software(window, "msiAfterburner")),
    ])

def _b_security(window, page):
    page.add_button_row_section(tr("installer.section.security"), [
        make_button("installer.malwarebytes", lambda: _install_software(window, "malwarebytes")),
        make_button("installer.bitwarden", lambda: _install_software(window, "bitwarden")),
        make_button("installer.wireshark", lambda: _install_software(window, "wireshark")),
    ])

_BUILDERS = {
    "browsers": _b_browsers,
    "media": _b_media,
    "drivers": _b_drivers,
    "microsoft": _b_microsoft,
    "utilities": _b_utilities,
    "devtools": _b_devtools,
    "gaming": _b_gaming,
    "security": _b_security,
}


def _install_software(window, name):
    sw_list = _get_software_config()
    sw = sw_list.get(name)
    if not sw:
        window.log(f"Unknown software: {name}", "error")
        return

    sw_type = sw.get("type", "exe")

    if sw_type == "winget":
        _install_winget(window, name, sw)
        return

    url = sw.get("url")
    if not url:
        window.log(f"No URL for {name}", "error")
        return

    sw_args = sw.get("args", "")

    ext = ".msi" if sw_type == "msi" else ".exe"
    out_dir = os.path.join(get_env("TEMP", os.path.expanduser("~\\Temp")), "ghost_install")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{name}.install{ext}")

    dl_thread = DownloadThread(url, out_file)

    def on_finished(ok, msg):
        if not ok:
            winget_id = sw.get("winget_id")
            if winget_id:
                window.log(f"Download failed, trying winget: {winget_id}", "warn")
                _install_winget(window, name, sw)
                return
            window.log(f"Download failed: {name} - {msg}", "error")
            window.set_busy(False)
            window.set_status(tr("app.status.ready"))
            return

        def install_task(sig):
            sig.status.emit(f"Installing {name}...")
            sig.busy.emit(True, f"Installing {name}...")
            try:
                if sw_type == "msi":
                    args = ["msiexec.exe", "/i", out_file]
                    if sw_args:
                        args.extend(sw_args.split())
                    r = subprocess.run(args)
                elif name == "ytDlp":
                    local_app = os.environ.get("LOCALAPPDATA",
                                               os.path.join(os.environ["USERPROFILE"], "AppData", "Local"))
                    dest = os.path.join(local_app, "Microsoft", "WindowsApps", "yt-dlp.exe")
                    shutil.copy2(out_file, dest)
                    r = None
                else:
                    args = [out_file]
                    if sw_args:
                        args.extend(sw_args.split())
                    r = subprocess.run(args)
                if r is None or r.returncode == 0:
                    sig.log.emit(f"{name} installed successfully!", "success")
                    notify_done(window, name, "installed successfully")
                else:
                    sig.log.emit(f"Install exit code {r.returncode} for {name} (may be OK)", "warn")
                    notify_done(window, name, "installed (check result)")
            except Exception as e:
                sig.log.emit(f"Install failed: {e}", "error")
            finally:
                shutil.rmtree(out_dir, ignore_errors=True)
                sig.busy.emit(False, "")
                sig.status.emit(tr("app.status.ready"))

        run_in_thread(install_task, window=window)

    window.set_busy(True, f"Downloading {name}...")
    dl_thread.finished.connect(on_finished)
    window._active_downloads.add(dl_thread)
    dl_thread.finished.connect(lambda: window._active_downloads.discard(dl_thread))
    dl_thread.start()


def _install_winget(window, name, sw):
    def task(sig):
        sig.status.emit(f"Installing {name}...")
        sig.busy.emit(True, f"Installing {name}...")
        try:
            winget_id = sw.get("winget_id", name)
            args = ["winget", "install", "--exact", "--silent", winget_id]
            subprocess.run(args, check=True)
            sig.log.emit(f"{name} installed successfully!", "success")
            notify_done(window, name, "installed successfully")
        except Exception as e:
            url = sw.get("url", "")
            if url:
                sig.log.emit(f"winget failed, trying direct download: {url}", "warn")
                try:
                    out_file = _download_file(sig, name, url)
                    if out_file:
                        _run_installer(sig, name, out_file, sw.get("args", ""))
                        notify_done(window, name, "installed successfully")
                except Exception as e2:
                    sig.log.emit(f"Download+install failed: {e2}", "error")
                return
            sig.log.emit(f"Install failed: {e}", "error")
        finally:
            sig.busy.emit(False, "")
            sig.status.emit(tr("app.status.ready"))
    run_in_thread(task, window=window)


def _download_file(sig, name, url):
    sig.status.emit(f"Downloading {name}...")
    sig.busy.emit(True, f"Downloading {name}...")
    ext = ".msi" if url.lower().endswith(".msi") else ".exe"
    out_dir = os.path.join(get_env("TEMP", os.path.expanduser("~\\Temp")), "ghost_install")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{name}.install{ext}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        with open(out_file, "wb") as f:
            shutil.copyfileobj(resp, f)
    return out_file


def _run_installer(sig, name, out_file, sw_args):
    sig.status.emit(f"Installing {name}...")
    if out_file.endswith(".msi"):
        args = ["msiexec.exe", "/i", out_file]
        if sw_args:
            args.extend(sw_args.split())
        r = subprocess.run(args)
    elif name == "ytDlp":
        local_app = os.environ.get("LOCALAPPDATA", os.path.join(os.environ["USERPROFILE"], "AppData", "Local"))
        dest = os.path.join(local_app, "Microsoft", "WindowsApps", "yt-dlp.exe")
        shutil.copy2(out_file, dest)
        r = None
    else:
        args = [out_file]
        if sw_args:
            args.extend(sw_args.split())
        r = subprocess.run(args)
    if r is None or r.returncode == 0:
        sig.log.emit(f"{name} installed successfully!", "success")
    else:
        sig.log.emit(f"Install exit code {r.returncode} for {name} (may be OK)", "warn")


def verify_all_urls(window):
    from modules.utils import run_in_thread

    def task(sig):
        sig.status.emit("Checking download URLs...")
        sw_list = _get_software_config()
        ok = 0
        fail = 0
        for name, sw in sw_list.items():
            url = sw.get("url", "")
            if not url or sw.get("type") == "winget":
                continue
            try:
                req = urllib.request.Request(url, method="HEAD")
                req.add_header("User-Agent", "Mozilla/5.0")
                resp = urllib.request.urlopen(req, timeout=10)
                if resp.status >= 400:
                    sig.log.emit(f"URL {name}: HTTP {resp.status} {resp.reason}", "warn")
                    fail += 1
                else:
                    sig.log.emit(f"URL {name}: OK", "info")
                    ok += 1
            except Exception as e:
                sig.log.emit(f"URL {name}: FAIL - {e}", "warn")
                fail += 1
        sig.log.emit(f"URL check done: {ok} OK, {fail} FAIL", "info")
    run_in_thread(task, window=window)
