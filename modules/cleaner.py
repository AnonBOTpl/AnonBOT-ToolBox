import os
import shutil
from i18n import tr
from core.system import run_cmd, get_env
from modules.utils import run_in_thread, make_button, confirm, notify_done


def show_page(window, page_id):
    if "." not in page_id:
        return
    sub = page_id.split(".", 1)[1]
    window.set_page_title("🧹 " + tr("cleaner.title") + " > " + tr(f"cleaner.{sub}"))
    page = window._pages.get(page_id)
    if not page:
        return
    page.clear()
    page.add_section(tr(f"cleaner.{sub}"))
    builder = _BUILDERS.get(sub)
    if builder:
        builder(window, page)
    else:
        window.log(f"Unknown page: {page_id}", "error")


def _b_event_logs(window, page):
    page.add_button_row_section(tr("cleaner.event_logs"), [
        make_button("cleaner.event_clear", lambda: _clean_event_logs(window)),
        make_button("cleaner.event_disable", lambda: _disable_logging(window)),
    ])


def _b_update(window, page):
    page.add_button_row_section(tr("cleaner.update"), [
        make_button("cleaner.update_cache", lambda: _clean_update_cache(window)),
        make_button("cleaner.deliveryopt", lambda: _clean_delivery_opt(window)),
        make_button("cleaner.temp", lambda: _clean_temp(window)),
        make_button("cleaner.all", lambda: _clean_all(window)),
        make_button("cleaner.prefetch", lambda: _clean_prefetch(window)),
        make_button("cleaner.dns_cache", lambda: _flush_dns(window)),
        make_button("cleaner.thumbnail", lambda: _clean_thumbnails(window)),
        make_button("cleaner.font_cache", lambda: _clean_font_cache(window)),
    ])


def _b_store(window, page):
    page.add_button_row_section(tr("cleaner.store"), [
        make_button("cleaner.store_cache", lambda: _clean_store(window)),
    ])


def _b_compact(window, page):
    page.add_button_row_section(tr("cleaner.compact"), [
        make_button("cleaner.compact_os", lambda: _compact_os(window)),
    ])


_BUILDERS = {
    "event_logs": _b_event_logs,
    "update": _b_update,
    "store": _b_store,
    "compact": _b_compact,
}


def _clean_event_logs(window):
    def task(sig):
        sig.status.emit("Clearing event logs...")
        sig.log.emit("Clearing all event logs...", "info")
        code, out, err = run_cmd(["wevtutil", "el"])
        logs = [l for l in out.strip().split("\n") if l.strip()]
        for log in logs:
            run_cmd(["wevtutil", "cl", log.strip()])
        sig.log.emit(f"All {len(logs)} event logs cleared", "success")
        notify_done(window, "Cleanup", f"{len(logs)} event logs cleared")
    run_in_thread(task, window=window)


def _disable_logging(window):
    run_cmd(["auditpol", "/set", "/subcategory:Filtering Platform Connection",
             "/success:disable", "/failure:enable"])
    window.log("Filtering logging disabled", "success")


def _clean_update_cache(window):
    def task(sig):
        sig.status.emit("Cleaning update cache...")
        run_cmd(["net", "stop", "wuauserv"])
        run_cmd(["net", "stop", "DoSvc"])
        sd_path = os.path.join(get_env("SystemRoot", "C:\\Windows"), "SoftwareDistribution", "Download")
        if os.path.exists(sd_path):
            for item in os.listdir(sd_path):
                p = os.path.join(sd_path, item)
                try:
                    shutil.rmtree(p, ignore_errors=True) if os.path.isdir(p) else os.remove(p)
                except Exception:
                    pass
        sig.log.emit("Update cache cleared", "success")
        run_cmd(["net", "start", "wuauserv"])
        run_cmd(["net", "start", "DoSvc"])
        notify_done(window, "Cleanup", "Update cache cleared")
    run_in_thread(task, window=window)


