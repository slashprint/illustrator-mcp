"""Tests for the platform backend abstraction layer."""

import os
import sys
import tempfile
import unittest
from unittest import mock

from illustrator.platform_backend import (
    IllustratorBackend,
    MacBackend,
    WindowsBackend,
    get_backend,
)


class TestGetBackend(unittest.TestCase):
    """Test the factory function returns the right backend per platform."""

    @mock.patch("illustrator.platform_backend.sys")
    @mock.patch.object(MacBackend, "__init__", return_value=None)
    def test_returns_mac_backend_on_darwin(self, mock_init, mock_sys):
        mock_sys.platform = "darwin"
        backend = get_backend()
        self.assertIsInstance(backend, MacBackend)

    @mock.patch("illustrator.platform_backend.sys")
    @mock.patch.object(WindowsBackend, "__init__", return_value=None)
    def test_returns_windows_backend_on_win32(self, mock_init, mock_sys):
        mock_sys.platform = "win32"
        backend = get_backend()
        self.assertIsInstance(backend, WindowsBackend)

    @mock.patch("illustrator.platform_backend.sys")
    def test_raises_on_unsupported_platform(self, mock_sys):
        mock_sys.platform = "freebsd"
        with self.assertRaises(RuntimeError):
            get_backend()


class TestMacBackendRunScript(unittest.TestCase):
    """Test MacBackend.run_script with mocked osascript."""

    def _make_backend(self):
        """Create a MacBackend without running the __init__ sanity check."""
        backend = MacBackend.__new__(MacBackend)
        backend._APP_NAME = "Adobe Illustrator"
        return backend

    @mock.patch("illustrator.platform_backend.subprocess.run")
    def test_run_script_success(self, mock_run):
        mock_run.return_value = mock.Mock(
            returncode=0, stdout="42\n", stderr=""
        )
        backend = self._make_backend()
        result = backend.run_script('alert("hello");')
        self.assertEqual(result, "42")

        # Verify osascript was called with the right arguments
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        self.assertEqual(cmd[0], "osascript")
        self.assertEqual(cmd[1], "-e")
        self.assertIn("do javascript", cmd[2])

    @mock.patch("illustrator.platform_backend.subprocess.run")
    def test_run_script_no_return_value(self, mock_run):
        mock_run.return_value = mock.Mock(
            returncode=0, stdout="", stderr=""
        )
        backend = self._make_backend()
        result = backend.run_script("app.documents.add();")
        self.assertEqual(result, "Script executed successfully (no return value)")

    @mock.patch("illustrator.platform_backend.subprocess.run")
    def test_run_script_osascript_error(self, mock_run):
        mock_run.return_value = mock.Mock(
            returncode=1, stdout="", stderr="execution error: Application not running"
        )
        backend = self._make_backend()
        with self.assertRaises(RuntimeError) as ctx:
            backend.run_script("bad code")
        self.assertIn("osascript failed", str(ctx.exception))


class TestMacBackendScreenshot(unittest.TestCase):
    """Test MacBackend.capture_screenshot with mocked screencapture."""

    def _make_backend(self):
        backend = MacBackend.__new__(MacBackend)
        backend._APP_NAME = "Adobe Illustrator"
        return backend

    @mock.patch("illustrator.platform_backend.os.path.exists", return_value=True)
    @mock.patch("illustrator.platform_backend.os.unlink")
    @mock.patch("illustrator.platform_backend.Image.open")
    @mock.patch("illustrator.platform_backend.subprocess.run")
    @mock.patch("illustrator.platform_backend.time.sleep")
    def test_capture_screenshot_returns_base64(
        self, mock_sleep, mock_run, mock_open, mock_unlink, mock_exists
    ):
        # Mock subprocess calls (focus_app + screencapture)
        mock_run.return_value = mock.Mock(returncode=0, stdout="", stderr="")

        # Mock Image.open to return a small test image
        from PIL import Image
        test_img = Image.new("RGB", (100, 100), color="red")
        mock_open.return_value = test_img

        backend = self._make_backend()
        result = backend.capture_screenshot()

        # Should be a non-empty base64 string
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

        # Should be valid base64
        import base64
        decoded = base64.b64decode(result)
        self.assertGreater(len(decoded), 0)


class TestWindowsBackendRunScript(unittest.TestCase):
    """Test WindowsBackend.run_script with mocked COM."""

    def _make_backend(self):
        backend = WindowsBackend.__new__(WindowsBackend)
        backend._win32com = mock.MagicMock()
        return backend

    def test_run_script_success(self):
        backend = self._make_backend()
        mock_app = mock.MagicMock()
        mock_app.DoJavaScriptFile.return_value = "result_value"
        backend._win32com.client.Dispatch.return_value = mock_app

        result = backend.run_script('alert("test");')
        self.assertEqual(result, "result_value")

    def test_run_script_no_return(self):
        backend = self._make_backend()
        mock_app = mock.MagicMock()
        mock_app.DoJavaScriptFile.return_value = None
        backend._win32com.client.Dispatch.return_value = mock_app

        result = backend.run_script("app.documents.add();")
        self.assertEqual(result, "Script executed successfully (no return value)")


class TestImageToBase64(unittest.TestCase):
    """Test the shared _image_to_base64_jpeg helper."""

    def test_returns_valid_base64_jpeg(self):
        import base64
        from PIL import Image

        img = Image.new("RGB", (50, 50), color="blue")
        result = IllustratorBackend._image_to_base64_jpeg(img)

        decoded = base64.b64decode(result)
        # JPEG files start with FF D8
        self.assertEqual(decoded[:2], b"\xff\xd8")


if __name__ == "__main__":
    unittest.main()

