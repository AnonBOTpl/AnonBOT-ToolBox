import os
from PyQt6.QtWidgets import QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from i18n import tr
from core.registry import get_snapshots, restore_snapshot
from ui.widgets import Separator
from modules.utils import make_button


def show_page(window, page_id):
    window.set_page_title("💾 " + tr("backup.title"))
    page = window._pages.get(page_id)
    if not page:
        return
    page.clear()
    page.add_section(tr("backup.restore"))
    snapshots = get_snapshots()
    if not snapshots:
        info = QLabel(tr("backup.no_backups"))
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("font-size: 13px; padding: 32px; color: #94a3b8;")
        page.add_widget(info)
        return
    for snap in snapshots:
        data = snap["data"]
        ts = data.get("timestamp", "unknown")
        mod = data.get("module", "unknown")
        count = len(data.get("entries", []))
        label = QLabel(f"[{mod}] {ts} ({count} entries)")
        label.setStyleSheet("font-size: 12px; padding: 4px 0;")
        page.add_widget(label)
        btn = QPushButton(tr("backup.restore_btn"))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(36)
        btn.clicked.connect(lambda checked=False, p=snap["file"]: _do_restore(window, p))
        page.add_widget(Separator())


def _do_restore(window, path):
    from PyQt6.QtWidgets import QMessageBox
    result = QMessageBox.question(
        window, tr("backup.confirm_title"),
        tr("backup.confirm_msg"),
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if result != QMessageBox.StandardButton.Yes:
        return
    count = restore_snapshot(path)
    window.log(f"Restored {count} registry entries from backup", "success")
    delete = QMessageBox.question(
        window, tr("backup.delete_title"),
        tr("backup.delete_msg"),
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    if delete == QMessageBox.StandardButton.Yes:
        try:
            os.remove(path)
            window.log("Backup file deleted", "info")
        except Exception as e:
            window.log(f"Failed to delete backup: {e}", "warn")
