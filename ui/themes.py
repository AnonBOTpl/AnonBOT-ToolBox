import winreg

ACCENT_COLORS = {
    "#7c3aed": "Purple",
    "#2563eb": "Blue",
    "#16a34a": "Green",
    "#dc2626": "Red",
    "#ea580c": "Orange",
    "#db2777": "Pink",
    "#0d9488": "Teal",
    "#0891b2": "Cyan",
}


def is_windows_dark():
    key = None
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return value == 0
    except Exception:
        return True
    finally:
        if key is not None:
            try:
                winreg.CloseKey(key)
            except Exception:
                pass


_DARK_QSS = """
QMainWindow, QDialog { background: #1e1e2e; }
QMainWindow > QWidget { background: #1e1e2e; }
QPushButton { background: #27272a; color: #e2e8f0; border: 1px solid #3f3f46; border-radius: 6px; padding: 6px 16px; font-size: 13px; min-height: 36px; }
QPushButton:hover { background: #3f3f46; border-color: ACCENT_COLOR; }
QPushButton:pressed { background: #1e1e2e; }
QPushButton[active="true"] { background: ACCENT_COLOR; color: #fff; border-color: ACCENT_COLOR; }
QLabel { color: #e2e8f0; }
QLabel#breadcrumb { color: #94a3b8; font-size: 11px; font-weight: 500; padding-right: 12px; }
QLabel#sidebarSection { color: ACCENT_COLOR; font-size: 11px; font-weight: 700; padding: 0 12px; letter-spacing: 1px; }
QLabel#pageTitle { font-size: 16px; font-weight: 600; }
QLabel#sysInfo { font-size: 11px; color: #64748b; }
QLabel#sidebarLogo { font-size: 13px; font-weight: 700; color: ACCENT_COLOR; padding: 16px 12px 8px; background: #16161e; }
QPushButton#sidebarBtn, QPushButton#sidebarSubBtn { background: transparent; border: none; border-radius: 0; text-align: left; padding: 0 12px; font-size: 13px; min-height: 36px; color: #94a3b8; }
QPushButton#sidebarBtn:hover, QPushButton#sidebarSubBtn:hover { background: #2a2a3e; color: #e2e8f0; }
QPushButton#sidebarBtn[active="true"], QPushButton#sidebarSubBtn[active="true"] { background: #2a2a3e; color: ACCENT_COLOR; border-left: 3px solid ACCENT_COLOR; }
QPushButton#sidebarSubBtn { padding: 0 12px 0 24px; font-size: 12px; min-height: 32px; }
QPushButton#settingsBtn { background: transparent; border: none; color: #94a3b8; font-size: 12px; }
QPushButton#settingsBtn:hover { color: ACCENT_COLOR; }
QPushButton#exportLogBtn { background: transparent; border: none; color: #64748b; font-size: 11px; }
QPushButton#exportLogBtn:hover { color: #e2e8f0; }
QProgressBar { background: #3f3f46; border: none; border-radius: 2px; height: 4px; text-align: center; }
QProgressBar::chunk { background: ACCENT_COLOR; border-radius: 2px; }
QScrollBar:vertical { background: #16161e; width: 8px; }
QScrollBar::handle:vertical { background: #3f3f46; border-radius: 4px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #16161e; height: 8px; }
QScrollBar::handle:horizontal { background: #3f3f46; border-radius: 4px; min-width: 30px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QComboBox { background: #27272a; color: #e2e8f0; border: 1px solid #3f3f46; border-radius: 6px; padding: 6px 12px; font-size: 13px; }
QComboBox:hover { border-color: ACCENT_COLOR; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView { background: #1e1e2e; color: #e2e8f0; selection-background-color: ACCENT_COLOR; }
QScrollArea#sidebar { background: #16161e; }
QScrollArea#sidebar QWidget { background: transparent; }
QWidget#headerWidget { background: #1e1e2e; border-bottom: 1px solid #3f3f46; }
QWidget#rightPanel { background: #1e1e2e; }
QWidget#bottomBar { background: #1e1e2e; border-top: 1px solid #3f3f46; }
"""

