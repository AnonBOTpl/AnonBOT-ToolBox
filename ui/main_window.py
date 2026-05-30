import json
import os
import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QLabel, QPushButton, QCheckBox,
    QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt
from i18n import tr, get_i18n
from ui.themes import get_qss, get_colors
from ui.widgets import ContentPage, Sidebar

import modules.dashboard as mod_dashboard
import modules.tweaks as mod_tweaks
import modules.cleaner as mod_cleaner
import modules.context_menu as mod_context_menu
import modules.installers as mod_installers
import modules.uwp as mod_uwp
import modules.personalize as mod_personalize
import modules.system_tools as mod_system_tools
import modules.network_dns as mod_network_dns
import modules.privacy as mod_privacy
import modules.performance as mod_performance
import modules.file_explorer as mod_file_explorer
import modules.backup_restore as mod_backup_restore
import modules.profiles as mod_profiles
import modules.wsl as mod_wsl
import modules.scheduled_tasks as mod_scheduled_tasks
import modules.windows_update as mod_windows_update
import modules.env_vars as mod_env_vars

MODULE_DISPATCH = {
    "dashboard":           mod_dashboard,
    "tweaks":              mod_tweaks,
    "cleaner":             mod_cleaner,
    "context_menu":        mod_context_menu,
    "installers":          mod_installers,
    "uwp":                 mod_uwp,
    "personalize":         mod_personalize,
    "system_tools":        mod_system_tools,
    "network_dns":         mod_network_dns,
    "privacy":             mod_privacy,
    "performance":         mod_performance,
    "file_explorer":       mod_file_explorer,
    "backup":              mod_backup_restore,
    "profiles":            mod_profiles,
    "wsl":                 mod_wsl,
    "scheduled_tasks":     mod_scheduled_tasks,
    "windows_update":      mod_windows_update,
    "env_vars":            mod_env_vars,
}

ALL_PAGE_IDS = [
    "dashboard",
    "backup",
    "profiles",
    "wsl.manager",
    "tweaks.action_center", "tweaks.hibernation", "tweaks.pagefile",
    "tweaks.taskbar", "tweaks.w11", "tweaks.windows_update",
    "tweaks.winre", "tweaks.dotnet",
    "cleaner.event_logs", "cleaner.update", "cleaner.store", "cleaner.compact",
    "performance.visual", "performance.cpu", "performance.power",
    "performance.startup", "performance.disk",
    "system_tools.benchmark", "system_tools.users", "system_tools.gaming",
    "system_tools.audio", "system_tools.cmd_schemes", "system_tools.explorer",
    "network_dns.dns", "network_dns.utilities", "network_dns.hosts", "network_dns.ipv6",
    "privacy.telemetry", "privacy.cortana", "privacy.ads", "privacy.location",
    "privacy.camera", "privacy.mic", "privacy.diagnostic",
    "context_menu.ownership", "context_menu.shortcuts", "context_menu.w11_menu",
    "uwp.xbox", "uwp.microsoft", "uwp.clipboard", "uwp.miracast",
    "personalize.dwm", "personalize.themes", "personalize.wallpapers",
    "file_explorer.general", "file_explorer.launch", "file_explorer.path", "file_explorer.view",
    "scheduled_tasks", "windows_update", "env_vars",
    "installers.browsers", "installers.media", "installers.drivers", "installers.microsoft",
    "installers.utilities", "installers.devtools", "installers.gaming", "installers.security",
]


