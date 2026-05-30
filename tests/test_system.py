import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestSystem(unittest.TestCase):
    def test_is_admin(self):
        from core.system import is_admin
        result = is_admin()
        self.assertIsInstance(result, bool)

    @patch("core.system.platform.version")
    @patch("core.system.platform.win32_edition")
    @patch("core.system.winreg.CloseKey")
    @patch("core.system.winreg.OpenKey")
    @patch("core.system.winreg.QueryValueEx")
    def test_get_os_info(self, mock_query, mock_open, mock_close, mock_edition, mock_version):
        mock_version.return_value = "10.0.22621"
        mock_edition.return_value = "Professional"
        mock_query.side_effect = [("22H2", 1), ("22621", 1), ("2009", 1)]
        from core.system import get_os_info
        info = get_os_info()
        self.assertEqual(info["os"], "Windows 11")
        self.assertEqual(info["display_version"], "22H2")
        self.assertEqual(info["build"], "22621")
        self.assertEqual(info["edition"], "Professional")

    def test_get_env_existing(self):
        from core.system import get_env
        result = get_env("SystemRoot")
        self.assertTrue(len(result) > 0)

    def test_get_env_missing(self):
        from core.system import get_env
        result = get_env("GHOST_TOOLBOX_NONEXISTENT_VAR", "fallback")
        self.assertEqual(result, "fallback")

    @patch("core.system.subprocess.run")
    def test_run_cmd(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "hello"
        mock_proc.stderr = ""
        mock_run.return_value = mock_proc
        from core.system import run_cmd
        code, out, err = run_cmd(["echo", "hello"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "hello")

    @patch("core.system.subprocess.run")
    def test_run_cmd_exception(self, mock_run):
        mock_run.side_effect = Exception("fail")
        from core.system import run_cmd
        code, out, err = run_cmd(["bad_command"])
        self.assertEqual(code, -1)
        self.assertEqual(out, "")

    @patch("core.system.shutil.which")
    @patch("core.system.run_cmd")
    def test_run_powershell_pwsh(self, mock_run_cmd, mock_which):
        mock_which.return_value = "pwsh.exe"
        mock_run_cmd.return_value = (0, "ok", "")
        from core.system import run_powershell
        code, out, err = run_powershell("Get-Date")
        self.assertEqual(code, 0)
        mock_run_cmd.assert_called_once()
        args = mock_run_cmd.call_args[0][0]
        self.assertIn("pwsh.exe", args)

    @patch("core.system.shutil.which")
    @patch("core.system.run_cmd")
    def test_run_powershell_fallback(self, mock_run_cmd, mock_which):
        mock_which.return_value = None
        mock_run_cmd.return_value = (0, "ok", "")
        from core.system import run_powershell
        code, out, err = run_powershell("Get-Date")
        self.assertEqual(code, 0)
        args = mock_run_cmd.call_args[0][0]
        self.assertIn("powershell.exe", args)

    def test_get_system_drive(self):
        from core.system import get_system_drive
        drive = get_system_drive()
        self.assertTrue(drive.endswith(":"))

    def test_is_dotnet_available_false(self):
        from core.system import is_dotnet_available
        result = is_dotnet_available("v99.99.99")
        self.assertFalse(result)

    @patch("core.system.subprocess.Popen")
    def test_run_visible(self, mock_popen):
        from core.system import run_visible
        mock_popen.return_value = MagicMock()
        result = run_visible(["echo", "test"], "Test")
        self.assertIsNotNone(result)

    @patch("core.system.run_powershell")
    def test_notify(self, mock_run):
        from core.system import notify
        notify("Title", "Message with 'quote'")
        mock_run.assert_called_once()
        script = mock_run.call_args[0][0]
        self.assertIn("''", script)
        self.assertIn("Title", script)
        self.assertIn("Message with ''quote''", script)

    @patch("core.system.run_cmd")
    def test_set_service_startup_auto(self, mock_run_cmd):
        mock_run_cmd.return_value = (0, "", "")
        from core.system import set_service_startup
        result = set_service_startup("Spooler", "Auto")
        self.assertTrue(result)

    def test_set_service_startup_invalid(self):
        from core.system import set_service_startup
        result = set_service_startup("Spooler", "InvalidType")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