_LIGHT_QSS = """
QMainWindow, QDialog { background: #f8fafc; }
QMainWindow > QWidget { background: #f8fafc; }
QPushButton { background: #ffffff; color: #1e293b; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 16px; font-size: 13px; min-height: 36px; }
QPushButton:hover { background: #f1f5f9; border-color: ACCENT_COLOR; }
QPushButton:pressed { background: #e2e8f0; }
QPushButton[active="true"] { background: ACCENT_COLOR; color: #fff; border-color: ACCENT_COLOR; }
QLabel { color: #1e293b; }
QLabel#breadcrumb { color: #64748b; font-size: 11px; font-weight: 500; padding-right: 12px; }
QLabel#sidebarSection { color: #64748b; font-size: 11px; font-weight: 700; padding: 0 12px; letter-spacing: 1px; }
QLabel#pageTitle { font-size: 16px; font-weight: 600; }
QLabel#sysInfo { font-size: 11px; color: #94a3b8; }
QLabel#sidebarLogo { font-size: 13px; font-weight: 700; color: #1e293b; padding: 16px 12px 8px; background: #f1f5f9; }
QPushButton#sidebarBtn, QPushButton#sidebarSubBtn { background: transparent; border: none; border-radius: 0; text-align: left; padding: 0 12px; font-size: 13px; min-height: 36px; color: #475569; }
QPushButton#sidebarBtn:hover, QPushButton#sidebarSubBtn:hover { background: #e2e8f0; color: #1e293b; }
QPushButton#sidebarBtn[active="true"], QPushButton#sidebarSubBtn[active="true"] { background: #e2e8f0; color: ACCENT_COLOR; border-left: 3px solid ACCENT_COLOR; }
QPushButton#sidebarSubBtn { padding: 0 12px 0 24px; font-size: 12px; min-height: 32px; }
QPushButton#settingsBtn { background: transparent; border: none; color: #64748b; font-size: 12px; }
QPushButton#settingsBtn:hover { color: ACCENT_COLOR; }
QPushButton#exportLogBtn { background: transparent; border: none; color: #94a3b8; font-size: 11px; }
QPushButton#exportLogBtn:hover { color: #1e293b; }
QCheckBox { color: #475569; spacing: 6px; font-size: 12px; }
QCheckBox::indicator { width: 16px; height: 16px; }
QProgressBar { background: #cbd5e1; border: none; border-radius: 2px; height: 4px; text-align: center; }
QProgressBar::chunk { background: ACCENT_COLOR; border-radius: 2px; }
QScrollBar:vertical { background: #f1f5f9; width: 8px; }
QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 4px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #f1f5f9; height: 8px; }
QScrollBar::handle:horizontal { background: #cbd5e1; border-radius: 4px; min-width: 30px; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }
QComboBox { background: #ffffff; color: #1e293b; border: 1px solid #cbd5e1; border-radius: 6px; padding: 6px 12px; font-size: 13px; }
QComboBox:hover { border-color: ACCENT_COLOR; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView { background: #ffffff; color: #1e293b; selection-background-color: ACCENT_COLOR; }
QScrollArea#sidebar { background: #f1f5f9; }
QScrollArea#sidebar QWidget { background: transparent; }
QWidget#headerWidget { background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
QWidget#rightPanel { background: #f8fafc; }
QWidget#bottomBar { background: #f8fafc; border-top: 1px solid #e2e8f0; }
"""


def get_qss(accent_color="#7c3aed", theme_mode="auto"):
    if theme_mode == "dark":
        dark = True
    elif theme_mode == "light":
        dark = False
    else:
        dark = is_windows_dark()
    template = _DARK_QSS if dark else _LIGHT_QSS
    return template.replace("ACCENT_COLOR", accent_color)


def get_colors(dark=None):
    if dark is None:
        dark = is_windows_dark()
    if dark:
        return {
            "bg": "#1e1e2e", "sidebar": "#16161e", "accent": "#7c3aed",
            "text": "#e2e8f0", "text_secondary": "#94a3b8", "text_muted": "#64748b",
            "card": "#27272a", "card_border": "#3f3f46",
            "success": "#22c55e", "warning": "#eab308", "danger": "#ef4444", "info": "#60a5fa",
        }
    else:
        return {
            "bg": "#f8fafc", "sidebar": "#f1f5f9", "accent": "#7c3aed",
            "text": "#1e293b", "text_secondary": "#475569", "text_muted": "#94a3b8",
            "card": "#ffffff", "card_border": "#cbd5e1",
            "success": "#16a34a", "warning": "#ca8a04", "danger": "#dc2626", "info": "#2563eb",
        }
