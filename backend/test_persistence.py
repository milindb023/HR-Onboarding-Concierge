import sqlite3

from app.persistence import DATABASE_PATH, checkpointer


THREAD_ID = "persistence-test-001"

config = {
    "configurable": {
        "thread_id": THREAD_ID,
        "checkpoint_ns": "",
    }
}


# Write a small checkpoint directly.
checkpointer.put(
    config,
    {
        "v": 4,
        "ts": "2026-09-27T00:00:00Z",
        "id": "persistence-test-checkpoint",
        "channel_values": {
            "question": "Persistence test",
            "response": "SQLite checkpoint created successfully",
        },
        "channel_versions": {},
        "versions_seen": {},
    },
    {},
    {},
)


# Read it back using the same thread_id.
saved_checkpoint = checkpointer.get(config)


print("DATABASE PATH")
print(DATABASE_PATH)

print("\nDATABASE EXISTS")
print(DATABASE_PATH.exists())

print("\nTHREAD ID")
print(THREAD_ID)

print("\nCHECKPOINT FOUND")
print(saved_checkpoint is not None)

print("\nCHECKPOINT")
print(saved_checkpoint)


# Verify that SQLite contains the checkpoint.
connection = sqlite3.connect(DATABASE_PATH)

cursor = connection.cursor()

cursor.execute(
    "SELECT COUNT(*) FROM checkpoints WHERE thread_id = ?",
    (THREAD_ID,),
)

count = cursor.fetchone()[0]

connection.close()

print("\nCHECKPOINT ROW COUNT")
print(count)


assert DATABASE_PATH.exists()
assert saved_checkpoint is not None
assert count >= 1

print("\nPersistence test passed.")