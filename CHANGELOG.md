# Changelog

## [0.2.0] — 2026-05-30

### Fixed
- **DeviantArt tag generation**: replaced broken `CurrentBuild` registry value with `DisplayVersion` for accurate Windows version detection in theme search
- **Sidebar label**: fixed `personalize.theme_title` → `personalize.themes` — the key was missing from locale files, causing the raw key name to appear in the sidebar
- **Breadcrumb**: added missing `sidebar.system_tools` locale key — system tools pages were showing a raw key in the breadcrumb
- **Config dual-write conflict**: removed `core/config.py` and `config.ini`; all user settings now consistently read/write from `config.json` only

### Added
- **Wallpapers section**: new "Search Wallpapers on DeviantArt" button that opens `deviantart.com/tag/wallpapers`
- **Language switch UI refresh**: `Sidebar.rebuild()` and `_refresh_language()` now reload the sidebar labels and re-render the current page when the language is changed in Settings
- **Missing i18n keys**: added `personalize.search_themes`, `personalize.search_wallpapers`, and `sidebar.system_tools` to both English and Polish locale files
- **i18n audit**: comprehensive verification of all ~214 keys × 2 locales — no missing keys remain

### Changed
- **Themes section**: restored "Search Themes on DeviantArt" button alongside SecureUxTheme and WindHawk tools; searches DeviantArt by Windows version tag (e.g., `25H2`)

### Removed
- `core/config.py` module (INI-based config)
- Unused `import winreg` and `import json` from `modules/personalize.py`

---

## [0.1.0] — 2026-05-28

### Added
- **Project scaffold**: directory structure with `core/`, `ui/`, `modules/`, `locales/`, `scripts/`, `tests/`, `backups/`, `logs/`
- **Internationalization (i18n)**: full PL/EN support with system language auto-detection; JSON-based locale files with ~415 keys each
- **Registry API**: `core/registry.py` with automatic backup snapshots per module, thread-safe backup rotation, HKCR support
- **System helpers**: `core/system.py` — PowerShell with `pwsh`→`powershell` fallback, visible console launcher, notifications, OS info
- **Download manager**: `core/download.py` — `DownloadThread` with socket-level cancellation and configurable chunk size
- **Dynamic theming**: `ui/themes.py` — dark/light QSS stylesheets driven by Windows accent color and `AppsUseLightTheme` registry key
- **Sidebar UI**: `ui/widgets.py` — `Sidebar` with 4 sections (SYSTEM, NETWORK, PRIVACY, CUSTOMIZE), collapsible groups, active state tracking; `ContentPage` with `add_section`, `add_widget`, `add_button_row_section` helpers
- **Main window**: `ui/main_window.py` — `MainWindow` with 63 page IDs, 18 module dispatch, breadcrumb navigation, ANSI-colored logging with automatic `session.log` export, progress bar, status bar
- **Settings dialog**: `ui/settings_dialog.py` — accent color picker, theme mode (auto/dark/light), language selector with live preview
- **18 feature modules**:
  - Dashboard, Backup & Restore, Profiles, WSL, Installers (28 items via winget/URL), Tweaks, Cleaner, Privacy, Context Menu, System Tools, Network & DNS, Performance, Personalize, File Explorer, UWP/AppX, Scheduled Tasks, Windows Update, Environment Variables
- **Profile system**: 4 pre-configured profiles (Gaming, Privacy Max, Fresh Install, Office) with one-click Apply
- **Backup/restore GUI**: list, inspect, and restore registry snapshots
- **Startup checks**: optional URL verification and profile validation on launch
- **Admin elevation**: auto-restart with `runas` via `ShellExecuteW`
- **29 unit tests**: 15 registry + 14 system tests, all passing
- **Scripts**: `install.bat` (UV-based venv + dependency setup), `start.bat` (launch), `scripts/verify_urls.py`
