# GRAFOMEM Reference LangGraph Agent

A reference implementation of a LangGraph agent that persists per-user memory using the GRAFOMEM checkpointer. This agent demonstrates how to durably store agent memory and, crucially, how to provably delete a user's thread, emitting a verifiable cryptographic erasure receipt.

## Quickstart

```python
import sqlite3
from typing import TypedDict, Annotated
import operator

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from grafomem_checkpoint import GrafomemSerializer, GrafomemCheckpointSaver
from grafomem_example.keys import load_or_create_identity

# 1. Self-hosted signing identity — your keys, no cloud.
private_key, public_key, key_id, trusted_keys = load_or_create_identity()

# 2. Setup the sqlite saver with the GRAFOMEM serde
# We set check_same_thread=False so LangGraph can access it across threads
conn = sqlite3.connect("memory.db", check_same_thread=False)
inner = SqliteSaver(conn, serde=GrafomemSerializer(private_key, key_id=key_id, trusted_keys=trusted_keys))

# 3. Wrap with the GRAFOMEM checkpointer
saver = GrafomemCheckpointSaver(inner)

# 4. Compile a simple deterministic memory graph
class State(TypedDict):
    messages: Annotated[list[str], operator.add]

def memory_node(state: State):
    return {"messages": []} # State is appended automatically

builder = StateGraph(State)
builder.add_node("memory", memory_node)
builder.add_edge(START, "memory")
builder.add_edge("memory", END)
graph = builder.compile(checkpointer=saver)

# 5. Run some turns on a thread
config = {"configurable": {"thread_id": "user-123"}}
graph.invoke({"messages": ["Hello! My name is Alice."]}, config=config)
graph.invoke({"messages": ["I live in Madrid."]}, config=config)

# 6. Erase memory and verify the cryptographic receipt
saver.delete_thread("user-123")
receipt = saver.last_receipt("user-123")
assert receipt.verify(public_key)
print("RECEIPT VERIFIED")
print(receipt.to_json())
```

## Honest Erasure

**Signed state-transition receipt** — cryptographic proof that the erasure operation occurred, bound to a key and a timestamp. This is not a claim of media sanitization or information-theoretic unrecoverability.

*There is no guaranteed, permanent, or non-recoverable deletion anywhere. Honesty is the differentiator.*

## Fair-Source
The GRAFOMEM runtime that this example depends on is Fair-Source software. This example repository itself is licensed under Apache-2.0.

## Fully Offline
This agent runs fully offline with self-hosted keys — there is no GRAFOMEM Cloud dependency and no external LLM API calls required by default.
