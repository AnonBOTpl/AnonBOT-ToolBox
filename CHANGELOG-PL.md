# Historia zmian

## [0.2.0] — 2026-05-30

### Naprawiono
- **Generowanie tagu DeviantArt**: zastąpiono uszkodzony `CurrentBuild` wartością `DisplayVersion` z rejestru dla dokładnego wykrywania wersji Windows w wyszukiwaniu motywów
- **Etykieta sidebaru**: poprawiono `personalize.theme_title` → `personalize.themes` — klucz brakował w plikach locale, przez co w sidebarze wyświetlała się surowa nazwa klucza
- **Breadcrumb**: dodano brakujący klucz `sidebar.system_tools` — strony narzędzi systemowych pokazywały surowy klucz w breadcrumbie
- **Konflikt configu**: usunięto `core/config.py` i `config.ini`; wszystkie ustawienia użytkownika są teraz spójnie odczytywane/zapisywane wyłącznie w `config.json`

### Dodano
- **Sekcja tapet**: nowy przycisk "Szukaj tapet na DeviantArt" otwierający `deviantart.com/tag/wallpapers`
- **Odświeżanie UI przy zmianie języka**: `Sidebar.rebuild()` i `_refresh_language()` przeładowują etykiety sidebaru i bieżącą stronę po zmianie języka w Ustawieniach
- **Brakujące klucze i18n**: dodano `personalize.search_themes`, `personalize.search_wallpapers` i `sidebar.system_tools` do obu plików locale (EN i PL)
- **Audyt i18n**: kompleksowa weryfikacja wszystkich ~214 kluczy × 2 locale — nie ma brakujących kluczy

### Zmieniono
- **Sekcja motywów**: przywrócono przycisk "Szukaj motywów na DeviantArt" obok SecureUxTheme i WindHawk; wyszukuje na DeviantArt według tagu wersji Windows (np. `25H2`)

### Usunięto
- Moduł `core/config.py` (konfiguracja INI)
- Nieużywane `import winreg` i `import json` z `modules/personalize.py`

---

## [0.1.0] — 2026-05-28

### Dodano
- **Szkielet projektu**: struktura katalogów `core/`, `ui/`, `modules/`, `locales/`, `scripts/`, `tests/`, `backups/`, `logs/`
- **Internacjonalizacja (i18n)**: pełne wsparcie PL/EN z auto-detekcją języka systemu; pliki locale JSON z ~415 kluczami każdy
- **API rejestru**: `core/registry.py` z automatycznymi migawkami kopii zapasowych na moduł, bezpieczną rotacją wątków, obsługą HKCR
- **Pomocnicy systemowi**: `core/system.py` — PowerShell z fallbackiem `pwsh`→`powershell`, uruchamianie widocznej konsoli, powiadomienia, informacje o OS
- **Menedżer pobierania**: `core/download.py` — `DownloadThread` z anulowaniem na poziomie socketu i konfigurowalnym rozmiarem bloku
- **Dynamiczne motywy**: `ui/themes.py` — ciemne/jasne arkusze QSS sterowane kolorem akcentu Windows i kluczem rejestru `AppsUseLightTheme`
- **Sidebar UI**: `ui/widgets.py` — `Sidebar` z 4 sekcjami (SYSTEM, NETWORK, PRIVACY, CUSTOMIZE), grupami zwijanymi, śledzeniem stanu aktywnego; `ContentPage` z helperami `add_section`, `add_widget`, `add_button_row_section`
- **Okno główne**: `ui/main_window.py` — `MainWindow` z 63 ID stron, dyspozytornią 18 modułów, nawigacją breadcrumb, logowaniem ANSI z automatycznym eksportem `session.log`, paskiem postępu, paskiem statusu
- **Okno ustawień**: `ui/settings_dialog.py` — wybór koloru akcentu, tryb motywu (auto/ciemny/jasny), wybór języka z podglądem na żywo
- **18 modułów funkcyjnych**:
  - Dashboard, Backup i Przywracanie, Profile, WSL, Instalatory (28 pozycji przez winget/URL), Tweaks, Czyszczenie, Prywatność, Menu kontekstowe, Narzędzia systemowe, Sieć i DNS, Wydajność, Personalizacja, Eksplorator plików, UWP/AppX, Zaplanowane zadania, Windows Update, Zmienne środowiskowe
- **System profili**: 4 predefiniowane profile (Gaming, Privacy Max, Fresh Install, Office) z jednym kliknięciem Apply
- **GUI kopii zapasowych**: przeglądanie, inspekcja i przywracanie migawek rejestru
- **Sprawdzanie przy starcie**: opcjonalna weryfikacja URL-i i walidacja profili przy uruchomieniu
- **Podniesienie uprawnień**: auto-restart z `runas` przez `ShellExecuteW`
- **29 testów jednostkowych**: 15 registry + 14 system, wszystkie przechodzą
- **Skrypty**: `install.bat` (venv + zależności przez UV), `start.bat` (uruchomienie), `scripts/verify_urls.py`
