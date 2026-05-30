import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")

    def test_parse_path_hklm(self):
        from core.registry import _parse_path, ROOT_KEYS
        hkey, subkey = _parse_path("HKLM:SOFTWARE\\Microsoft")
        self.assertEqual(hkey, ROOT_KEYS["HKLM"])
        self.assertEqual(subkey, "SOFTWARE\\Microsoft")

    def test_parse_path_hkcu(self):
        from core.registry import _parse_path, ROOT_KEYS
        hkey, subkey = _parse_path("HKCU:Software\\Test")
        self.assertEqual(hkey, ROOT_KEYS["HKCU"])
        self.assertEqual(subkey, "Software\\Test")

    def test_parse_path_with_slash(self):
        from core.registry import _parse_path, ROOT_KEYS
        hkey, subkey = _parse_path("HKLM:SOFTWARE/Microsoft")
        self.assertEqual(subkey, "SOFTWARE\\Microsoft")

    def test_parse_path_default_root(self):
        from core.registry import _parse_path, ROOT_KEYS
        hkey, subkey = _parse_path("SOFTWARE\\Test")
        self.assertEqual(hkey, ROOT_KEYS["HKLM"])

    def test_parse_path_invalid_root(self):
        from core.registry import _parse_path
        with self.assertRaises(ValueError):
            _parse_path("INVALID:path")

    def test_type_name_for_value_int(self):
        from core.registry import _type_name_for_value
        self.assertEqual(_type_name_for_value(1), "DWord")

    def test_type_name_for_value_str(self):
        from core.registry import _type_name_for_value
        self.assertEqual(_type_name_for_value("hello"), "String")

    def test_type_name_for_value_bytes(self):
        from core.registry import _type_name_for_value
        self.assertEqual(_type_name_for_value(b"\x00\x01"), "Binary")

    def test_type_name_for_value_unknown(self):
        from core.registry import _type_name_for_value
        self.assertEqual(_type_name_for_value(1.5), "String")

    def test_strip_hkcr(self):
        from core.registry import _strip_hkcr
        result = _strip_hkcr("HKCR:.txt")
        self.assertEqual(result, ".txt")

    def test_get_registry_nonexistent(self):
        from core.registry import get_registry
        result = get_registry("HKLM:SOFTWARE\\NonExistentKey\\GhostTest", "NonExistentValue", "default")
        self.assertEqual(result, "default")

    def test_backup_snapshot_entry(self):
        from core.registry import backup_snapshot_entry, _SESSION_BACKUPS
        _SESSION_BACKUPS.clear()
        backup_snapshot_entry("HKLM:SOFTWARE\\Test", "TestValue", 1, "DWord", module_name="test_mod")
        self.assertIn("test_mod", _SESSION_BACKUPS)
        self.assertEqual(len(_SESSION_BACKUPS["test_mod"]), 1)
        self.assertEqual(_SESSION_BACKUPS["test_mod"][0]["value"], 1)

    def test_save_snapshot_no_entries(self):
        from core.registry import save_snapshot, _SESSION_BACKUPS
        _SESSION_BACKUPS.clear()
        result = save_snapshot("nonexistent")
        self.assertIsNone(result)

    def test_get_snapshots_empty_dir(self):
        from core.registry import get_snapshots
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        snapshots = get_snapshots()
        self.assertIsInstance(snapshots, list)

    def test_caller_module(self):
        from core.registry import _caller_module
        mod = _caller_module()
        self.assertIsInstance(mod, str)


if __name__ == "__main__":
    unittest.main()
