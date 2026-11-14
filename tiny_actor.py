from pathlib import Path
import sqlite3


class TinyActor:
    def __init__(self, actor_id: str, data_dir: str = "data"):
        self.id = actor_id
        folder = Path(data_dir)
        folder.mkdir(parents = True, exist_ok = True)
        self._db = sqlite3.connect(folder/f"{actor_id}.sqlite", isolation_level=None)

    def close(self) -> None:
        self._db.close()
