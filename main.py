import sys
import os
import ctypes
from core.system import is_admin


def main():
    if not is_admin():
        result = ctypes.windll.user32.MessageBoxW(
            0,
            "AnonBOT Toolbox requires administrator privileges.\nRestart as Admin?",
            "Elevation Required",
            4 | 48
        )
        if result == 6:
            script = os.path.abspath(__file__)
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script}"', None, 1
            )
        sys.exit(0)

    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt, QTimer
    from ui.main_window import MainWindow
    from modules.dashboard import show_dashboard
    from modules.installers import verify_all_urls
    from modules.profiles import validate_profiles
    from core import system

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()

    os_info = system.get_os_info()
    sys_text = f"{os_info['os']} {os_info['display_version']} (Build {os_info['build']}) | {os_info['arch']}"
    window.set_sys_info(sys_text)

    page = window._pages.get("dashboard")
    if page:
        page.clear()
        show_dashboard(window)

    window.show()

    try:
        with open(os.path.join(os.path.dirname(__file__), "config.json"), encoding="utf-8") as f:
            import json
            cfg = json.load(f)
        do_checks = cfg.get("startup_checks", True)
    except Exception:
        do_checks = True
    if do_checks:
        QTimer.singleShot(1000, lambda: verify_all_urls(window))
        QTimer.singleShot(2000, lambda: validate_profiles(window))

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
