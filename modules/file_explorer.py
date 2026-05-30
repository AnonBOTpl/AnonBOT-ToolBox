from i18n import tr
from core.registry import set_registry
from modules.utils import make_button

EXPLORER_ADVANCED = r"HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"


def show_page(window, page_id):
    if "." not in page_id:
        return
    sub = page_id.split(".", 1)[1]
    window.set_page_title("📁 " + tr("file_explorer.title") + " > " + tr(f"file_explorer.{sub}"))
    page = window._pages.get(page_id)
    if not page:
        return
    page.clear()
    page.add_section(tr(f"file_explorer.{sub}"))
    builder = _BUILDERS.get(sub)
    if builder:
        builder(window, page)
    else:
        window.log(f"Unknown page: {page_id}", "error")


def _b_general(window, page):
    page.add_button_row_section(tr("file_explorer.general"), [
        make_button("file_explorer.hidden", lambda: _hidden_files(window, True)),
        make_button("file_explorer.hide_hidden", lambda: _hidden_files(window, False)),
        make_button("file_explorer.extensions", lambda: _extensions(window, True)),
        make_button("file_explorer.hide_extensions", lambda: _extensions(window, False)),
    ])


def _b_launch(window, page):
    page.add_button_row_section(tr("cleaner.compact"), [
        make_button("file_explorer.this_pc", lambda: _launch_to(window, "ThisPC")),
        make_button("file_explorer.quick_access", lambda: _launch_to(window, "QuickAccess")),
        make_button("file_explorer.folders", lambda: _restore_folders(window, True)),
        make_button("file_explorer.no_restore", lambda: _restore_folders(window, False)),
    ])


def _b_path(window, page):
    page.add_button_row_section(tr("file_explorer.path"), [
        make_button("file_explorer.path", lambda: _full_path(window, True)),
        make_button("file_explorer.hide_path", lambda: _full_path(window, False)),
    ])


def _b_view(window, page):
    page.add_button_row_section(tr("file_explorer.view"), [
        make_button("file_explorer.disable_grouping", lambda: _grouping(window, False)),
        make_button("file_explorer.enable_grouping", lambda: _grouping(window, True)),
        make_button("file_explorer.compact", lambda: _compact_view(window)),
    ])


_BUILDERS = {
    "general": _b_general,
    "launch": _b_launch,
    "path": _b_path,
    "view": _b_view,
}


def _hidden_files(window, show):
    val = 1 if show else 2
    set_registry(EXPLORER_ADVANCED, "Hidden", val)
    set_registry(EXPLORER_ADVANCED, "ShowSuperHidden", int(show))
    window.log(f"Hidden files {'shown' if show else 'hidden'}", "success")


def _extensions(window, show):
    set_registry(EXPLORER_ADVANCED, "HideFileExt", 0 if show else 1)
    window.log(f"File extensions {'shown' if show else 'hidden'}", "success")


def _launch_to(window, target):
    set_registry(EXPLORER_ADVANCED, "LaunchTo", 1 if target == "ThisPC" else 0)
    window.log(f"Explorer opens to {target}", "success")


def _restore_folders(window, restore):
    set_registry(EXPLORER_ADVANCED, "RestorePreviousFolderAtLogon", 1 if restore else 0)
    window.log(f"Restore previous folders: {'on' if restore else 'off'}", "success")


def _full_path(window, show):
    set_registry(EXPLORER_ADVANCED, "FullPathTitle", 1 if show else 0)
    window.log(f"Full path in title bar: {'shown' if show else 'hidden'}", "success")


def _grouping(window, enable):
    set_registry(EXPLORER_ADVANCED, "AutoGroupInListView", 1 if enable else 0)
    window.log(f"Auto-grouping: {'on' if enable else 'off'}", "success")


def _compact_view(window):
    set_registry(EXPLORER_ADVANCED, "UseCompactMode", 1)
    window.log("Compact view mode enabled. Restart Explorer.", "success")
