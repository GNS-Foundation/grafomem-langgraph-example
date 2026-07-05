import argparse
import sys
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

from grafomem_checkpoint import GrafomemSerializer, GrafomemCheckpointSaver
from grafomem_example.keys import load_or_create_identity
from grafomem_example.agent import build_graph

HONEST_ERASURE_CAVEAT = """
Signed state-transition receipt — cryptographic proof that the erasure operation occurred, bound to a key and a timestamp. This is not a claim of media sanitization or information-theoretic unrecoverability.
"""

def main():
    parser = argparse.ArgumentParser(description="GRAFOMEM Reference Agent")
    parser.add_argument("--user", type=str, required=True, help="User ID (thread ID)")
    parser.add_argument("--script", type=str, help="Path to input script file for headless mode")
    args = parser.parse_args()

    user_id = args.user

    private_key, public_key, key_id, trusted_keys = load_or_create_identity()

    conn = sqlite3.connect("memory.db", check_same_thread=False)
    inner = SqliteSaver(conn, serde=GrafomemSerializer(private_key, key_id=key_id, trusted_keys=trusted_keys))
    saver = GrafomemCheckpointSaver(inner)
    
    graph = build_graph(saver)
    config = {"configurable": {"thread_id": user_id}}

    inputs = []
    if args.script:
        with open(args.script, "r") as f:
            inputs = [line.strip() for line in f if line.strip()]
    
    def get_input(prompt):
        if inputs:
            val = inputs.pop(0)
            print(f"{prompt}{val}")
            return val
        if args.script:
            sys.exit(0)
        try:
            return input(prompt)
        except EOFError:
            return "/quit"

    print(f"Started session for {user_id}. Type a fact to remember, or /recall, /forget, /quit.")
    
    while True:
        cmd = get_input("> ")
        if not cmd:
            continue
            
        if cmd == "/quit":
            break
        elif cmd == "/recall":
            state = graph.get_state(config)
            messages = state.values.get("messages", [])
            if not messages:
                print("No memory.")
            else:
                for msg in messages:
                    print(f"Remembered: {msg}")
        elif cmd == "/forget":
            saver.delete_thread(user_id)
            receipt = saver.last_receipt(user_id)
            if receipt is None:
                print("Error: No receipt generated.")
                continue
                
            is_valid = receipt.verify(public_key)
            if is_valid:
                print("RECEIPT VERIFIED")
            else:
                print("RECEIPT VERIFICATION FAILED")
                
            print(receipt.to_json())
            print(HONEST_ERASURE_CAVEAT)
        else:
            # Normal turn
            graph.invoke({"messages": [cmd]}, config=config)

if __name__ == "__main__":
    main()
