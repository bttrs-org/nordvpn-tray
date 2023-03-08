from typing import Callable, Optional, List, TypeVar, Generic
from PySide6.QtCore import QProcess

T = TypeVar('T')


class Process(QProcess, Generic[T]):
    on_finish: Optional[Callable[[T], None]] = None
    on_error: Optional[Callable[[str], None]] = None

    def __init__(self, on_finish: Optional[Callable[[T], None]] = None,
                 on_error: Optional[Callable[[str], None]] = None):
        super().__init__()
        self.on_finish = on_finish
        self.on_error = on_error
        self.finished.connect(self.process_finished)

    def close(self) -> None:
        self.on_finish = None
        self.on_error = None
        super().close()

    def start_process(self, params: List[str]):
        super().start('nordvpn', params)
        return self

    def process_finished(self, code):
        if code == 0:
            if self.on_finish:
                stdout = bytes(self.readAllStandardOutput()).decode("utf8")
                out = self.parse_output(stdout)
                if out is None:
                    self.on_finish()
                else:
                    self.on_finish(out)
        else:
            if self.on_error:
                stderr = bytes(self.readAllStandardError()).decode("utf8")
                self.on_error(stderr)

        self.on_finish = None
        self.on_error = None

    def parse_output(self, data: str) -> T:
        pass
