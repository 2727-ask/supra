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
    inputs = {"user_query": "Create a single-file Tetris game using only HTML, CSS, and vanilla JavaScript (ES6+). The file should be stand-alone (no external libraries) and run by opening the HTML file in a browser. Deliver well-commented, readable code and a brief usage/readme section at the top of the file explaining controls and how to run. Requirements:  Playfield (10x20 visible grid).  Tetrominoes with standard shapes (I, J, L, O, S, T, Z).  Piece spawn, movement (left/right/down), soft drop, hard drop.  Rotation (implement the Super Rotation System (SRS) or a reasonable rotation with wall kicks).  Next-piece preview (at least next 3) and Hold piece.  Line clearing with proper removal and collapse.  Scoring (single/double/triple/tetris), level progression (speed increases), and display of score, level, lines cleared.  Pause/resume and restart controls.  Save high score in localStorage.  Keyboard controls (arrow keys, space for hard drop, shift for hold, P to pause) and touch support for mobile (simple swipe/tap interface).  Responsive UI and basic styling (CSS) so it looks good on desktop and mobile.  No blocking UI; use requestAnimationFrame / setInterval responsibly.  Include unit-testable functions where appropriate (e.g., collision detection, rotation logic).  Accessibility: provide ARIA labels and allow keyboard-only play.  Add small sound effects (optional) but make them toggleable.  At top of file include a short checklist of acceptance criteria."}
    current_state = inputs
    
    for event in app.stream(inputs, stream_mode="values"):
        # event is the full state dictionary (or pydantic model converted to dict depending on graph setup)
        # With Pydantic state, values stream usually returns dicts in recent LangGraph versions or the state object
        log_plan(event)
        current_state = event
        
    print("\n✅ Done! Project saved in /generated_project")