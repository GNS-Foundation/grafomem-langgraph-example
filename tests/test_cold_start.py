import sqlite3
import pytest
from langgraph.checkpoint.sqlite import SqliteSaver
from grafomem_checkpoint import GrafomemSerializer, GrafomemCheckpointSaver
from grafomem_example.keys import load_or_create_identity
from grafomem_example.agent import build_graph

def test_cold_start():
    private_key, public_key, key_id, trusted_keys = load_or_create_identity()
    
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    inner = SqliteSaver(conn, serde=GrafomemSerializer(private_key, key_id=key_id, trusted_keys=trusted_keys))
    saver = GrafomemCheckpointSaver(inner)
    
    graph = build_graph(saver)
    
    config = {"configurable": {"thread_id": "ci"}}
    
    # 1. Add some memory
    graph.invoke({"messages": ["Test memory 1"]}, config=config)
    graph.invoke({"messages": ["Test memory 2"]}, config=config)
    
    # 2. Check memory persists
    state = graph.get_state(config)
    assert "messages" in state.values
    assert len(state.values["messages"]) == 2
    
    # 3. Delete thread
    saver.delete_thread("ci")
    
    # 4. Verify receipt
    receipt = saver.last_receipt("ci")
    assert receipt is not None
    assert receipt.scope == "ci"
    assert receipt.verify(public_key) is True
    
    # 5. Recall after delete shows empty
    state_after = graph.get_state(config)
    assert not state_after.values.get("messages")
