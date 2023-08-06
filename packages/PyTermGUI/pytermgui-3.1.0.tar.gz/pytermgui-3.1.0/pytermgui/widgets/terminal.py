import os
import io
import shlex
from typing import IO

from subprocess import Popen, PIPE

from .base import Widget
from ..ansi_interface import MouseEvent


class TerminalWidget(Widget):
    auto_close: bool = True

    """The streams the given process will use."""
    _stdout: IO[bytes]
    _stdin: IO[bytes]
    _stderr: IO[bytes]

    def __init__(self, **attrs) -> None:
        """Initialize a terminal widget."""

        super().__init__(**attrs)
        self._stream = open("stream", "rb+")
        self._process: Popen | None = None
        self._process_content = []

    def run(self, command: str) -> int:
        """Runs given command, returns its exit value."""

        self._process = Popen(command, stdout=PIPE, shell=True)
        # os.set_blocking(self._process.stdout.fileno(), False)

    def handle_key(self, key: str) -> bool:
        """Sends given key to the process STDOUT stream, returns True always?"""

    def handle_mouse(self, event: MouseEvent) -> bool:
        """Sends given event as ANSI to the process STDIN stream, returns True always?"""

    def get_lines(self) -> list[str]:
        """Updates & displays the current process' content."""

        if self._process is None:
            return []

        # if self._process.poll() is None:
        for line in self._process.stdout:
            self._process_content.append(line.decode("utf-8").strip())

        with open("log", "a") as log:
            log.write("\n\n" + "\n".join(self._process_content))

        return self._process_content
