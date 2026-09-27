from pathlib import Path
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "backend" / "checkpoints.sqlite"


connection = sqlite3.connect(
    DATABASE_PATH,
    check_same_thread=False,
)

checkpointer = SqliteSaver(connection)