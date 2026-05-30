import os
import socket
import subprocess
from PyQt6.QtWidgets import QTextEdit
from i18n import tr
from core.registry import set_registry
from core.system import run_cmd
from modules.utils import run_in_thread, make_button, confirm

HOSTS_PATH = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"),
                          "System32", "drivers", "etc", "hosts")


def show_page(window, page_id):
    if "." not in page_id:
        return
    sub = page_id.split(".", 1)[1]
    window.set_page_title("🌐 " + tr("network_dns.title") + " > " + tr(f"network_dns.{sub}"))
    page = window._pages.get(page_id)
    if not page:
        return
    page.clear()
    page.add_section(tr(f"network_dns.{sub}"))
    builder = _BUILDERS.get(sub)
    if builder:
        builder(window, page)
    else:
        window.log(f"Unknown page: {page_id}", "error")


def _b_dns(window, page):
    page.add_button_row_section(tr("network_dns.dns"), [
        make_button("network_dns.cloudflare", lambda: _set_dns(window, "1.1.1.1", "1.0.0.1")),
        make_button("network_dns.google", lambda: _set_dns(window, "8.8.8.8", "8.8.4.4")),
        make_button("network_dns.quad9", lambda: _set_dns(window, "9.9.9.9", "149.112.112.112")),
        make_button("network_dns.automatic", lambda: _set_dns_auto(window)),
    ])


def _b_utilities(window, page):
    page.add_button_row_section(tr("network_dns.utilities_label"), [
        make_button("network_dns.flush", lambda: _flush_dns(window)),
        make_button("network_dns.reset", lambda: _reset_network(window)),
    ])


def _b_hosts(window, page):
    page.add_button_row_section(tr("network_dns.hosts"), [
        make_button("network_dns.block_spy", lambda: _block_spyware(window)),
        make_button("network_dns.unblock_spy", lambda: _unblock_hosts(window)),
        make_button("network_dns.view_hosts", lambda: _view_hosts(window, page)),
        make_button("network_dns.add_entry", lambda: _add_hosts_entry(window)),
    ])


def _b_ipv6(window, page):
    page.add_button_row_section(tr("network_dns.ipv6_section"), [
        make_button("network_dns.ipv6", lambda: _toggle_ipv6(window, False)),
        make_button("network_dns.ipv6_enable", lambda: _toggle_ipv6(window, True)),
    ])


_BUILDERS = {
    "dns": _b_dns,
    "utilities": _b_utilities,
    "hosts": _b_hosts,
    "ipv6": _b_ipv6,
}


def _set_dns(window, primary, secondary):
    def task(sig):
        sig.status.emit("Setting DNS servers...")
        code, out, _ = run_cmd(["powershell", "-NoProfile", "-Command",
            "Get-NetAdapter -Physical | Where-Object Status -eq Up | Select-Object -ExpandProperty Name"])
        if code != 0 or not out.strip():
            sig.log.emit("No active network adapter found", "error")
            return
        for name in out.strip().split("\n"):
            name = name.strip()
            if name:
                run_cmd(["powershell", "-NoProfile", "-Command",
                    f"Set-DnsClientServerAddress -InterfaceAlias '{name}' "
                    f"-ServerAddresses ('{primary}','{secondary}')"])
                sig.log.emit(f"DNS set to {primary} / {secondary} on {name}", "success")
    run_in_thread(task, window=window)


def _set_dns_auto(window):
    def task(sig):
        sig.status.emit("Reverting to DHCP DNS...")
        code, out, _ = run_cmd(["powershell", "-NoProfile", "-Command",
            "Get-NetAdapter -Physical | Where-Object Status -eq Up | Select-Object -ExpandProperty Name"])
        if code != 0 or not out.strip():
            sig.log.emit("No active network adapter found", "error")
            return
        for name in out.strip().split("\n"):
            name = name.strip()
            if name:
                run_cmd(["powershell", "-NoProfile", "-Command",
                    f"Set-DnsClientServerAddress -InterfaceAlias '{name}' -ResetServerAddresses"])
                sig.log.emit(f"DNS set to DHCP (auto) on {name}", "success")
    run_in_thread(task, window=window)


