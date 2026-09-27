from app.graph import graph, run_ticket


THREAD_ID = "graph-persistence-test-001"

config = {
    "configurable": {
        "thread_id": THREAD_ID,
    }
}


print("GRAPH PERSISTENCE TEST")
print("----------------------")

print("\nTHREAD ID")
print(THREAD_ID)


# The thread does not exist yet.
# Because the graph has a checkpointer, get_state() should work.
snapshot = graph.get_state(config)


print("\nINITIAL SNAPSHOT")
print(snapshot)


print("\nINITIAL VALUES")
print(snapshot.values)


assert snapshot.values == {}

print("\nCHECKPOINT CONFIGURATION")
print("Graph successfully supports persistent state.")

print("\nGraph persistence wiring test passed.")