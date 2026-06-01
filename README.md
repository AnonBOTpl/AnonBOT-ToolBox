<div align="center">
  <h1>🛠️ AnonBOT Toolbox</h1>
  <p><strong>Windows optimization & customization utility — built with Python & PyQt6</strong></p>
  <p>
    <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/pyqt-6.5%2B-green?style=flat-square" alt="PyQt6">
    <img src="https://img.shields.io/badge/windows-10%2F11-0078D4?style=flat-square&logo=windows" alt="Windows">
    <img src="https://img.shields.io/badge/license-MIT-yellow?style=flat-square" alt="License">
  </p>
  <p>
    <a href="README-pl.md">🇵🇱 Polski</a>
  </p>
</div>

---

**AnonBOT Toolbox** is a desktop application for configuring, tweaking, cleaning, and personalizing Windows 10 and 11. It combines system utilities, registry tweaks, privacy controls, application installers, and visual customization in one cohesive interface — all with full Polish and English localization.

<img width="1201" height="829" alt="{C4DC17B2-BB2D-4687-8485-4C27A3E31E65}" src="https://github.com/user-attachments/assets/f4d9cf77-6b4f-4a57-bbef-690d863f7cb4" />


## ✨ Features

### 🔧 System
- **Tweaks** — disable Copilot, Widgets, Chat, OneDrive; configure Action Center, hibernation, pagefile, Taskbar, Windows Update delivery, WinRE, .NET
- **Cleaner** — clear Event Logs, Windows Update cache, Microsoft Store cache, compact OS
- **Performance** — visual effects, CPU scheduling, power plans, startup programs, disk optimization
- **System Tools** — disk benchmark, user management, gaming mode, audio settings, Explorer control panel schemes
- **Scheduled Tasks** — view, disable, re-enable Windows scheduled tasks
- **Windows Update** — check and list pending updates
- **Environment Variables** — manage system/user environment variables

### 🌐 Network
- **DNS** — switch between popular DNS providers (Google, Cloudflare, OpenDNS, etc.)
- **Utilities** — flush DNS, renew IP, reset Winsock
- **Hosts** — add/remove hosts entries with IP validation
- **IPv6** — enable or disable IPv6

### 🛡 Privacy
- **Telemetry** — disable telemetry and data collection
- **Cortana** — disable Cortana and web search
- **Ads** — disable personalized ads and suggestions
- **Location, Camera, Mic** — granular privacy toggles
- **Diagnostic** — set diagnostic data to minimum

### 🎨 Customize
- **Context Menu** — add ownership (cmd/powershell), create shortcuts, restore Windows 11 context menu
- **UWP / AppX** — remove Xbox, Microsoft bloatware, Clipboard history, Miracast
- **Personalize** — DWM color schemes (8 presets), theme tools (SecureUxTheme, WindHawk), DeviantArt theme/wallpaper searcher
- **File Explorer** — show hidden files, extensions, launch settings, path display, view configuration
- **Installers** — 28 software titles across 8 categories: browsers, media, drivers, Microsoft tools, utilities, dev tools, gaming, security — installed via winget with URL fallback

### 💾 Maintenance
- **Backup & Restore** — automatic registry snapshot before every modification; browse, inspect, and restore snapshots from the GUI
- **Profiles** — one-click apply preset configurations (Gaming, Privacy Max, Fresh Install, Office)
- **Session Log** — every action is logged with ANSI colors; exportable to `.txt`

## 🖥️ Screenshots

| Sidebar | Settings | Themes |
|---------|----------|--------|
| *(screenshot)* | *(screenshot)* | *(screenshot)* |

## 📋 Requirements

- **Windows 10** (21H2+) or **Windows 11**
- **Python 3.10+** (or use the UV-based installer which bundles it)
- **Administrator privileges** (required for registry changes and system modifications)
- **UV** (recommended) — [Install UV](https://docs.astral.sh/uv/#installation)
- **winget** (optional but recommended for software installer module)

## 🚀 Installation

### Quick start (recommended)

```batch
cd AnonBOT-ToolBox
install.bat
start.bat
```

`install.bat` will:
1. Verify UV is installed
2. Create a virtual environment (`.venv`)
3. Install PyQt6 from `requirements.txt`

### Manual setup
```batch
cd AnonBOT-ToolBox
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uv run main.py
```

> **Note**: The app auto-restarts with administrator privileges if launched without them.

## ⚙️ Configuration

User settings are stored in `config.json`:

```json
{
  "language": "en",
  "accent_color": "#7c3aed",
  "theme_mode": "auto",
  "startup_checks": true
}
```

- `language` — `"en"`, `"pl"`, or `"auto"` (system language)
- `accent_color` — any hex color (live picker in Settings)
- `theme_mode` — `"auto"`, `"dark"`, or `"light"`
- `startup_checks` — verify URLs and validate profiles on launch

## 🌐 Internationalization

The app fully supports **English** and **Polish**:
- Automatic system language detection
- Manual override in Settings → Language
- ~214 translated keys per language
- Sidebar and pages rebuild on language switch

## 🏗 Project Structure

```
AnonBOT-ToolBox/
├── core/              # Core APIs (registry, system, download)
├── ui/                # UI components (main window, sidebar, themes, settings)
├── modules/           # Feature modules (18 modules)
├── locales/           # Translation files (en.json, pl.json)
├── scripts/           # Standalone utilities
├── tests/             # Unit tests (29 tests)
├── backups/           # Registry snapshot storage
├── logs/              # Session logs
├── config.json        # User configuration
├── urls.json          # Software installer URLs
├── main.py            # Entry point
├── install.bat        # UV-based setup script
└── start.bat          # Launch script
```

## 🧪 Running Tests

```batch
uv run python -m unittest tests.test_registry tests.test_system -v
```

## 📄 License

This project is for personal use. All trademarks and product names belong to their respective owners.

---


