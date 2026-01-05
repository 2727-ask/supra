from langchain_core.messages import HumanMessage
import json
from states import PlanState

import json
import functools
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama

def research_node(state: PlanState, llm):
    query = state.user_query 
    
    # --- STEP 1: Scoped Conceptualization ---
    # ADDED: "MVP" and "Single Developer" constraints to stop scope creep.
    concept_prompt = f"""
    You are a pragmatic software architect. 
    User Request: "{query}"

    Constraint: Plan a "Minimum Viable Product" (MVP).
    Constraint: Assume a single developer is building this. 
    Constraint: Do NOT include features like "Team Collaboration", "AI", or "Cloud Sync" unless explicitly asked.

    Output strictly a JSON object:
    {{
      "name": "Short Project Name",
      "description": "One sentence summary",
      "features": ["Feature 1", "Feature 2", "Feature 3"] (Max 3-4 core features)
    }}
    """
    
    resp_concept = llm.invoke([HumanMessage(content=concept_prompt)])
    
    # Robust Cleaning
    try:
        clean_content = resp_concept.content.strip().replace("```json", "").replace("```", "")
        data_concept = json.loads(clean_content)
    except:
        # Fallback if model fails
        data_concept = {
            "name": "SimpleApp", 
            "description": query, 
            "features": ["Basic Functionality"]
        }

    # --- STEP 2: Stack Selection ---
    # ADDED: "Local Development" constraint.
    stack_prompt = f"""
    Project: {data_concept.get('name')}
    Features: {data_concept.get('features')}
    
    Recommend a simple, robust Tech Stack.
    Constraint: Prefer local-first (e.g., SQLite over MongoDB, Local file storage).
    Do not use any external libraries unless explicitly asked.
    Do not use any external frameworks unless explicitly asked.
    Strictly use vanilla implementation.
    Strictly use HTML, CSS, and JavaScript.
    Output strictly a JSON list of strings. Example: ["HTML", "CSS", "JavaScript", "LocalStorage"]
    """
    
    resp_stack = llm.invoke([HumanMessage(content=stack_prompt)])
    
    try:
        clean_stack = resp_stack.content.strip().replace("```json", "").replace("```", "")
        data_stack = json.loads(clean_stack)
    except:
        data_stack = ["HTML", "CSS", "JavaScript", "LocalStorage"]

    # --- STEP 3: Clean Synthesis ---
    # Improved formatting to avoid the "\n" mess in the logs
    summary = (
        f"APP: {data_concept.get('name')}\n"
        f"GOAL: {data_concept.get('description')}\n"
        f"STACK: {', '.join(data_stack)}\n"
        f"SCOPE: MVP"
    )

    research_logs = {
        "concept": data_concept,
        "stack": data_stack,
        "summary": summary
    }

    return {
        "name": data_concept.get("name"),
        "description": data_concept.get("description"),
        "features": data_concept.get("features"), # Now strictly returned
        "techstack": data_stack,
        "research_notes": summary,
        "logs": {"research": research_logs}
    }