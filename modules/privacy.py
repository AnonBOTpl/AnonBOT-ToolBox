from i18n import tr
from core.registry import set_registry
from core.system import run_cmd, set_service_startup
from modules.utils import make_button, confirm


def show_page(window, page_id):
    if "." not in page_id:
        return
    sub = page_id.split(".", 1)[1]
    window.set_page_title("🛡 " + tr("privacy.title") + " > " + tr(f"privacy.{sub}"))
    page = window._pages.get(page_id)
    if not page:
        return
    page.clear()
    page.add_section(tr(f"privacy.{sub}"))
    builder = _BUILDERS.get(sub)
    if builder:
        builder(window, page)
    else:
        window.log(f"Unknown page: {page_id}", "error")


def _b_telemetry(window, page):
    page.add_button_row_section(tr("privacy.telemetry"), [
        make_button("privacy.telemetry_disable", lambda: _disable_telemetry(window)),
    ])


def _b_cortana(window, page):
    page.add_button_row_section(tr("privacy.cortana"), [
        make_button("privacy.cortana_disable", lambda: _disable_cortana(window)),
    ])


def _b_ads(window, page):
    page.add_button_row_section(tr("privacy.ads"), [
        make_button("privacy.ads_disable", lambda: _disable_ads(window)),
    ])


def _b_location(window, page):
    page.add_button_row_section(tr("privacy.location"), [
        make_button("privacy.location_disable", lambda: _disable_location(window)),
    ])


def _b_camera(window, page):
    page.add_button_row_section(tr("privacy.camera"), [
        make_button("privacy.camera_disable", lambda: _disable_camera(window)),
    ])


def _b_mic(window, page):
    page.add_button_row_section(tr("privacy.mic"), [
        make_button("privacy.mic_disable", lambda: _disable_mic(window)),
    ])


def _b_diagnostic(window, page):
    page.add_button_row_section(tr("privacy.diagnostic"), [
        make_button("privacy.diagnostic_min", lambda: _diagnostic_min(window)),
    ])


_BUILDERS = {
    "telemetry": _b_telemetry,
    "cortana": _b_cortana,
    "ads": _b_ads,
    "location": _b_location,
    "camera": _b_camera,
    "mic": _b_mic,
    "diagnostic": _b_diagnostic,
}


def _disable_telemetry(window):
    if not confirm(window, "Disable telemetry? This modifies system services and registry."):
        return
    for path in [r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection",
                  r"HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection",
                  r"HKLM:\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Policies\DataCollection"]:
        set_registry(path, "AllowTelemetry", 0)
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection", "MaxTelemetryAllowed", 0)
    set_service_startup("DiagTrack", "Disabled")
    set_service_startup("dmwappushservice", "Disabled")
    run_cmd(["sc.exe", "stop", "DiagTrack"])
    run_cmd(["sc.exe", "stop", "dmwappushservice"])
    window.log("Telemetry disabled. Restart recommended.", "success")


def _disable_cortana(window):
    for key in [r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search"]:
        set_registry(key, "AllowCortana", 0)
        set_registry(key, "AllowCortanaAboveLock", 0)
        set_registry(key, "AllowSearchToUseLocation", 0)
    set_registry(r"HKCU:\Software\Microsoft\Personalization\Settings", "AcceptedPrivacyPolicy", 0)
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\InputPersonalization", "AllowInputPersonalization", 0)
    window.log("Cortana disabled", "success")


def _disable_ads(window):
    set_registry(r"HKCU:\Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo", "Enabled", 0)
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\AdvertisingInfo", "DisabledByGroupPolicy", 1)
    window.log("Advertising ID disabled", "success")


def _disable_location(window):
    set_registry(r"HKLM:\SYSTEM\CurrentControlSet\Services\lfsvc", "Start", 4)
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors", "DisableLocation", 1)
    set_registry(r"HKCU:\Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location",
                 "Value", "Deny")
    run_cmd(["sc.exe", "stop", "lfsvc"])
    window.log("Location tracking disabled", "success")


def _disable_camera(window):
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\AppPrivacy", "LetAppsAccessCamera", 2)
    window.log("Camera access disabled for all apps", "success")


def _disable_mic(window):
    set_registry(r"HKLM:\SOFTWARE\Policies\Microsoft\Windows\AppPrivacy", "LetAppsAccessMicrophone", 2)
    window.log("Microphone access disabled for all apps", "success")


def _diagnostic_min(window):
    set_registry(r"HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Diagnostics\DiagTrack", "SubmittedTelemetry", 0)
    set_registry(r"HKCU:\Software\Microsoft\Windows\CurrentVersion\Diagnostics\DiagTrack", "SubmittedTelemetry", 0)
    window.log("Diagnostic data set to Required Only", "success")
