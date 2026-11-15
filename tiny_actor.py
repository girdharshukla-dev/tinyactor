from concurrent.futures import Future
from pathlib import Path
import sqlite3
import queue
import threading

class TinyActor:
    def __init__(self, actor_id: str, data_dir: str = "data"):
        self.id = actor_id
        folder = Path(data_dir)
        folder.mkdir(parents = True, exist_ok = True)
        self._db = sqlite3.connect(
            folder/f"{actor_id}.sqlite", 
            isolation_level=None, 
            check_same_thread=False)

        self._queue: queue.Queue = queue.Queue()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread is None:
            self._thread = threading.Thread(
                target=self._run, name=f"actor-{self.id}", daemon=True
            )
            self._thread.start()

    def stop(self) -> None:
        if self._thread is not None:
            self._queue.put(None)
            self._thread.join()
            self._thread = None
        self._db.close()

    def submit(self, method: str, *args) -> Future:
        if self._thread is None:
            raise RuntimeError(f"actor is not running, actor id: {self.id}")
        fut: Future = Future()
        self._queue.put((method, args, fut))
        return fut

    def call(self, method, *args):
        return self.submit(method, *args).result()

    def _run(self) -> None:
        while True:
            item = self._queue.get()
            if item is None:
                break
            method, args, fut = item
            if not fut.set_running_or_notify_cancel():
                continue
            try:
                fut.set_result(getattr(self, method)(*args))
            except Exception as e:
                fut.set_exception(e)
        