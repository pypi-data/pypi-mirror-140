from typing import List, Optional

from typing_extensions import Literal, TypedDict

from selenium.common.exceptions import (  # type: ignore
    JavascriptException,
    TimeoutException,
)
from inspector.windows.base import Window, traceback
from inspector.windows.browser import BrowserBridge


class AppendMessage(TypedDict):
    value: str
    type: str
    trigger: Literal["click", "change", "unknown"]


class RecordEvent(TypedDict):
    list: List[AppendMessage]
    actionType: Literal["exception", "stop", "append"]
    url: Optional[str]


class TabInfo(TypedDict):
    title: str
    url: str


class RecorderBridge(BrowserBridge):
    """Javascript API bridge for recorder functionality."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_url: Optional[str] = None
        self._messages: List[AppendMessage] = []

    @traceback
    def start_recording(self) -> List[AppendMessage]:
        # TODO: Handle as async in future instead of blocking
        self._record()
        self.logger.debug("Recorded events: %s", self._messages)
        return self._messages

    def _record(self):
        self._messages = []
        while True:
            # TODO: Could we try catch the page change?
            try:
                event: RecordEvent = self.driver.record_event()
            except JavascriptException as exc:
                self.logger.debug("Ignoring Javascript exception: %s", exc)
                event: RecordEvent = {
                    "actionType": "exception",
                    "list": [],
                    "url": self._current_url,
                }
            except TimeoutException:
                self.logger.debug("Retrying after script timeout")
                event: RecordEvent = {
                    "actionType": "exception",
                    "list": [],
                    "url": self._current_url,
                }

            if not event:
                self.logger.error("Received empty event: %s", event)
                continue

            if not self._handle_event(event):
                return

    def _handle_event(self, event: RecordEvent) -> bool:
        event_type = event["actionType"]
        event_url = event["url"]

        if not self._current_url:
            self._current_url = event_url
        elif event_url != self._current_url:
            message: AppendMessage = {
                "type": "comment",
                "value": f"Recorder detected that URL changed to {event_url}",
                "trigger": "unknown",
            }
            self._current_url = event_url
            self._messages += [message]

        if event_type == "exception":
            return True  # Ignore errors for now
        elif event_type == "event":
            self.logger.debug("Received event(s) from page: %s", event["list"])
            self._messages += event["list"]
            return True
        elif event_type == "stop":
            self.logger.debug("Received stop from page")
            self.driver.stop_recording()
            self._messages += event["list"]
            return False
        else:
            raise ValueError(f"Unknown event type: {event_type}")

    @traceback
    def show_guide(self):
        self.driver.show_guide("recording-guide")


class RecorderWindow(Window):
    BRIDGE = RecorderBridge
    DEFAULTS = {
        "url": "recorder.html",
        "width": 480,
        "height": 720,
        "on_top": True,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._force_closing = False

    def on_closing(self):
        should_close = super().on_closing()
        if not should_close:
            return False

        driver = self._context.webdriver
        if driver is not None and driver.is_running:
            try:
                driver.clear()
            except Exception as exc:  # pylint: disable=broad-except
                self.logger.debug("Failed to clear webdriver: %s", exc)

        return True
