<div align="center">
  <h1>🛠️ AnonBOT Toolbox</h1>
  <p><strong>Narzędzie do optymalizacji i personalizacji Windows — zbudowane w Python & PyQt6</strong></p>
  <p>
    <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/pyqt-6.5%2B-green?style=flat-square" alt="PyQt6">
    <img src="https://img.shields.io/badge/windows-10%2F11-0078D4?style=flat-square&logo=windows" alt="Windows">
    <img src="https://img.shields.io/badge/license-MIT-yellow?style=flat-square" alt="License">
  </p>
  <p>
    <a href="README.md">🇬🇧 English</a>
  </p>
</div>

---

**AnonBOT Toolbox** to aplikacja desktopowa do konfiguracji, czyszczenia i personalizacji Windows 10 i 11. Łączy narzędzia systemowe, tweaki rejestru, kontrolę prywatności, instalatory oprogramowania i personalizację wizualną w jednym spójnym interfejsie — w pełni po polsku i angielsku.

![Podgląd pulpitu](https://via.placeholder.com/800x450/1e1e2e/7c3aed?text=AnonBOT+Toolbox+—+Zrzut+ekranu)

## ✨ Funkcje

### 🔧 System
- **Tweaks** — wyłącz Copilot, Widgety, Czat, OneDrive; skonfiguruj Centrum akcji, hibernację, plik stronicowania, pasek zadań, dostarczanie Windows Update, WinRE, .NET
- **Czyszczenie** — wyczyść dzienniki zdarzeń, cache Windows Update, cache Sklepu Microsoft, kompaktuj OS
- **Wydajność** — efekty wizualne, planowanie CPU, plany zasilania, programy startowe, optymalizacja dysku
- **Narzędzia systemowe** — test dysku, zarządzanie użytkownikami, tryb gry, ustawienia audio, schematy panelu sterowania Explorera
- **Zaplanowane zadania** — przeglądaj, wyłączaj i włączaj zadania systemowe Windows
- **Windows Update** — sprawdź i wyświetl oczekujące aktualizacje
- **Zmienne środowiskowe** — zarządzaj zmiennymi systemowymi i użytkownika

### 🌐 Sieć
- **DNS** — przełączaj między popularnymi dostawcami DNS (Google, Cloudflare, OpenDNS itd.)
- **Narzędzia** — wyczyść DNS, odśwież IP, zresetuj Winsock
- **Hosts** — dodawaj/usuwaj wpisy hosts z walidacją IP
- **IPv6** — włącz lub wyłącz IPv6

### 🛡 Prywatność
- **Telemetria** — wyłącz telemetrię i zbieranie danych
- **Cortana** — wyłącz Cortanę i wyszukiwanie w sieci
- **Reklamy** — wyłącz spersonalizowane reklamy i sugestie
- **Lokalizacja, Kamera, Mikrofon** — szczegółowe przełączniki prywatności
- **Diagnostyka** — ustaw dane diagnostyczne na minimum

### 🎨 Personalizacja
- **Menu kontekstowe** — dodaj "Otwórz tutaj" (cmd/powershell), utwórz skróty, przywróć menu kontekstowe Windows 11
- **UWP / AppX** — usuń Xbox, nadmiarowe aplikacje Microsoft, historię schowka, Miracast
- **Personalizacja** — schematy kolorów DWM (8 presetów), narzędzia motywów (SecureUxTheme, WindHawk), wyszukiwarka motywów/tapet na DeviantArt
- **Eksplorator plików** — pokaż ukryte pliki, rozszerzenia, ustawienia uruchamiania, widok
- **Instalatory** — 28 programów w 8 kategoriach: przeglądarki, multimedia, sterowniki, Microsoft, narzędzia, deweloperskie, gaming, bezpieczeństwo — instalacja przez winget z fallbackiem URL

### 💾 Konserwacja
- **Kopia zapasowa i przywracanie** — automatyczna migawka rejestru przed każdą modyfikacją; przeglądaj, inspekcjonuj i przywracaj migawki z GUI
- **Profile** — zastosuj predefiniowane konfiguracje jednym kliknięciem (Gaming, Privacy Max, Fresh Install, Office)
- **Dziennik sesji** — każda akcja jest logowana z kolorami ANSI; eksportowalny do `.txt`

## 🖥️ Zrzuty ekranu

| Sidebar | Ustawienia | Motywy |
|---------|-----------|--------|
| *(zrzut)* | *(zrzut)* | *(zrzut)* |

## 📋 Wymagania

- **Windows 10** (21H2+) lub **Windows 11**
- **Python 3.10+** (lub użyj instalatora UV, który go wymaga)
- **Uprawnienia administratora** (wymagane do zmian w rejestrze i systemie)
- **UV** (zalecane) — [Zainstaluj UV](https://docs.astral.sh/uv/#installation)
- **winget** (opcjonalny, ale zalecany dla modułu instalatorów)

## 🚀 Instalacja

### Szybki start (zalecany)

```batch
cd AnonBOT-ToolBox
install.bat
start.bat
```

`install.bat`:
1. Sprawdza dostępność UV
2. Tworzy wirtualne środowisko (`.venv`)
3. Instaluje PyQt6 z `requirements.txt`

### Ręczna instalacja
```batch
cd AnonBOT-ToolBox
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uv run main.py
```

> **Uwaga**: Aplikacja automatycznie restartuje się z uprawnieniami administratora, jeśli została uruchomiona bez nich.

## ⚙️ Konfiguracja

Ustawienia użytkownika są przechowywane w `config.json`:

```json
{
  "language": "pl",
  "accent_color": "#7c3aed",
  "theme_mode": "auto",
  "startup_checks": true
}
```

- `language` — `"en"`, `"pl"` lub `"auto"` (język systemu)
- `accent_color` — dowolny kolor hex (wybierany w Ustawieniach)
- `theme_mode` — `"auto"`, `"dark"` lub `"light"`
- `startup_checks` — weryfikuj URL-e i waliduj profile przy starcie

## 🌐 Internacjonalizacja

Aplikacja w pełni wspiera **język polski** i **angielski**:
- Automatyczne wykrywanie języka systemu
- Ręczna zmiana w Ustawieniach → Język
- ~214 przetłumaczonych kluczy na język
- Sidebar i strony przeładowują się po zmianie języka

## 🏗 Struktura projektu

```
AnonBOT-ToolBox/
├── core/              # API (rejestr, system, pobieranie)
├── ui/                # Komponenty UI (okno główne, sidebar, motywy, ustawienia)
├── modules/           # Moduły funkcyjne (18 modułów)
├── locales/           # Pliki tłumaczeń (en.json, pl.json)
├── scripts/           # Narzędzia pomocnicze
├── tests/             # Testy jednostkowe (29 testów)
├── backups/           # Migawki rejestru
├── logs/              # Logi sesji
├── config.json        # Konfiguracja użytkownika
├── urls.json          # URL-e instalatorów
├── main.py            # Punkt wejścia
├── install.bat        # Skrypt instalacji UV
└── start.bat          # Skrypt uruchomienia
```

## 🧪 Uruchamianie testów

```batch
uv run python -m unittest tests.test_registry tests.test_system -v
```

## 📄 Licencja

Projekt do użytku osobistego. Wszystkie znaki towarowe i nazwy produktów należą do ich właścicieli.

---


