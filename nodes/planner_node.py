from langchain_core.messages import HumanMessage
import json
from states import PlanState  # Assuming this is your Pydantic model

def planner_node(state: PlanState, llm):
    name = state.name
    tech_stack = state.techstack
    features = state.features
    notes = state.research_notes

    print(f"📋 Planning tasks for: {name}")

    # --- STEP 1: Files ---
    file_prompt = f"""
    Plan the file structure for: "{name}"
    
    Stack: {tech_stack}
    Features: {features}
    
    Output strictly a JSON dict {{filename: purpose}}.
    Example: {{"index.html": "Main UI", "script.js": "Logic"}}
    """
    
    resp_files = llm.invoke([HumanMessage(content=file_prompt)])
    try:
        clean_files = resp_files.content.strip().replace("```json", "").replace("```", "")
        file_structure = json.loads(clean_files)
    except:
        file_structure = {"index.html": "UI", "script.js": "Logic", "style.css": "Styles"}

    # --- STEP 2: Tasks ---
    task_prompt = f"""
        We are building "{name}".
        File Structure: {json.dumps(file_structure)}
        Features: {features}
        
        Create a detailed implementation plan.
        
        CRITICAL RULES:
        1. **Descriptive Tasks**: Do NOT just say "Create HTML". 
           - BAD: "Create index.html"
           - GOOD: "Create index.html containing the app title, input field, 'Add' button, and a list container."
        2. **Batching**: Group logic by file.
           - Step 1: HTML (Structure + UI Elements).
           - Step 2: CSS (Styling).
           - Step 3: JS (Logic).
        3. **Wiring**: Ensure HTML links to CSS/JS in step 1.
        
        Output strictly a JSON list of strings.
    """
    
    resp_tasks = llm.invoke([HumanMessage(content=task_prompt)])
    
    try:
        clean_tasks = resp_tasks.content.strip().replace("```json", "").replace("```", "")
        task_queue = json.loads(clean_tasks)
    except:
        task_queue = ["Create index.html with UI elements", "Create script.js"]

    # --- STEP 3: Verify & Patch ---
    # Ensure every file in the structure has a corresponding task
    for filename, purpose in file_structure.items():
        covered = False
        for task in task_queue:
            if filename in task:
                covered = True
                break
        
        if not covered:
            print(f"⚠️ Planner: Auto-injecting missing task for {filename}")
            task_queue.append(f"Create {filename} which handles: {purpose}")

    current_logs = state.logs or {}
    current_logs["planner"] = {"files_dict": file_structure, "task_queue": task_queue}
    
    return {
        "files": [{"path": k, "purpose": v} for k, v in file_structure.items()],
        "task_queue": task_queue,
        "logs": current_logs
    }