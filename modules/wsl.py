import os
import subprocess
from PyQt6.QtWidgets import QLabel, QPushButton, QMessageBox, QInputDialog, QLineEdit, QDialog, QTextEdit, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from i18n import tr
from modules.utils import make_button, confirm, run_in_thread

_WSL_ENV = {**os.environ, "WSL_UTF8": "1"}


def _run_wsl(args, timeout=120):
    try:
        proc = subprocess.run(
            ["wsl"] + list(args),
            capture_output=True,
            timeout=timeout,
            env=_WSL_ENV,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        out = proc.stdout.decode("utf-8", errors="replace") if proc.stdout else ""
        err = proc.stderr.decode("utf-8", errors="replace") if proc.stderr else ""
        return proc.returncode, out, err
    except Exception:
        return -1, "", ""


def _get_distro_list():
    code, out, _ = _run_wsl(["--list", "--quiet"])
    if code != 0 or not out.strip():
        return []
    lines = out.strip().splitlines()
    clean = []
    for line in lines:
        line = line.strip().replace("\ufeff", "")
        for suffix in [" (Default)", " (default)", " (domyślna)"]:
            line = line.replace(suffix, "")
        if line:
            clean.append(line)
    return clean


def show_page(window, page_id):
    if "." not in page_id:
        return
    sub = page_id.split(".", 1)[1]
    window.set_page_title("🐧 " + tr("wsl.title") + " > " + tr(f"wsl.{sub}"))
    page = window._pages.get(page_id)
    if not page:
        return
    page.clear()
    page.add_section(tr("wsl.manager"))

    code, out, err = _run_wsl(["--status"])

    if code != 0:
        list_code, list_out, _ = _run_wsl(["--list"])
        if list_code == 0:
            code, out = 0, list_out
            window.log("WSL status check returned error — using fallback", "warn")
        else:
            info = QLabel(tr("wsl.not_installed"))
            info.setWordWrap(True)
            info.setStyleSheet("font-size: 13px; padding: 16px;")
            page.add_widget(info)
            page.add_widget(make_button("wsl.install", lambda: _install_wsl(window)))
            return

    out_lower = out.lower()
    virt_off = any(kw in out_lower for kw in [
        "virtualization is not enabled",
        "wirtualizacja nie jest",
        "virtualization is not supported",
        "please enable the virtual machine platform",
        "virtual machine platform is not installed",
    ])
    if virt_off:
        warn = QLabel(tr("wsl.no_virt"))
        warn.setWordWrap(True)
        warn.setStyleSheet("font-size: 13px; padding: 12px; color: #eab308; border: 1px solid #eab308; border-radius: 6px; margin: 4px 0;")
        page.add_widget(warn)

    lines = out.strip().splitlines()[:20] if out else []
    status = QLabel("\n".join(lines) if lines else tr("wsl.status_ok"))
    status.setWordWrap(True)
    status.setStyleSheet("font-size: 12px; padding: 8px; font-family: 'Consolas', 'Courier New';")
    page.add_widget(status)

    page.add_button_row_section(tr("wsl.actions"), [
        make_button("wsl.list", lambda: _show_distro_dialog(window)),
        make_button("wsl.shutdown", lambda: _shutdown_wsl(window)),
        make_button("wsl.open", lambda: _open_wsl()),
    ])

    if not virt_off:
        page.add_button_row_section(tr("wsl.config"), [
            make_button("wsl.set_default", lambda: _set_default_distro(window)),
            make_button("wsl.set_version", lambda: _set_version(window)),
            make_button("wsl.unregister", lambda: _unregister_distro(window)),
        ])


def _install_wsl(window):
    if not confirm(window, tr("wsl.install_confirm")):
        return
    def task(sig):
        sig.log.emit("Installing WSL... (this may take a while)", "info")
        code, out, err = _run_wsl(["--install"], timeout=600)
        if code == 0:
            sig.log.emit("WSL installed. Restart required.", "success")
        else:
            sig.log.emit(f"WSL install failed: {err}", "error")
    run_in_thread(task, window=window)


def _show_distro_dialog(window):
    code, out, err = _run_wsl(["--list", "--verbose"])
    dlg = QDialog(window)
    dlg.setWindowTitle(tr("wsl.list"))
    dlg.resize(600, 400)
    layout = QVBoxLayout(dlg)
    text = QTextEdit()
    text.setReadOnly(True)
    if code == 0 and out.strip():
        text.setPlainText(out.strip())
    else:
        text.setPlainText(tr("wsl.no_distros"))
    text.setStyleSheet("font-family: 'Consolas', 'Courier New'; font-size: 12px;")
    layout.addWidget(text)
    btn_row = QHBoxLayout()
    btn_row.addStretch()
    close_btn = QPushButton(tr("wsl.close"))
    close_btn.setMinimumHeight(32)
    close_btn.clicked.connect(dlg.accept)
    btn_row.addWidget(close_btn)
    layout.addLayout(btn_row)
    dlg.exec()


def _open_wsl():
    try:
        subprocess.Popen(["wt.exe", "wsl.exe"],
                         creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)
    except FileNotFoundError:
        subprocess.Popen(["wsl.exe"],
                         creationflags=subprocess.CREATE_NEW_CONSOLE)


def _shutdown_wsl(window):
    if not confirm(window, tr("wsl.shutdown_confirm")):
        return
    code, out, err = _run_wsl(["--shutdown"])
    window.log("WSL shut down" if code == 0 else f"WSL shutdown failed: {err}",
               "success" if code == 0 else "error")


def _pick_distro(window, title_key, prompt_key):
    distros = _get_distro_list()
    if not distros:
        QMessageBox.information(window, tr("wsl.list"), tr("wsl.no_distros"))
        return None
    name, ok = QInputDialog.getItem(window, tr(title_key), tr(prompt_key),
                                     distros, 0, False)
    return name.strip() if ok and name.strip() else None


def _set_default_distro(window):
    name = _pick_distro(window, "wsl.set_default", "wsl.distro_choose")
    if not name:
        return
    code, out, err = _run_wsl(["--set-default", name])
    if code == 0:
        window.log(tr("wsl.default_set").format(name), "success")
    else:
        window.log(tr("wsl.default_fail").format(name, err), "error")


def _set_version(window):
    name = _pick_distro(window, "wsl.set_version", "wsl.distro_choose")
    if not name:
        return
    ver, ok2 = QInputDialog.getInt(window, tr("wsl.set_version"),
                                    tr("wsl.version_prompt"), 2, 1, 2)
    if not ok2:
        return
    code, out, err = _run_wsl(["--set-version", name, str(ver)])
    if code == 0:
        window.log(tr("wsl.version_set").format(name, ver), "success")
    else:
        window.log(tr("wsl.version_fail").format(name, err), "error")


def _unregister_distro(window):
    name = _pick_distro(window, "wsl.unregister", "wsl.distro_choose")
    if not name:
        return
    if not confirm(window, tr("wsl.unregister_confirm")):
        return
    code, out, err = _run_wsl(["--unregister", name])
    if code == 0:
        window.log(tr("wsl.unregister_done").format(name), "success")
    else:
        window.log(tr("wsl.unregister_fail").format(name, err), "error")
