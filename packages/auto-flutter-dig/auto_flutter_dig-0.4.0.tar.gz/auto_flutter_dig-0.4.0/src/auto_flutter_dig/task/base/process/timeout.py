from .interval import *

__all__ = [
    "Task",
    "List",
    "TaskIdentity",
    "TaskResult",
    "TaskId",
    "Args",
    "Process",
    "BaseProcessTimeoutTask",
    "ProcessOrResult",
]


class BaseProcessTimeoutTask(BaseProcessIntervalTask):
    def __init__(
        self,
        ignore_failure: bool = False,
        show_output_at_end: bool = False,
        interval: float = 5,
        timeout: float = 30,
    ) -> None:
        super().__init__(ignore_failure, show_output_at_end, interval)
        self._timeout = timeout
        if timeout < interval:
            self._interval = timeout
        self._stopped = False
        self._killed = False

    def _on_interval(self, process: Process, time: float, count: int) -> None:
        if time >= self._timeout:
            if self._stopped and not self._killed:
                self._killed = True
                process.kill()
                self._on_process_kill(process, time, count)
            else:
                self._stopped = True
                process.stop()
                self._on_process_stop(process, time, count)

    def _on_process_stop(self, process: Process, time: float, count: int) -> None:
        # process.stop() already called
        pass

    def _on_process_kill(self, process: Process, time: float, count: int) -> None:
        # process.kill() already called
        pass
