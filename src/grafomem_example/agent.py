import operator
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    messages: Annotated[list[str], operator.add]

def memory_node(state: State):
    # Deterministic echo. The input message was already appended to state.messages.
    # We return an empty list because state is Annotated with operator.add,
    # so we don't want to duplicate the existing messages.
    return {"messages": []}

def build_graph(saver):
    builder = StateGraph(State)
    builder.add_node("memory", memory_node)
    builder.add_edge(START, "memory")
    builder.add_edge("memory", END)
    return builder.compile(checkpointer=saver)