def _clean_delivery_opt(window):
    def task(sig):
        run_cmd(["net", "stop", "DoSvc"])
        do_path = os.path.join(get_env("SystemRoot", "C:\\Windows"),
                               "ServiceProfiles", "NetworkService", "AppData", "Local",
                               "Microsoft", "Windows", "DeliveryOptimization")
        for sub in ["Cache", "Logs", "State"]:
            p = os.path.join(do_path, sub)
            if os.path.exists(p):
                shutil.rmtree(p, ignore_errors=True)
        sig.log.emit("Delivery Optimization cleaned", "success")
        run_cmd(["sc.exe", "config", "DoSvc", "start=delayed-auto"])
    run_in_thread(task, window=window)


def _clean_temp(window):
    for d in [get_env("TEMP", os.path.expanduser("~\\AppData\\Local\\Temp")),
              os.path.join(get_env("SystemRoot", "C:\\Windows"), "Temp")]:
        if os.path.exists(d):
            for item in os.listdir(d):
                try:
                    p = os.path.join(d, item)
                    shutil.rmtree(p, ignore_errors=True) if os.path.isdir(p) else os.remove(p)
                except Exception:
                    pass
    window.log("Temp files cleaned", "success")


def _clean_store(window):
    run_cmd(["taskkill", "/f", "/im", "WinStore.App"])
    run_cmd(["wsreset.exe"])
    window.log("Store cache cleared", "success")


def _clean_prefetch(window):
    pf_path = os.path.join(get_env("SystemRoot", "C:\\Windows"), "Prefetch")
    if os.path.exists(pf_path):
        for item in os.listdir(pf_path):
            try:
                p = os.path.join(pf_path, item)
                shutil.rmtree(p, ignore_errors=True) if os.path.isdir(p) else os.remove(p)
            except Exception:
                pass
    window.log("Prefetch cleaned", "success")


def _flush_dns(window):
    code, out, err = run_cmd(["ipconfig", "/flushdns"])
    window.log("DNS cache flushed" if code == 0 else f"DNS flush failed: {err}", "success" if code == 0 else "error")


def _clean_thumbnails(window):
    def task(sig):
        base = os.path.join(get_env("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local")),
                            "Microsoft", "Windows", "Explorer")
        if os.path.exists(base):
            for f in os.listdir(base):
                if f.endswith(".db") or "thumbcache" in f.lower():
                    try:
                        os.remove(os.path.join(base, f))
                    except Exception:
                        pass
        sig.log.emit("Thumbnail cache cleaned", "success")
    run_in_thread(task, window=window)


def _clean_font_cache(window):
    def task(sig):
        run_cmd(["net", "stop", "FontCache"])
        fc_path = os.path.join(get_env("SystemRoot", "C:\\Windows"), "ServiceProfiles",
                               "LocalService", "AppData", "Local", "FontCache")
        if os.path.exists(fc_path):
            shutil.rmtree(fc_path, ignore_errors=True)
        run_cmd(["net", "start", "FontCache"])
        sig.log.emit("Font cache cleaned. Restart recommended.", "success")
    run_in_thread(task, window=window)


def _clean_all(window):
    if not confirm(window, "Run FULL system cleanup? This clears logs, caches, temp files, and prefetch."):
        return
    _clean_event_logs(window)
    _clean_update_cache(window)
    _clean_delivery_opt(window)
    _clean_temp(window)
    _clean_prefetch(window)
    _flush_dns(window)
    window.log("Full cleanup completed", "success")


def _compact_os(window):
    if not confirm(window, "Compact the OS? This compresses system files and cannot be easily reverted."):
        return
    def task(sig):
        code, out, err = run_cmd(["compact.exe", "/CompactOS:always"], timeout=600)
        sig.log.emit("Compaction complete. Restart required." if code == 0 else f"Compaction failed: {err}",
                     "success" if code == 0 else "error")
        notify_done(window, "Compact OS", "OS compaction completed!")
    run_in_thread(task, window=window)
