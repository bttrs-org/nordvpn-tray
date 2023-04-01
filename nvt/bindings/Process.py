from typing import Callable, Optional, TypeVar, Generic
from PySide6.QtCore import QProcess

T = TypeVar('T')


class Process(QProcess, Generic[T]):
    on_finish: Optional[Callable[[T], None]]
    on_error: Optional[Callable[[str], None]]

    def __init__(self, on_finish: Optional[Callable[[T], None]] = None,
                 on_error: Optional[Callable[[str], None]] = None):
        super().__init__()
        self.on_finish = on_finish
        self.on_error = on_error
        self.finished.connect(self._process_finished)

    def close(self) -> None:
        self.on_finish = None
        self.on_error = None
        super().close()

    def _start_process(self, params: list[str]):
        super().start('nordvpn', params)
        return self

    def _process_finished(self, code):
        stdout = bytes(self.readAllStandardOutput()).decode("utf8")
        stderr = bytes(self.readAllStandardError()).decode("utf8")
        if code == 0:
            if self.on_finish:
                out = self._parse_output(stdout)
                if out is None:
                    self.on_finish()
                else:
                    self.on_finish(out)
        else:
            if self.on_error:
                if stderr:
                    self.on_error(stderr)
                else:
                    self.on_error(stdout)

        self.on_finish = None
        self.on_error = None

    def _parse_output(self, data: str) -> T:
        pass
