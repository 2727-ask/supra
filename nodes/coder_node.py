import json
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from states import PlanState
from tools import read_file, write_file

def coder_node(state: PlanState, llm):
    """
    Executes the current task from the task_queue.
    """
    current_idx = state.current_task_index
    total_tasks = len(state.task_queue)
    
    if current_idx >= total_tasks:
        return {}
        
    current_task = state.task_queue[current_idx]
    print(f"\n👨‍💻 [Task {current_idx + 1}/{total_tasks}]: {current_task}")

    # 1. Build File Context
    project_context = ""
    for file_obj in state.files:
        path = file_obj.path
        content = read_file.invoke(path) 
        if content:
            project_context += f"\n--- FILE: {path} ---\n{content}\n"
    
    if not project_context:
        project_context = "(Project is currently empty)"

    # 2. Prepare Context Variables
    allowed_files_str = ", ".join([f.path for f in state.files])
    tech_stack_str = ", ".join(state.techstack)
    # CRITICAL FIX: Convert features list to string for the prompt
    features_str = "\n".join([f"- {f}" for f in state.features])

    # 3. The Prompt
    prompt = f"""
    You are a Senior Web Developer.
    
    GOAL: Execute this task: "{current_task}"
    
    === APP CONTEXT (WHAT WE ARE BUILDING) ===
    App Name: {state.name}
    Description: {state.description}
    Core Features:
    {features_str}
    
    === STRICT CONSTRAINTS ===
    1. **HTML-First UI**: If editing HTML, you MUST include the actual UI elements (buttons, inputs, divs) mentioned in the features. Do NOT create empty <body> tags.
    2. **Allowed Files**: Only read/write: [{allowed_files_str}].
    3. **Wiring Integrity**: If generating an HTML file, you MUST Include <script src="..."> for EVERY .js file and <link rel="stylesheet"> for EVERY .css file listed in 'Allowed Files'. Do not omit any.
    4. **Tech Stack**: Use ONLY: {tech_stack_str}.
    5. **No Placeholders**: Write the FULL functional code.
    
    === CURRENT FILES ===
    {project_context}
    
    === INSTRUCTIONS ===
    1. Write the code required for the task.
    2. Use the following XML-like format to output files:
    
    <file path="exact_file_path">
    FULL_CODE_HERE
    </file>
    
    Example:
    <file path="index.html">
    <html>...</html>
    </file>
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    # 4. Parse & Execute
    try:
        import re
        # Regex to capture <file path="..."> content </file>
        # flags=re.DOTALL allows . to match newlines
        pattern = r'<file path="(.*?)">\n?(.*?)\n?</file>'
        matches = re.findall(pattern, response.content, re.DOTALL)
        
        file_updates = []
        for path, content in matches:
            # CLEANUP: Strip markdown code fences if the model included them inside the XML tags
            # e.g. ```javascript\n code... \n```
            content = re.sub(r"^```[a-zA-Z0-9]*\n?", "", content.strip())
            content = re.sub(r"```$", "", content.strip())
            
            file_updates.append({"action": "write", "path": path, "content": content})
            
            if path and content:
                write_file.invoke({"path": path, "content": content})
                print(f"   └── 💾 Wrote {path}")
                
        # Log & Increment
        current_logs = state.logs or {}
        if "execution" not in current_logs:
            current_logs["execution"] = []
        current_logs["execution"].append({
            "task_index": current_idx + 1,
            "task": current_task,
            "updates": file_updates
        })
        
        return {
            "current_task_index": current_idx + 1, 
            "logs": current_logs
        } 
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {"retry_count": state.retry_count + 1}