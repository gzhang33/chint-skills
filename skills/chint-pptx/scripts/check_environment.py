#!/usr/bin/env python3
"""Check the runtime and CHINT fonts; optionally open the native font installer."""
from __future__ import annotations

import importlib.util
import ctypes
import ntpath
import os
import platform
import subprocess
import sys
from pathlib import Path


MODULES = {
    "python-pptx": "pptx",
    "PyYAML": "yaml",
    "lxml": "lxml",
    "defusedxml": "defusedxml",
    "Pillow": "PIL",
    "numpy": "numpy",
    "fonttools": "fontTools",
    "PyMuPDF": "fitz",
}
FONT_FILES = ("CHINTinno-Regular.ttf", "CHINTinno-Bold.ttf", "CHINTinno-Light.ttf")
FONT_POSTSCRIPT_NAMES = {
    "CHINTinno-Regular.ttf": "CHINTinno",
    "CHINTinno-Bold.ttf": "CHINTinnoBold",
    "CHINTinno-Light.ttf": "CHINTinnoLight",
}


def _macos_postscript_names() -> set[str]:
    core = ctypes.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
    text = ctypes.CDLL("/System/Library/Frameworks/ApplicationServices.framework/Frameworks/CoreText.framework/CoreText")
    text.CTFontManagerCopyAvailablePostScriptNames.restype = ctypes.c_void_p
    fonts = text.CTFontManagerCopyAvailablePostScriptNames()
    if not fonts:
        return set()
    core.CFArrayGetCount.argtypes = [ctypes.c_void_p]
    core.CFArrayGetCount.restype = ctypes.c_long
    core.CFArrayGetValueAtIndex.argtypes = [ctypes.c_void_p, ctypes.c_long]
    core.CFArrayGetValueAtIndex.restype = ctypes.c_void_p
    core.CFStringGetLength.argtypes = [ctypes.c_void_p]
    core.CFStringGetLength.restype = ctypes.c_long
    core.CFStringGetMaximumSizeForEncoding.argtypes = [ctypes.c_long, ctypes.c_uint32]
    core.CFStringGetMaximumSizeForEncoding.restype = ctypes.c_long
    core.CFStringGetCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_long, ctypes.c_uint32]
    core.CFStringGetCString.restype = ctypes.c_bool
    names = set()
    encoding = 0x08000100  # kCFStringEncodingUTF8
    try:
        for index in range(core.CFArrayGetCount(fonts)):
            item = core.CFArrayGetValueAtIndex(fonts, index)
            size = core.CFStringGetMaximumSizeForEncoding(core.CFStringGetLength(item), encoding) + 1
            buffer = ctypes.create_string_buffer(size)
            if core.CFStringGetCString(item, buffer, size, encoding):
                names.add(buffer.value.decode("utf-8"))
    finally:
        core.CFRelease.argtypes = [ctypes.c_void_p]
        core.CFRelease.restype = None
        core.CFRelease(fonts)
    return names


def _windows_registered_files() -> set[str]:
    import winreg

    registered = set()
    key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
    for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        try:
            with winreg.OpenKey(hive, key_path) as key:
                for index in range(winreg.QueryInfoKey(key)[1]):
                    _name, value, _kind = winreg.EnumValue(key, index)
                    registered.add(ntpath.basename(os.path.expandvars(str(value))).casefold())
        except OSError:
            continue
    return registered


def _linux_font_files(home: Path | None = None) -> set[str]:
    home = home or Path.home()
    roots = (home / ".local" / "share" / "fonts", home / ".fonts",
             Path("/usr/local/share/fonts"), Path("/usr/share/fonts"))
    return {path.name.casefold() for root in roots if root.exists() for path in root.rglob("*.ttf")}


