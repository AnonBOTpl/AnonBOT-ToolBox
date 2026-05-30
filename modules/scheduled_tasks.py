import subprocess
from i18n import tr
from modules.utils import run_in_thread, make_button, confirm

COMMON_TASKS = [
    ("\\Microsoft\\Windows\\Application Experience\\", "ProgramDataUpdater"),
    ("\\Microsoft\\Windows\\Customer Experience Improvement Program\\", "Consolidator"),
    ("\\Microsoft\\Windows\\Customer Experience Improvement Program\\", "KernelCeipTask"),
    ("\\Microsoft\\Windows\\Customer Experience Improvement Program\\", "UsbCeip"),
    ("\\Microsoft\\Windows\\DiskDiagnostic\\", "Microsoft-Windows-DiskDiagnosticDataCollector"),
    ("\\Microsoft\\Windows\\Location\\", "Notifications"),
    ("\\Microsoft\\Windows\\Windows Update\\", "Automatic App Update"),
    ("\\Microsoft\\Office\\", "OfficeTelemetryAgentFallBack"),
    ("\\Microsoft\\Office\\", "OfficeTelemetryAgentLogOn"),
    ("\\Microsoft\\Windows\\Power Efficiency Diagnostics\\", "AnalyzeSystem"),
    ("\\Microsoft\\Windows\\Application Experience\\", "StartupAppTask"),
]


def show_page(window, page_id):
    window.set_page_title(tr("scheduled_tasks.title"))
    page = window._pages.get(page_id)
    if not page:
        return
    page.clear()
    page.add_section(tr("scheduled_tasks.title"))
    _build_tasks(window, page)


def _build_tasks(window, page):
    for task_path, task_name in COMMON_TASKS:
        page.add_button_row_section(task_name, [
            make_button("scheduled_tasks.refresh", (lambda p, n: lambda: _check_task(window, p, n))(task_path, task_name)),
            make_button("scheduled_tasks.disable", (lambda p, n: lambda: _toggle_task(window, p, n, False))(task_path, task_name)),
            make_button("scheduled_tasks.enable", (lambda p, n: lambda: _toggle_task(window, p, n, True))(task_path, task_name)),
        ])


def _sanitize_ps(s):
    return s.replace("`", "``").replace("'", "''").replace("$(", "`$(")


def _check_task(window, task_path, task_name):
    def task(sig):
        try:
            safe_name = _sanitize_ps(task_name)
            safe_path = _sanitize_ps(task_path)
            r = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 f"(Get-ScheduledTask -TaskName '{safe_name}' -TaskPath '{safe_path}').State"],
                capture_output=True, text=True, timeout=15
            )
            state = r.stdout.strip()
            sig.log.emit(f"{task_name}: {state}", "info")
        except Exception as e:
            sig.log.emit(f"Failed to check {task_name}: {e}", "error")
    run_in_thread(task, window=window)


def _toggle_task(window, task_path, task_name, enable):
    action = "Enable" if enable else "Disable"
    safe_name = _sanitize_ps(task_name)
    if not confirm(window, f"{action} {task_name}?"):
        return

    def task(sig):
        sig.status.emit(f"{action}ing {task_name}...")
        cmd = "Enable-ScheduledTask" if enable else "Disable-ScheduledTask"
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 f"{cmd} -TaskName '{safe_name}' -TaskPath '{_sanitize_ps(task_path)}'"],
                check=True, timeout=30
            )
            sig.log.emit(f"{task_name}: {action}d", "success")
        except Exception as e:
            sig.log.emit(f"Failed to {action.lower()} {task_name}: {e}", "error")
    run_in_thread(task, window=window)
