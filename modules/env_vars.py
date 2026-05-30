import subprocess
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import QMetaObject, Qt, Q_ARG
from i18n import tr
from modules.utils import run_in_thread, make_button

_page_text = {}


def _set_text_threadsafe(text_widget, content):
    QMetaObject.invokeMethod(text_widget, "setPlainText",
                             Qt.ConnectionType.QueuedConnection,
                             Q_ARG(str, content))


def _ensure_text_widget(page):
    pid = id(page)
    old = _page_text.get(pid)
    if old:
        old.setParent(None)
        old.deleteLater()
    text = QTextEdit()
    text.setReadOnly(True)
    text.setMinimumHeight(300)
    page.add_widget(text)
    _page_text[pid] = text
    return text


def show_page(window, page_id):
    window.set_page_title(tr("env_vars.title"))
    page = window._pages.get(page_id)
    if not page:
        return
    page.clear()
    if id(page) in _page_text:
        del _page_text[id(page)]
    page.add_section(tr("env_vars.title"))
    page.add_button_row_section(tr("env_vars.scope"), [
        make_button("env_vars.system", lambda: _show_vars(window, page, "Machine")),
        make_button("env_vars.user", lambda: _show_vars(window, page, "User")),
    ])
    page.add_button_row_section(tr("env_vars.path"), [
        make_button("env_vars.path_user", lambda: _show_path(window, page, "User")),
        make_button("env_vars.path_system", lambda: _show_path(window, page, "Machine")),
    ])


def _show_vars(window, page, scope):
    text = _ensure_text_widget(page)
    _set_text_threadsafe(text, f"Loading {scope} variables...")

    def task(sig):
        sig.status.emit(f"Reading {scope} environment variables...")
        try:
            r = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 f"[System.Environment]::GetEnvironmentVariables('{scope}') | Format-Table -AutoSize | Out-String -Width 4096"],
                capture_output=True, text=True, timeout=15
            )
            content = r.stdout.strip() or "No variables found"
            _set_text_threadsafe(text, content[:10000])
            sig.log.emit(f"{scope} variables displayed", "info")
        except Exception as e:
            _set_text_threadsafe(text, f"Error: {e}")
            sig.log.emit(f"Failed: {e}", "error")
    run_in_thread(task, window=window)


def _show_path(window, page, scope):
    text = _ensure_text_widget(page)
    _set_text_threadsafe(text, f"Loading PATH ({scope})...")

    def task(sig):
        sig.status.emit(f"Reading PATH ({scope})...")
        try:
            r = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 f"([Environment]::GetEnvironmentVariable('Path','{scope}') -split ';') | Select-String ."],
                capture_output=True, text=True, timeout=15
            )
            paths = [p.strip() for p in r.stdout.strip().split("\n") if p.strip()]
            lines = [f"PATH entries ({scope}, {len(paths)}):"]
            for i, p in enumerate(paths, 1):
                lines.append(f"  {i}. {p}")
            _set_text_threadsafe(text, "\n".join(lines))
            sig.log.emit(f"PATH ({scope}, {len(paths)} entries)", "info")
        except Exception as e:
            _set_text_threadsafe(text, f"Error: {e}")
            sig.log.emit(f"Failed: {e}", "error")
    run_in_thread(task, window=window)
