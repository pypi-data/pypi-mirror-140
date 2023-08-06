import sys

if sys.platform.startswith("win32"):
    from winreg import CloseKey, OpenKey, SetValueEx, HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_SZ

from ..model.browser.base.driver import BrowserDriver
from ..model.browser.base.type import BrowserType


def set_image_loading(browser_driver: BrowserDriver, load_images: bool = True):
    if browser_driver.settings.type is BrowserType.INTERNET_EXPLORER and sys.platform.startswith("win32"):
        value = "yes" if load_images else "no"
        key = OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Internet Explorer\Main", 0, KEY_ALL_ACCESS)
        SetValueEx(key, "Display Inline Images", 0, REG_SZ, value)
        CloseKey(key)


def disable_images(browser_driver: BrowserDriver) -> None:
    set_image_loading(browser_driver, load_images=False)


def enable_images(browser_driver: BrowserDriver) -> None:
    set_image_loading(browser_driver, load_images=True)
