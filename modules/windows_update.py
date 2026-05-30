import subprocess
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import QMetaObject, Qt, Q_ARG
from i18n import tr
from modules.utils import run_in_thread, make_button


def _set_text_threadsafe(text_widget, content):
    QMetaObject.invokeMethod(text_widget, "setPlainText",
                             Qt.ConnectionType.QueuedConnection,
                             Q_ARG(str, content))


def show_page(window, page_id):
    window.set_page_title(tr("windows_update.title"))
    page = window._pages.get(page_id)
    if not page:
        return
    page.clear()
    page.add_section(tr("windows_update.title"))
    page.add_button_row_section(tr("windows_update.actions"), [
        make_button("windows_update.check", lambda: _check_updates(window, page)),
        make_button("windows_update.list", lambda: _list_updates(window, page)),
    ])


def _check_updates(window, page):
    window.log("Checking for Windows updates...", "info")
    text = QTextEdit()
    text.setReadOnly(True)
    text.setMinimumHeight(300)
    page.add_widget(text)
    _set_text_threadsafe(text, "Checking for updates...")

    def task(sig):
        sig.status.emit("Checking for updates...")
        try:
            r = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "Install-Module PSWindowsUpdate -Force -Scope CurrentUser -ErrorAction SilentlyContinue; "
                 "Get-WindowsUpdate | Select-Object Size, Title"],
                capture_output=True, text=True, timeout=120
            )
            content = r.stdout.strip()
            if not content:
                content = "No updates found or PSWindowsUpdate not available"
            _set_text_threadsafe(text, content[:10000])
            sig.log.emit("Update check complete", "info")
        except Exception as e:
            _set_text_threadsafe(text, f"Update check failed: {e}")
            sig.log.emit(f"Update check failed: {e}", "warn")
    run_in_thread(task, window=window)


def _list_updates(window, page):
    text = QTextEdit()
    text.setReadOnly(True)
    text.setMinimumHeight(300)
    page.add_widget(text)
    _set_text_threadsafe(text, "Fetching installed updates...")

    def task(sig):
        sig.status.emit("Fetching installed updates...")
        try:
            r = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "Get-HotFix | Select-Object HotFixID, InstalledOn, Description | Sort-Object InstalledOn -Descending | Format-Table -AutoSize | Out-String -Width 4096"],
                capture_output=True, text=True, timeout=30
            )
            content = r.stdout.strip()
            if not content:
                content = "No updates found"
            _set_text_threadsafe(text, content[:10000])
            sig.log.emit("Installed updates displayed", "info")
        except Exception as e:
            _set_text_threadsafe(text, f"Failed: {e}")
            sig.log.emit(f"Failed to list updates: {e}", "error")
    run_in_thread(task, window=window)
