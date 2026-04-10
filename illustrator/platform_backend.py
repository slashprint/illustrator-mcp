"""
Platform abstraction layer for Adobe Illustrator automation.

Provides a unified interface for screenshot capture and ExtendScript execution
across Windows (COM/win32) and macOS (AppleScript/osascript).
"""

import abc
import base64
import io
import logging
import os
import subprocess
import sys
import tempfile
import time

from PIL import Image

logger = logging.getLogger(__name__)


class IllustratorBackend(abc.ABC):
    """Abstract base class for platform-specific Illustrator automation."""

    @abc.abstractmethod
    def focus_app(self) -> None:
        """Bring Adobe Illustrator to the foreground."""

    @abc.abstractmethod
    def capture_screenshot(self) -> str:
        """Capture a screenshot of the Illustrator window.

        Returns:
            Base64-encoded JPEG image data.
        """

    @abc.abstractmethod
    def run_script(self, code: str) -> str:
        """Execute ExtendScript code in Illustrator.

        Args:
            code: ExtendScript/JavaScript source code.

        Returns:
            Result text from the script execution.
        """

    # ---- shared helpers ------------------------------------------------

    @staticmethod
    def _image_to_base64_jpeg(img: Image.Image, quality: int = 50) -> str:
        """Compress a PIL Image to JPEG and return base64-encoded data."""
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        return base64.b64encode(buf.getvalue()).decode("utf-8")


# =====================================================================
# Windows backend
# =====================================================================

class WindowsBackend(IllustratorBackend):
    """Illustrator automation via Windows COM (pywin32)."""

    def __init__(self) -> None:
        try:
            import win32com.client  # noqa: F401
            import pythoncom  # noqa: F401
            self._win32com = win32com
            logger.info("WindowsBackend initialised – win32com loaded.")
        except ImportError as exc:
            raise RuntimeError(
                "pywin32 is required on Windows. Install it with: pip install pywin32"
            ) from exc

    def focus_app(self) -> None:
        shell = self._win32com.client.Dispatch("WScript.Shell")
        shell.AppActivate("Adobe Illustrator")

    def capture_screenshot(self) -> str:
        from PIL import ImageGrab

        self.focus_app()
        time.sleep(1)
        screenshot = ImageGrab.grab()
        logger.info("Screenshot captured (Windows/ImageGrab).")
        return self._image_to_base64_jpeg(screenshot)

    def run_script(self, code: str) -> str:
        with tempfile.NamedTemporaryFile(suffix=".jsx", delete=False, mode="w",
                                         encoding="utf-8") as f:
            f.write(code)
            jsx_path = f.name

        try:
            logger.debug("ExtendScript saved to: %s", jsx_path)
            app = self._win32com.client.Dispatch("Illustrator.Application")
            result = app.DoJavaScriptFile(jsx_path)
            logger.info("ExtendScript executed successfully (Windows/COM).")
            return str(result) if result is not None else "Script executed successfully (no return value)"
        finally:
            os.unlink(jsx_path)
            logger.debug("Temporary .jsx file removed.")


# =====================================================================
# macOS backend
# =====================================================================

class MacBackend(IllustratorBackend):
    """Illustrator automation via AppleScript / osascript on macOS."""

    # AppleScript application name — Adobe Illustrator registers itself this
    # way in the scripting dictionary.  Older versions may use a year suffix
    # (e.g. "Adobe Illustrator 2024") – we try the plain name first.
    _APP_NAME = "Adobe Illustrator"

    def __init__(self) -> None:
        # Quick sanity check — osascript must be present.
        if not os.path.isfile("/usr/bin/osascript"):
            raise RuntimeError("osascript not found – this backend requires macOS.")

        # Verify we can talk to Illustrator (also triggers the macOS
        # Automation permission dialog on first run).
        try:
            self._osascript(f'tell application "{self._APP_NAME}" to get version')
            logger.info("MacBackend initialised – can communicate with Illustrator.")
        except RuntimeError as exc:
            logger.warning(
                "Could not communicate with Adobe Illustrator: %s. "
                "Make sure Illustrator is running and macOS Automation "
                "permissions are granted (System Settings → Privacy & "
                "Security → Automation).",
                exc,
            )
            # Don't raise — the user may start Illustrator later.

    # ---- helpers -------------------------------------------------------

    @staticmethod
    def _osascript(script: str) -> str:
        """Run a one-liner AppleScript and return stdout."""
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise RuntimeError(f"osascript failed ({result.returncode}): {stderr}")
        return result.stdout.strip()

    @staticmethod
    def _osascript_multi(lines: list[str]) -> str:
        """Run a multi-line AppleScript passed as separate -e arguments."""
        cmd: list[str] = ["osascript"]
        for line in lines:
            cmd.extend(["-e", line])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            stderr = result.stderr.strip()
            raise RuntimeError(f"osascript failed ({result.returncode}): {stderr}")
        return result.stdout.strip()

    # ---- interface implementation --------------------------------------

    def focus_app(self) -> None:
        self._osascript(f'tell application "{self._APP_NAME}" to activate')

    def capture_screenshot(self) -> str:
        self.focus_app()
        time.sleep(1)  # give Illustrator time to come to foreground

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            tmp_path = f.name

        try:
            # -x  suppresses the shutter sound
            # -t jpg  output format
            subprocess.run(
                ["screencapture", "-x", "-t", "jpg", tmp_path],
                check=True,
                timeout=10,
            )
            img = Image.open(tmp_path)
            logger.info("Screenshot captured (macOS/screencapture).")
            return self._image_to_base64_jpeg(img)
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def run_script(self, code: str) -> str:
        with tempfile.NamedTemporaryFile(suffix=".jsx", delete=False, mode="w",
                                         encoding="utf-8") as f:
            f.write(code)
            jsx_path = f.name

        try:
            logger.debug("ExtendScript saved to: %s", jsx_path)
            # Use AppleScript to tell Illustrator to run the script file.
            applescript = (
                f'tell application "{self._APP_NAME}" to '
                f'do javascript (read POSIX file "{jsx_path}") as string'
            )
            result = self._osascript(applescript)
            logger.info("ExtendScript executed successfully (macOS/osascript).")
            return result if result else "Script executed successfully (no return value)"
        finally:
            os.unlink(jsx_path)
            logger.debug("Temporary .jsx file removed.")


# =====================================================================
# Factory
# =====================================================================

def get_backend() -> IllustratorBackend:
    """Return the appropriate backend for the current platform."""
    if sys.platform == "darwin":
        return MacBackend()
    elif sys.platform == "win32":
        return WindowsBackend()
    else:
        raise RuntimeError(
            f"Unsupported platform: {sys.platform}. "
            "This project supports Windows and macOS."
        )

