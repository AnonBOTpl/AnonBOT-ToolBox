import json
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QPushButton, QMessageBox, QApplication
from i18n import tr


def _get_profiles():
    try:
        cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        with open(cfg_path, encoding="utf-8") as f:
            return json.load(f).get("profiles", {})
    except Exception:
        return {}


def show_page(window, page_id):
    window.set_page_title("⚡ " + tr("profiles.title"))
    page = window._pages.get(page_id)
    if not page:
        return
    page.clear()
    page.add_section(tr("profiles.title"))
    profiles = _get_profiles()
    if not profiles:
        info = QLabel(tr("profiles.none"))
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("font-size: 13px; padding: 32px; color: #94a3b8;")
        page.add_widget(info)
        return
    for key, prof in profiles.items():
        card = QLabel(f"<b>{prof['label']}</b><br>{prof['description']}")
        card.setWordWrap(True)
        card.setStyleSheet("font-size: 13px; padding: 12px; border: 1px solid #3f3f46; border-radius: 6px; margin: 4px 0;")
        page.add_widget(card)
        btn = QPushButton(tr("profiles.apply"))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(36)
        btn.clicked.connect(lambda checked=False, k=key, p=prof: _apply_profile(window, k, p))
        page._layout.addWidget(btn)


def _apply_profile(window, key, profile):
    result = QMessageBox.question(
        window, tr("profiles.confirm_title"),
        tr("profiles.confirm_msg").format(profile["label"]),
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if result != QMessageBox.StandardButton.Yes:
        return

    window.log(f"Applying profile: {profile['label']}...", "info")
    for action_path in profile.get("actions", []):
        window.log(f"Running: {action_path}", "info")
        parts = action_path.split(".")
        if len(parts) == 2:
            mod_name, func_name = parts
            window.set_status(f"Running {func_name}...")
            try:
                mod = _import_module(mod_name)
                if mod and hasattr(mod, func_name):
                    getattr(mod, func_name)(window)
                else:
                    window.log(f"Function {action_path} not found", "warn")
            except Exception as e:
                window.log(f"Failed {action_path}: {e}", "error")
        QApplication.processEvents()
    window.log(f"Profile '{profile['label']}' applied", "success")
    window.set_status(tr("app.status.ready"))


def _import_module(name):
    import importlib
    try:
        return importlib.import_module(f"modules.{name}")
    except (ImportError, ModuleNotFoundError, AttributeError):
        return None


def validate_profiles(window=None):
    profiles = _get_profiles()
    errors = []
    for key, prof in profiles.items():
        for action_path in prof.get("actions", []):
            parts = action_path.split(".")
            if len(parts) != 2:
                errors.append(f"{key}: invalid action '{action_path}'")
                continue
            mod_name, func_name = parts
            mod = _import_module(mod_name)
            if not mod:
                errors.append(f"{key}: module '{mod_name}' not found for '{action_path}'")
            elif not hasattr(mod, func_name):
                errors.append(f"{key}: function '{func_name}' not found in '{mod_name}' for '{action_path}'")
    if window:
        if errors:
            for e in errors:
                window.log(f"Profile validation: {e}", "warn")
            window.log(f"Profile validation: {len(errors)} warnings", "info")
        else:
            window.log("Profile validation: all actions OK", "info")
    return errors
