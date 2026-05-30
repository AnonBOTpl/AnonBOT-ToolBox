import json
import os
import locale
import ctypes
import threading


class I18n:
    def __init__(self, locales_dir=None):
        if locales_dir is None:
            locales_dir = os.path.join(os.path.dirname(__file__), "locales")
        self.locales_dir = locales_dir
        self._locales = {}
        self.current_lang = self._detect_language()
        self._load()

    def _detect_language(self):
        try:
            windll = ctypes.windll.kernel32
            lang_id = windll.GetUserDefaultUILanguage()
            if lang_id & 0x3FF == 0x15:
                return "pl"
        except Exception:
            pass
        try:
            lang_code = locale.getdefaultlocale()[0]
            if lang_code and lang_code.startswith("pl"):
                return "pl"
        except Exception:
            pass
        return "en"

    def _load(self):
        for lang in ("en", "pl"):
            path = os.path.join(self.locales_dir, f"{lang}.json")
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    self._locales[lang] = json.load(f)
            else:
                self._locales[lang] = {}

    def tr(self, key, **kwargs):
        val = self._locales.get(self.current_lang, {}).get(key)
        if val is None:
            val = self._locales.get("en", {}).get(key)
        if val is None:
            val = key
        if kwargs:
            try:
                val = val.format(**kwargs)
            except KeyError:
                pass
        return val

    def set_language(self, lang):
        if lang in self._locales:
            self.current_lang = lang

    def get_language(self):
        return self.current_lang

    def available_languages(self):
        return list(self._locales.keys())


_i18n = None
_i18n_lock = threading.Lock()


def get_i18n(locales_dir=None):
    global _i18n
    if _i18n is None:
        with _i18n_lock:
            if _i18n is None:
                _i18n = I18n(locales_dir)
    return _i18n


def tr(key, **kwargs):
    return get_i18n().tr(key, **kwargs)
