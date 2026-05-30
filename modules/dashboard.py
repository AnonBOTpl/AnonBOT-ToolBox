from PyQt6.QtWidgets import QLabel, QProgressBar, QPushButton
from PyQt6.QtCore import Qt
from i18n import tr
from core.registry import get_registry
from modules.utils import make_button


def show_page(window, page_id=None):
    show_dashboard(window)


def show_dashboard(window):
    window.set_page_title("🏠 " + tr("dashboard.title"))
    page = window._pages.get("dashboard")
    if not page:
        return
    page.clear()

    title = QLabel(tr("dashboard.title"))
    title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 16px 0;")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    page.add_widget(title)

    subtitle = QLabel(tr("dashboard.subtitle"))
    subtitle.setStyleSheet("font-size: 14px; margin: 0 0 24px 0;")
    subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
    page.add_widget(subtitle)

    score = _health_score()
    bar = QProgressBar()
    bar.setRange(0, 100)
    bar.setValue(score)
    bar.setFixedHeight(24)
    bar.setTextVisible(True)
    bar.setFormat(f"{tr('dashboard.score')}: {score}/100")
    if score < 40:
        bar.setStyleSheet("QProgressBar::chunk { background: #ef4444; } QProgressBar { text-align: center; font-size: 13px; }")
    elif score < 70:
        bar.setStyleSheet("QProgressBar::chunk { background: #eab308; } QProgressBar { text-align: center; font-size: 13px; }")
    else:
        bar.setStyleSheet("QProgressBar::chunk { background: #22c55e; } QProgressBar { text-align: center; font-size: 13px; }")
    page.add_widget(bar)

    rescan_btn = QPushButton(tr("dashboard.rescan"))
    rescan_btn.setCursor(Qt.CursorShape.PointingHandCursor)
    rescan_btn.setMinimumHeight(36)
    rescan_btn.clicked.connect(lambda: _rescan(window))
    page._layout.addWidget(rescan_btn)

    info = QLabel(tr("dashboard.info"))
    info.setWordWrap(True)
    info.setStyleSheet("font-size: 13px; padding: 16px;")
    info.setAlignment(Qt.AlignmentFlag.AlignCenter)
    page.add_widget(info)


def _health_score():
    score = 0

    if get_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry") == 0:
        score += 10
    if get_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search", "AllowCortana") == 0:
        score += 5
    if get_registry(r"HKCU:\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo", "Enabled") == 0:
        score += 5
    if get_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\AppPrivacy", "LetAppsAccessCamera") == 2:
        score += 5
    if get_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\AppPrivacy", "LetAppsAccessMicrophone") == 2:
        score += 5
    if get_registry(r"HKLM:\SYSTEM\CurrentControlSet\Services\lfsvc", "Start") == 4:
        score += 5
    if get_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot", "TurnOffWindowsCopilot") == 1:
        score += 5
    if get_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Dsh", "AllowNewsAndInterests") == 0:
        score += 5
    if get_registry(r"HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting") == 2:
        score += 5
    return min(score, 100)


def _rescan(window):
    window.log("Re-scanning system health...", "info")
    show_dashboard(window)