def _flush_dns(window):
    code, out, err = run_cmd(["ipconfig", "/flushdns"])
    window.log("DNS cache flushed" if code == 0 else f"DNS flush failed: {err}",
               "success" if code == 0 else "error")


def _reset_network(window):
    def task(sig):
        run_cmd(["netsh", "int", "ip", "reset"])
        run_cmd(["netsh", "winsock", "reset"])
        sig.log.emit("TCP/IP and Winsock reset. Restart required.", "success")
    run_in_thread(task, window=window)


SPYWARE_DOMAINS = [
    "0.0.0.0 tracking.opencandy.com.s3.amazonaws.com",
    "0.0.0.0 api.spotify.com", "0.0.0.0 www.google-analytics.com",
    "0.0.0.0 ssl.google-analytics.com", "0.0.0.0 ads.youtube.com",
    "0.0.0.0 doubleclick.net", "0.0.0.0 www.googletagmanager.com",
]


def _block_spyware(window):
    if not confirm(window, "Block spyware domains by modifying the hosts file?"):
        return
    try:
        if not os.path.exists(HOSTS_PATH):
            window.log("Hosts file not found", "error")
            return
        with open(HOSTS_PATH, "r") as f:
            existing = f.read()
        added = 0
        with open(HOSTS_PATH, "a") as f:
            for domain in SPYWARE_DOMAINS:
                hostname = domain.split()[-1]
                if hostname not in existing:
                    f.write(f"\n{domain}")
                    added += 1
        window.log(f"Added {added} spyware domains to hosts file", "success")
    except Exception as e:
        window.log(f"Failed to modify hosts: {e}", "error")


def _unblock_hosts(window):
    try:
        with open(HOSTS_PATH, "r") as f:
            lines = f.readlines()
        with open(HOSTS_PATH, "w") as f:
            for line in lines:
                if not any(domain.split()[-1] in line for domain in SPYWARE_DOMAINS):
                    f.write(line)
        window.log("Spyware domains removed from hosts", "success")
    except Exception as e:
        window.log(f"Failed: {e}", "error")


def _toggle_ipv6(window, enable):
    set_registry(r"HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip6\Parameters",
                 "DisabledComponents", 0 if enable else 255)
    window.log(f"IPv6 {'enabled' if enable else 'disabled'}. Restart required.", "success")


def _view_hosts(window, page):
    try:
        with open(HOSTS_PATH, "r") as f:
            content = f.read()
        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(content)
        text.setMinimumHeight(300)
        page.add_widget(text)
        window.log(f"Hosts file displayed ({len(content.splitlines())} lines)", "info")
    except Exception as e:
        window.log(f"Failed to read hosts: {e}", "error")


def _is_valid_ip(ip):
    import re
    ip = ip.strip()
    if ip == "0.0.0.0" or ip == "127.0.0.1" or ip == "::1":
        return True
    parts = ip.split(".")
    if len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
        return True
    try:
        socket.inet_pton(socket.AF_INET6, ip)
        return True
    except (socket.error, OSError):
        return False


def _add_hosts_entry(window):
    from PyQt6.QtWidgets import QInputDialog, QLineEdit
    ip, ok = QInputDialog.getText(window, tr("network_dns.add_entry"),
                                  "IP address:", QLineEdit.EchoMode.Normal, "0.0.0.0")
    if not ok or not ip:
        return
    ip = ip.strip()
    if not _is_valid_ip(ip):
        window.log(f"Invalid IP address: {ip}", "error")
        return
    domain, ok = QInputDialog.getText(window, tr("network_dns.add_entry"),
                                      "Domain:", QLineEdit.EchoMode.Normal)
    if not ok or not domain:
        return
    domain = domain.strip().lower()
    if not domain or " " in domain or not "." in domain:
        window.log(f"Invalid domain: {domain}", "error")
        return
    try:
        with open(HOSTS_PATH, "a") as f:
            f.write(f"\n{ip} {domain}")
            window.log(f"Added {ip} {domain} to hosts", "success")
    except Exception as e:
        window.log(f"Failed: {e}", "error")