class MainWindow(QMainWindow):
    SECTION_MAP = {
        "tweaks": "SYSTEM", "cleaner": "SYSTEM", "performance": "SYSTEM",
        "system_tools": "SYSTEM",
        "backup": "SYSTEM", "profiles": "SYSTEM", "wsl": "SYSTEM",
        "scheduled_tasks": "SYSTEM", "windows_update": "SYSTEM", "env_vars": "SYSTEM",
        "network_dns": "NETWORK",
        "privacy": "PRIVACY",
        "context_menu": "CUSTOMIZE", "uwp": "CUSTOMIZE", "personalize": "CUSTOMIZE",
        "file_explorer": "CUSTOMIZE",
        "installers": "CUSTOMIZE",
        "installers.utilities": "CUSTOMIZE",
    }

    def __init__(self):
        super().__init__()
        self._accent_color = "#7c3aed"
        self._theme_mode = "auto"
        self._pages = {}
        self._log_history = []
        self._active_downloads = set()
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        self._log_file = os.path.join(log_dir, "session.log")
        self._setup_ui()
        self._load_config()
        self._apply_theme(self._accent_color)

    def _setup_ui(self):
        self.setWindowTitle(tr("app.title"))
        self.setMinimumSize(1200, 800)
        self.resize(1200, 800)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar_col = QVBoxLayout()
        sidebar_col.setContentsMargins(0, 0, 0, 0)
        sidebar_col.setSpacing(0)

        self._sidebar = Sidebar()
        self._sidebar.page_selected.connect(self.show_page)

        sidebar_bottom = QWidget()
        sidebar_bottom.setFixedHeight(48)
        sbl = QVBoxLayout(sidebar_bottom)
        sbl.setContentsMargins(12, 4, 12, 8)
        sbl.setSpacing(4)
        settings_btn = QPushButton(tr("btn.settings"))
        settings_btn.setObjectName("settingsBtn")
        settings_btn.setFlat(True)
        settings_btn.clicked.connect(self._open_settings)
        sbl.addWidget(settings_btn)

        sidebar_col.addWidget(self._sidebar, stretch=1)
        sidebar_col.addWidget(sidebar_bottom)

        right_panel = QWidget()
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        header = QWidget()
        header.setObjectName("headerWidget")
        header.setFixedHeight(50)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 0, 16, 0)
        self._breadcrumb = QLabel()
        self._breadcrumb.setObjectName("breadcrumb")
        header_layout.addWidget(self._breadcrumb)
        self._page_title = QLabel(tr("app.title"))
        self._page_title.setObjectName("pageTitle")
        header_layout.addWidget(self._page_title)
        header_layout.addStretch()
        self._sys_info = QLabel(tr("app.status.ready"))
        self._sys_info.setObjectName("sysInfo")
        header_layout.addWidget(self._sys_info)

        self._content_stack = QStackedWidget()
        for page_id in ALL_PAGE_IDS:
            page = ContentPage()
            self._content_stack.addWidget(page)
            self._pages[page_id] = page

        bottom_bar = QWidget()
        bottom_bar.setObjectName("bottomBar")
        bottom_bar.setFixedHeight(48)
        bottom_layout = QVBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(8, 4, 8, 8)

        status_row = QHBoxLayout()
        self._status_label = QLabel(tr("app.status.ready"))
        self._status_label.setObjectName("statusLabel")
        status_row.addWidget(self._status_label)
        status_row.addStretch()

        export_btn = QPushButton("Export Log")
        export_btn.setObjectName("exportLogBtn")
        export_btn.setFlat(True)
        export_btn.clicked.connect(self._export_log)
        status_row.addWidget(export_btn)

        self._progress = QProgressBar()
        self._progress.setFixedHeight(4)
        self._progress.setVisible(False)
        self._progress.setTextVisible(False)

        bottom_layout.addLayout(status_row)
        bottom_layout.addWidget(self._progress)

        right_layout.addWidget(header)
        right_layout.addWidget(self._content_stack, stretch=1)
        right_layout.addWidget(bottom_bar)

        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar_col)
        sidebar_widget.setFixedWidth(250)

        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(right_panel, stretch=1)

    def show_page(self, page_id):
        module = page_id.split(".")[0]
        mod = MODULE_DISPATCH.get(module)
        if mod:
            if hasattr(mod, "show_page"):
                mod.show_page(self, page_id)
            else:
                self.log(f"Module '{module}' has no show_page function", "warn")
        page = self._pages.get(page_id)
        if page:
            self._content_stack.setCurrentWidget(page)
        self._sidebar.set_active(page_id)
        self._update_breadcrumb(page_id)

    def _update_breadcrumb(self, page_id):
        parts = page_id.split(".")
        if len(parts) == 1:
            self._breadcrumb.setText("")
            return
        module = parts[0]
        section = self.SECTION_MAP.get(module, "")
        module_name = tr(f"sidebar.{module}")
        if section:
            self._breadcrumb.setText(f"{section} › {module_name}")
        else:
            self._breadcrumb.setText(module_name)

    def set_page_title(self, title):
        self._page_title.setText(title)

    def set_sys_info(self, text):
        self._sys_info.setText(text)

    def log(self, message, level="info"):
        ansi = {
            "info": "\033[94m",
            "success": "\033[92m",
            "warn": "\033[93m",
            "error": "\033[91m",
        }
        color = ansi.get(level, "")
        reset = "\033[0m"
        print(f"{color}[{level.upper()}] {message}{reset}")
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._log_history.append((now, level.upper(), message))
        if len(self._log_history) > 1000:
            self._log_history = self._log_history[-500:]
        try:
            with open(self._log_file, "a", encoding="utf-8") as f:
                f.write(f"[{now}] [{level.upper()}] {message}\n")
        except Exception:
            pass

    def set_status(self, text, color="#22c55e"):
        self._status_label.setText(text)
        self._status_label.setStyleSheet(f"font-size: 11px; color: {color};")

    def set_busy(self, busy, label=""):
        self._progress.setVisible(busy)
        if label:
            self._status_label.setText(label)

    def _export_log(self):
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = os.path.join(log_dir, f"anonbot_{ts}.txt")
        try:
            with open(path, "w", encoding="utf-8") as f:
                for log_ts, level, msg in self._log_history:
                    f.write(f"[{log_ts}] [{level}] {msg}\n")
            QMessageBox.information(self, "Log Exported", f"Log saved to:\n{path}")
        except Exception as e:
            self.log(f"Export failed: {e}", "error")

    def _open_settings(self):
        from ui.settings_dialog import SettingsDialog
        d = SettingsDialog(self)
        d.finished.connect(lambda: self._reload_config())
        d.finished.connect(lambda: self._refresh_language())
        d.exec()

    def _refresh_language(self):
        self._sidebar.rebuild()
        curr = self._content_stack.currentWidget()
        for pid, page in self._pages.items():
            if page == curr:
                self.show_page(pid)
                break

    def _reload_config(self):
        self._load_config()
        self._apply_theme(self._accent_color)

    def _load_config(self):
        cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        try:
            with open(cfg_path, encoding="utf-8") as f:
                cfg = json.load(f)
            self._accent_color = cfg.get("accent_color", "#7c3aed")
            self._theme_mode = cfg.get("theme_mode", "auto")
            lang = cfg.get("language", "auto")
            if lang and lang != "auto":
                get_i18n().set_language(lang)
        except Exception:
            pass

    def _apply_theme(self, accent_color):
        self.setStyleSheet(get_qss(accent_color, self._theme_mode))
        self._accent_color = accent_color
