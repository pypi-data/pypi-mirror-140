from inspector.utils import IS_WINDOWS
from .recorder import RecorderWindow
from .base import WindowState
from .browser import BrowserWindow
from .manager import ManagerWindow
from .image import ImageWindow

WINDOWS = {
    "browser": BrowserWindow,
    "image": ImageWindow,
    "manager": ManagerWindow,
    "recorder": RecorderWindow,
}

if IS_WINDOWS:
    from .windows import WindowsWindow

    WINDOWS["windows"] = WindowsWindow
