from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool
from i18n import tr


class LogSignals(QObject):
    log = pyqtSignal(str, str)
    status = pyqtSignal(str)
    busy = pyqtSignal(bool, str)
    done = pyqtSignal()


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = LogSignals()

    def run(self):
        try:
            self.fn(self.signals, *self.args, **self.kwargs)
        except Exception as e:
            self.signals.log.emit(str(e), "error")
        finally:
            self.signals.done.emit()


def run_in_thread(fn, *args, **kwargs):
    window = kwargs.pop('window', None)
    worker = Worker(fn, *args, **kwargs)
    if window:
        worker.signals.log.connect(lambda msg, lvl: window.log(msg, lvl))
        worker.signals.status.connect(lambda msg, color="#22c55e": window.set_status(msg, color))
        worker.signals.busy.connect(lambda b, lbl: window.set_busy(b, lbl))
        worker.signals.done.connect(lambda: window.set_status(tr("app.status.ready")))
    QThreadPool.globalInstance().start(worker)
    return worker


def make_button(text_key, callback, danger=False):
    from PyQt6.QtWidgets import QPushButton
    from PyQt6.QtCore import Qt
    btn = QPushButton(tr(text_key))
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setMinimumHeight(36)
    btn.clicked.connect(callback)
    return btn


def log_window(window, message, level="info"):
    window.log(message, level)


def set_busy(window, busy, label=""):
    window.set_busy(busy, label)


def confirm(window, message):
    from PyQt6.QtWidgets import QMessageBox
    result = QMessageBox.question(
        window, "Confirm", message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    return result == QMessageBox.StandardButton.Yes


def notify_done(window, title, message):
    from core.system import notify
    try:
        notify(title, message)
    except Exception:
        pass


def restart_explorer(window):
    import subprocess
    import time
    from core.system import run_cmd
    run_cmd(["taskkill", "/f", "/im", "explorer.exe"])
    time.sleep(0.5)
    try:
        subprocess.Popen("explorer.exe")
        window.log("Explorer restarted", "success")
    except Exception as e:
        window.log(f"Failed to restart Explorer: {e}. Restart manually or run 'start explorer.exe' in CMD.", "error")
