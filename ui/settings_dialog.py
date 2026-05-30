from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QWidget, QColorDialog, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from i18n import tr, get_i18n
from ui.themes import ACCENT_COLORS, get_qss


class ColorSwatch(QPushButton):
    selected = pyqtSignal(str)

    def __init__(self, hex_color, parent=None):
        super().__init__(parent)
        self._hex = hex_color
        self.setFixedSize(32, 32)
        self.setStyleSheet(f"""
            QPushButton {{
                background: {hex_color}; border: 2px solid transparent;
                border-radius: 16px; min-height: 32px; min-width: 32px;
            }}
            QPushButton:hover {{ border-color: #94a3b8; }}
            QPushButton[active="true"] {{ border-color: #fff; }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(ACCENT_COLORS.get(hex_color, hex_color))
        self.clicked.connect(lambda: self.selected.emit(hex_color))


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("settings.title"))
        self.setMinimumWidth(420)
        self.setMinimumHeight(400)
        self._parent = parent
        self._current_accent = "#7c3aed"
        self._current_mode = "auto"
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel(tr("settings.title"))
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        layout.addWidget(QLabel(tr("settings.accent_color")))
        grid = QGridLayout()
        grid.setSpacing(8)
        row, col = 0, 0
        self._swatches = []
        for hex_color in ACCENT_COLORS:
            swatch = ColorSwatch(hex_color)
            swatch.selected.connect(self._set_accent)
            grid.addWidget(swatch, row, col)
            self._swatches.append(swatch)
            col += 1
            if col > 3:
                col = 0
                row += 1

        custom_btn = QPushButton(tr("settings.custom_color"))
        custom_btn.clicked.connect(self._pick_custom)
        grid.addWidget(custom_btn, row + 1, 0, 1, 4)
        layout.addLayout(grid)

        self._mode_combo = QComboBox()
        self._mode_combo.addItem(tr("settings.theme_auto"), "auto")
        self._mode_combo.addItem(tr("settings.theme_dark"), "dark")
        self._mode_combo.addItem(tr("settings.theme_light"), "light")
        layout.addWidget(QLabel(tr("settings.theme_mode")))
        layout.addWidget(self._mode_combo)

        self._lang_combo = QComboBox()
        self._lang_combo.addItem(tr("lang.auto"), "auto")
        self._lang_combo.addItem(tr("lang.en"), "en")
        self._lang_combo.addItem(tr("lang.pl"), "pl")
        layout.addWidget(QLabel(tr("settings.language")))
        layout.addWidget(self._lang_combo)

        hint = QLabel(tr("settings.restart_hint"))
        hint.setStyleSheet("font-size: 11px; color: #64748b;")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton(tr("settings.cancel"))
        cancel_btn.clicked.connect(self.reject)
        apply_btn = QPushButton(tr("settings.apply"))
        apply_btn.clicked.connect(self._apply)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)

        self._mode_combo.currentIndexChanged.connect(self._update_preview)
        self._lang_combo.currentIndexChanged.connect(self._update_preview)

    def _set_accent(self, hex_color):
        self._current_accent = hex_color
        for swatch in self._swatches:
            swatch.setProperty("active", swatch._hex == hex_color)
            swatch.style().unpolish(swatch)
            swatch.style().polish(swatch)
        self._update_preview()

    def _pick_custom(self):
        color = QColorDialog.getColor(QColor(self._current_accent), self, tr("settings.custom_color"))
        if color.isValid():
            self._set_accent(color.name())

    def _update_preview(self):
        if self._parent:
            mode = self._mode_combo.currentData()
            self._parent.setStyleSheet(get_qss(self._current_accent, mode))

    def _load_settings(self):
        import json, os
        cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        try:
            with open(cfg_path, encoding="utf-8") as f:
                cfg = json.load(f)
            accent = cfg.get("accent_color", "#7c3aed")
            if accent in ACCENT_COLORS:
                self._set_accent(accent)
            mode = cfg.get("theme_mode", "auto")
            midx = self._mode_combo.findData(mode)
            if midx >= 0:
                self._mode_combo.setCurrentIndex(midx)
            lang = cfg.get("language", "auto")
            lidx = self._lang_combo.findData(lang)
            if lidx >= 0:
                self._lang_combo.setCurrentIndex(lidx)
        except Exception:
            pass

    def _save_settings(self):
        import json, os
        cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        try:
            with open(cfg_path, encoding="utf-8") as f:
                cfg = json.load(f)
            cfg["accent_color"] = self._current_accent
            cfg["theme_mode"] = self._mode_combo.currentData()
            cfg["language"] = self._lang_combo.currentData()
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def _apply(self):
        self._save_settings()
        self.accept()
