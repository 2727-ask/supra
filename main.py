import pathlib
import subprocess
import json
import functools
from typing import Tuple, List, Optional
from pydantic import BaseModel, Field

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from tools import write_file, read_file
import functools
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from states import PlanState
from tools import init_project_root
from nodes.planner_node import planner_node
from nodes.research_node import research_node
from nodes.coder_node import coder_node
from nodes.should_continue import should_continue

from utils.logger import log_plan

if __name__ == "__main__":
    # Setup
    init_project_root()
    llm = ChatOllama(model="qwen2.5-coder:7b", temperature=0)
    
    # Build Graph
    workflow = StateGraph(PlanState)
    
    # Add Nodes
    workflow.add_node("research_node", functools.partial(research_node, llm=llm))
    workflow.add_node("planner_node", functools.partial(planner_node, llm=llm))
    workflow.add_node("coder_node", functools.partial(coder_node, llm=llm))
    
    # Define Edges
    workflow.set_entry_point("research_node")
    workflow.add_edge("research_node", "planner_node")
    workflow.add_edge("planner_node", "coder_node")
    
    # Add Conditional Edge (The Loop)
    workflow.add_conditional_edges(
        "coder_node",
        should_continue,
        {
            "coder_node": "coder_node",
            END: END
        }
    )
    
    # Compile
    app = workflow.compile()
    
    # Run
    print("🚀 Starting AI Developer...")
    
    # Use stream to log state after each step
    inputs = {"user_query": "Create a tic tac toe game with game ui"}
    current_state = inputs
    
    for event in app.stream(inputs, stream_mode="values"):
        # event is the full state dictionary (or pydantic model converted to dict depending on graph setup)
        # With Pydantic state, values stream usually returns dicts in recent LangGraph versions or the state object
        log_plan(event)
        current_state = event
        
    print("\n✅ Done! Project saved in /generated_project")