def registered_font_files(system: str | None = None) -> set[str]:
    system = system or platform.system()
    if system == "Darwin":
        try:
            names = _macos_postscript_names()
        except OSError:
            return set()
        return {filename.casefold() for filename, postscript in FONT_POSTSCRIPT_NAMES.items()
                if postscript in names}
    if system == "Windows":
        registered = _windows_registered_files()
        return {filename.casefold() for filename in FONT_FILES if filename.casefold() in registered}
    return _linux_font_files()


def missing_installed_fonts(installed_files: set[str] | None = None) -> list[str]:
    installed = registered_font_files() if installed_files is None else {name.casefold() for name in installed_files}
    return [name for name in FONT_FILES if name.casefold() not in installed]


def open_font_installer(font_dir: Path | None = None, font_names: list[str] | None = None,
                        system: str | None = None) -> None:
    system = system or platform.system()
    font_dir = font_dir or Path(__file__).resolve().parents[1] / "assets" / "fonts"
    fonts = [font_dir / name for name in (FONT_FILES if font_names is None else font_names)]
    missing = [font.name for font in fonts if not font.is_file()]
    if missing:
        raise FileNotFoundError("Missing bundled font files: " + ", ".join(missing))
    if system == "Darwin":
        subprocess.run(["open", "-a", "Font Book", *map(str, fonts)], check=True)
    elif system == "Windows":
        for font in fonts:
            os.startfile(str(font))  # type: ignore[attr-defined]
    else:
        raise OSError("Native font installation is supported on macOS and Windows only.")


def print_font_install_help(missing_fonts: list[str], system: str | None = None) -> None:
    system = system or platform.system()
    print("[FAIL] CHINT fonts are not installed in the operating system: " + ", ".join(missing_fonts))
    print("Install the three bundled fonts from assets/fonts for your user account.")
    if system == "Darwin":
        print("macOS: Open each .ttf file in Font Book and add it to the current user.")
    elif system == "Windows":
        print("Windows: Select the .ttf files, right-click, then choose Install.")
    else:
        print("Install each .ttf file in your operating system's user font folder.")
    print("After user approval, open the native installer with: python3 scripts/check_environment.py --open-font-installer")
    print("Restart PowerPoint or WPS, then run this environment check again.")


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Check CHINT PPTX runtime and required installed fonts.")
    parser.add_argument("--open-font-installer", action="store_true",
                        help="Open the operating system's user-level font installation interface")
    args = parser.parse_args(argv)
    print(f"Python: {sys.executable} ({sys.version.split()[0]})")
    font_dir = Path(__file__).resolve().parents[1] / "assets" / "fonts"
    missing_fonts = [name for name in FONT_FILES if not (font_dir / name).is_file()]
    missing_installed = missing_installed_fonts()
    if args.open_font_installer:
        if not missing_installed:
            print("[PASS] All CHINT fonts are already registered; no installer opened.")
            return 0
        try:
            open_font_installer(font_dir, missing_installed)
        except (FileNotFoundError, OSError, subprocess.CalledProcessError) as exc:
            print(f"[FAIL] Could not open the native font installer: {exc}")
            return 1
        print("[INFO] Complete installation in the native font window, restart Office, then rerun this check.")
        return 0

    missing = [package for package, module in MODULES.items()
               if importlib.util.find_spec(module) is None]
    failed = False
    if sys.version_info < (3, 11):
        print("[FAIL] chint-pptx requires Python 3.11 or newer.")
        failed = True
    if missing:
        print("[FAIL] Missing packages: " + ", ".join(missing))
        print("Install requirements.txt into this Python environment and run this check again.")
        failed = True
    if missing_fonts:
        print("[FAIL] Missing CHINT font assets: " + ", ".join(missing_fonts))
        failed = True
    if missing_installed:
        print_font_install_help(missing_installed)
        print("After user confirmation, open the native installer with: python3 scripts/check_environment.py --open-font-installer")
        failed = True
    if failed:
        return 1
    print("[PASS] Python version, required packages, bundled assets, and installed CHINT fonts are available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
