from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from i18n import tr


class Separator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setStyleSheet("background: #3f3f46; max-height: 1px; margin: 4px 0;")


class Section(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("font-size: 20px; font-weight: 600; padding: 0 0 16px 0;")


class ActionButton(QPushButton):
    def __init__(self, text, hint="", danger=False, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)
        if hint:
            self.setToolTip(hint)


class ButtonRow(QWidget):
    def __init__(self, buttons, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(6)
        for btn_def in buttons:
            if isinstance(btn_def, QPushButton):
                layout.addWidget(btn_def)
            else:
                btn = ActionButton(btn_def["text"], hint=btn_def.get("hint", ""))
                if "click" in btn_def:
                    btn.clicked.connect(btn_def["click"])
                layout.addWidget(btn)


class ButtonRowSection(QWidget):
    def __init__(self, title, buttons, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(8)
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: 600;")
        layout.addWidget(title_label)
        layout.addWidget(ButtonRow(buttons))
        layout.addWidget(Separator())


class ContentPage(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setWidget(self._container)

    def clear(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def add_widget(self, widget):
        self._layout.addWidget(widget)

    def add_section(self, title):
        self.add_widget(Section(title))

    def add_button_row_section(self, title, buttons):
        self.add_widget(ButtonRowSection(title, buttons))


class _CollapsibleGroup(QWidget):
    toggled = pyqtSignal(str)

    def __init__(self, page_id, label, children_data, parent=None):
        super().__init__(parent)
        self._page_id = page_id
        self._expanded = False
        self._child_buttons = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._header = QPushButton(f"▶  {label}")
        self._header.setObjectName("sidebarBtn")
        self._header.setFlat(True)
        self._header.setCursor(Qt.CursorShape.PointingHandCursor)
        self._header.setFixedHeight(36)
        self._header.clicked.connect(self._toggle)
        layout.addWidget(self._header)

        self._child_container = QWidget()
        self._child_container.setVisible(False)
        cl = QVBoxLayout(self._child_container)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        for child_id, child_key in children_data:
            btn = QPushButton(tr(child_key))
            btn.setObjectName("sidebarSubBtn")
            btn.setFlat(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(32)
            btn.clicked.connect(lambda checked=False, pid=child_id: self._emit_page(pid))
            cl.addWidget(btn)
            self._child_buttons[child_id] = btn

        layout.addWidget(self._child_container)

    def _toggle(self):
        self._expanded = not self._expanded
        text = self._header.text()
        prefix = "▼ " if self._expanded else "▶ "
        self._header.setText(prefix + text[2:])
        self._child_container.setVisible(self._expanded)

    def _emit_page(self, page_id):
        self.toggled.emit(page_id)

    def collapse(self):
        if self._expanded:
            self._toggle()

    def set_active_child(self, page_id):
        for pid, btn in self._child_buttons.items():
            is_active = pid == page_id
            btn.setProperty("active", is_active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        if page_id in self._child_buttons and not self._expanded:
            self._toggle()

    def set_active(self, active):
        self._header.setProperty("active", active)
        self._header.style().unpolish(self._header)
        self._header.style().polish(self._header)


class Sidebar(QScrollArea):
    page_selected = pyqtSignal(str)

    SECTIONS = [
        ("SYSTEM", [
            ("dashboard", "sidebar.dashboard", []),
            ("backup", "sidebar.backup", []),
            ("profiles", "sidebar.profiles", []),
            ("tweaks", "sidebar.tweaks", [
                ("tweaks.action_center", "tweaks.action_center"),
                ("tweaks.hibernation", "tweaks.hibernation"),
                ("tweaks.pagefile", "tweaks.pagefile"),
                ("tweaks.taskbar", "tweaks.taskbar"),
                ("tweaks.w11", "tweaks.w11"),
                ("tweaks.windows_update", "tweaks.windows_update"),
                ("tweaks.winre", "tweaks.winre"),
                ("tweaks.dotnet", "tweaks.dotnet"),
            ]),
            ("cleaner", "sidebar.cleaner", [
                ("cleaner.event_logs", "cleaner.event_logs"),
                ("cleaner.update", "cleaner.update"),
                ("cleaner.store", "cleaner.store"),
                ("cleaner.compact", "cleaner.compact"),
            ]),
            ("performance", "sidebar.performance", [
                ("performance.visual", "performance.visual"),
                ("performance.cpu", "performance.cpu"),
                ("performance.power", "performance.power"),
                ("performance.startup", "performance.startup"),
                ("performance.disk", "performance.disk"),
            ]),
            ("system", "sidebar.system", [
                ("system_tools.benchmark", "system.disk_bench"),
                ("system_tools.users", "system.users"),
                ("system_tools.gaming", "system.gaming"),
                ("system_tools.audio", "system.audio"),
                ("system_tools.cmd_schemes", "system.cmd_schemes"),
                ("system_tools.explorer", "system.explorer"),
            ]),
            ("wsl", "sidebar.wsl", [
                ("wsl.manager", "wsl.manager"),
            ]),
            ("scheduled_tasks", "sidebar.scheduled_tasks", []),
            ("windows_update", "sidebar.windows_update", []),
            ("env_vars", "sidebar.env_vars", []),
        ]),
        ("NETWORK", [
            ("network_dns", "sidebar.network_dns", [
                ("network_dns.dns", "network_dns.dns"),
                ("network_dns.utilities", "network_dns.utilities"),
                ("network_dns.hosts", "network_dns.hosts"),
                ("network_dns.ipv6", "network_dns.ipv6_label"),
            ]),
        ]),
        ("PRIVACY", [
            ("privacy", "sidebar.privacy", [
                ("privacy.telemetry", "privacy.telemetry"),
                ("privacy.cortana", "privacy.cortana"),
                ("privacy.ads", "privacy.ads"),
                ("privacy.location", "privacy.location"),
                ("privacy.camera", "privacy.camera"),
                ("privacy.mic", "privacy.mic"),
                ("privacy.diagnostic", "privacy.diagnostic"),
            ]),
        ]),
        ("CUSTOMIZE", [
            ("context_menu", "sidebar.context_menu", [
                ("context_menu.ownership", "context.ownership_add"),
                ("context_menu.shortcuts", "context.shortcuts_label"),
                ("context_menu.w11_menu", "context.w11_menu"),
            ]),
            ("uwp", "sidebar.uwp", [
                ("uwp.xbox", "uwp.xbox_label"),
                ("uwp.microsoft", "uwp.microsoft_label"),
                ("uwp.clipboard", "uwp.clipboard_label"),
                ("uwp.miracast", "uwp.miracast"),
            ]),
            ("personalize", "sidebar.personalize", [
                ("personalize.dwm", "personalize.dwm_title"),
                ("personalize.themes", "personalize.themes"),
                ("personalize.wallpapers", "personalize.wallpaper_title"),
            ]),
            ("file_explorer", "sidebar.file_explorer", [
                ("file_explorer.general", "file_explorer.general"),
                ("file_explorer.launch", "file_explorer.launch_label"),
                ("file_explorer.path", "file_explorer.path"),
                ("file_explorer.view", "file_explorer.view"),
            ]),
            ("installers", "sidebar.installers", [
                ("installers.browsers", "installers.browsers_label"),
                ("installers.media", "installers.media_label"),
                ("installers.drivers", "installers.drivers_label"),
                ("installers.microsoft", "installers.microsoft_label"),
                ("installers.utilities", "installers.utilities_label"),
                ("installers.devtools", "installers.devtools_label"),
                ("installers.gaming", "installers.gaming_label"),
                ("installers.security", "installers.security_label"),
            ]),
        ]),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setObjectName("sidebar")
        self.setFixedWidth(250)
        self._flat_buttons = {}
        self._groups = {}
        self._active_id = None
        self._module_to_parent = {}

        container = QWidget()
        self._layout = QVBoxLayout(container)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.setWidget(container)

        logo = QLabel("ANONBOT\nTOOLBOX")
        logo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        logo.setFixedHeight(72)
        logo.setObjectName("sidebarLogo")
        self._layout.addWidget(logo)

        for section_title, items in self.SECTIONS:
            header = QLabel(section_title)
            header.setObjectName("sidebarSection")
            header.setAlignment(Qt.AlignmentFlag.AlignLeft)
            header.setFixedHeight(28)
            self._layout.addWidget(header)

            for page_id, label_key, children in items:
                if children:
                    for child_id, _ in children:
                        mod = child_id.split(".")[0]
                        self._module_to_parent[mod] = page_id
                    group = _CollapsibleGroup(page_id, tr(label_key), children)
                    group.toggled.connect(self._on_child_click)
                    self._layout.addWidget(group)
                    self._groups[page_id] = group
                else:
                    btn = QPushButton(tr(label_key))
                    btn.setObjectName("sidebarBtn")
                    btn.setFlat(True)
                    btn.setCursor(Qt.CursorShape.PointingHandCursor)
                    btn.setFixedHeight(36)
                    btn.clicked.connect(lambda checked=False, pid=page_id: self._on_flat_click(pid))
                    self._layout.addWidget(btn)
                    self._flat_buttons[page_id] = btn

            spacer = QWidget()
            spacer.setFixedHeight(4)
            self._layout.addWidget(spacer)

        self._layout.addStretch()

    def rebuild(self):
        for pid, btn in self._flat_buttons.items():
            btn.deleteLater()
        for gid, group in self._groups.items():
            group.deleteLater()
        self._flat_buttons.clear()
        self._groups.clear()
        self._module_to_parent.clear()
        while self._layout.count():
            item = self._layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        logo = QLabel("ANONBOT\nTOOLBOX")
        logo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        logo.setFixedHeight(72)
        logo.setObjectName("sidebarLogo")
        self._layout.addWidget(logo)
        for section_title, items in self.SECTIONS:
            header = QLabel(section_title)
            header.setObjectName("sidebarSection")
            header.setAlignment(Qt.AlignmentFlag.AlignLeft)
            header.setFixedHeight(28)
            self._layout.addWidget(header)
            for page_id, label_key, children in items:
                if children:
                    for child_id, _ in children:
                        mod = child_id.split(".")[0]
                        self._module_to_parent[mod] = page_id
                    group = _CollapsibleGroup(page_id, tr(label_key), children)
                    group.toggled.connect(self._on_child_click)
                    self._layout.addWidget(group)
                    self._groups[page_id] = group
                else:
                    btn = QPushButton(tr(label_key))
                    btn.setObjectName("sidebarBtn")
                    btn.setFlat(True)
                    btn.setCursor(Qt.CursorShape.PointingHandCursor)
                    btn.setFixedHeight(36)
                    btn.clicked.connect(lambda checked=False, pid=page_id: self._on_flat_click(pid))
                    self._layout.addWidget(btn)
                    self._flat_buttons[page_id] = btn
            spacer = QWidget()
            spacer.setFixedHeight(4)
            self._layout.addWidget(spacer)
        self._layout.addStretch()

    def _on_flat_click(self, page_id):
        self._set_active_flat(page_id)
        self.page_selected.emit(page_id)

    def _on_child_click(self, page_id):
        self._set_active_child(page_id)
        self.page_selected.emit(page_id)

    def _set_active_flat(self, page_id):
        for pid, btn in self._flat_buttons.items():
            is_active = pid == page_id
            btn.setProperty("active", is_active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        for gid, group in self._groups.items():
            group.set_active(False)
            group.collapse()
        self._active_id = page_id

    def _set_active_child(self, page_id):
        module = page_id.split(".")[0]
        parent = self._module_to_parent.get(module, module)
        for gid, group in self._groups.items():
            is_active = gid == parent
            group.set_active(is_active)
            if is_active:
                group.set_active_child(page_id)
            else:
                group.collapse()
                group.set_active(False)
        for pid, btn in self._flat_buttons.items():
            btn.setProperty("active", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._active_id = page_id

    def set_active(self, page_id):
        module = page_id.split(".")[0]
        if module == page_id:
            if page_id in self._flat_buttons:
                self._set_active_flat(page_id)
            return
        self._set_active_child(page_id)
