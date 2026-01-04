from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
from langgraph.constants import END

from states import Plan, TaskPlan, CoderState
from agent.prompts import Prompts
from agent.tools import read_file, write_file, list_files, get_current_directory

from langchain_ollama import ChatOllama

class Agents:
    def __init__(self, llm: any = None):
        self.llm = llm
        self.prompts = Prompts()
    

    def planner_agent(self, state: dict) -> dict:
        """Converts user prompt into a structured Plan."""
        user_prompt = state["user_prompt"]
        resp = self.llm.with_structured_output(Plan).invoke(
            self.prompts.planner_prompt(user_prompt)
        )
        
        if resp is None:
            raise ValueError("Planner did not return a valid response.")
        return {"plan": resp}

    def architect_agent(self, state: dict) -> dict:
        """Creates TaskPlan from Plan."""
        from langchain_core.output_parsers import PydanticOutputParser
        
        plan: Plan = state["plan"]
        parser = PydanticOutputParser(pydantic_object=TaskPlan)
        
        prompt = self.prompts.architect_prompt(plan=plan.model_dump_json())
        # Append format instructions to ensuring the model knows how to output JSON
        prompt += "\n\n" + parser.get_format_instructions()
        
        # Invoke directly
        try:
            resp_msg = self.llm.invoke(prompt)
            # Parse the content
            task_plan = parser.parse(resp_msg.content)
        except Exception as e:
            # Fallback for some models: try to extract JSON if it's wrapped in markdown
            print(f"Architect Agent Parse Error: {e}, attempting fallback parsing...")
            import json
            import re
            content = resp_msg.content
            match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
            if match:
                content = match.group(1)
            try:
                task_plan = parser.parse(content)
            except Exception as e2:
                print(f"Architect Agent Fallback Failed: {e2}")
                raise ValueError("Architect Agent failed to generate a valid TaskPlan.")

        task_plan.plan = plan
        print(task_plan.model_dump_json())
        return {"task_plan": task_plan}

    def coder_agent(self, state: dict) -> dict:
        """LangGraph tool-using coder agent."""
        coder_state: CoderState = state.get("coder_state")
        if coder_state is None:
            coder_state = CoderState(task_plan=state["task_plan"], current_step_idx=0)

        steps = coder_state.task_plan.implementation_steps
        if coder_state.current_step_idx >= len(steps):
            return {"coder_state": coder_state, "status": "DONE"}

        current_task = steps[coder_state.current_step_idx] # ImplementationTask
        # Need to fix how we read file in tool usage vs here.
        # Actually in the prompt below we read the file using the tool? 
        # No, 'read_file.run(...)'. Since 'read_file' is a structured tool, run might work or invoke.
        # langchain tools usually have .invoke or .run
        
        # We need to make sure the file exists or handle error, but read_file handles it.
        existing_content = read_file.invoke(current_task.filepath)

        system_prompt = self.prompts.coder_system_prompt()
        user_prompt = (
            f"Task: {current_task.task_description}\n"
            f"File: {current_task.filepath}\n"
            f"Existing content:\n{existing_content}\n"
            "Use write_file(path, content) to save your changes."
        )

        coder_tools = [read_file, write_file, list_files, get_current_directory]
        # create_react_agent creates a graph. We need to invoke it.
        # The state for this agent is a list of messages.
        
        react_agent = create_react_agent(self.llm, coder_tools)

        # The output of react_agent.invoke includes 'messages'
        result = react_agent.invoke({"messages": [{"role": "system", "content": system_prompt},
                                        {"role": "user", "content": user_prompt}]})
        
        print(f"\n--- Coder Agent Step {coder_state.current_step_idx} ---")
        print(f"File: {current_task.filepath}")
        for m in result["messages"]:
            print(f"[{m.type}]: {m.content}")
            if hasattr(m, 'tool_calls') and m.tool_calls:
                print(f"Tool Calls: {m.tool_calls}")
        
        
        # We don't really use the result messages here except to confirm it finished.
        # Ideally we capture the output.
        
        # FALLBACK: If the model outputs the tool call as JSON in the content instead of a structured tool call
        import json
        last_message = result["messages"][-1]
        if not (hasattr(last_message, 'tool_calls') and last_message.tool_calls):
            content = last_message.content
            # Cleanup markdown code blocks if present
            if "```" in content:
                import re
                match = re.search(r"```(?:json)?(.*?)```", content, re.DOTALL)
                if match:
                    content = match.group(1).strip()
                
            try:
                parsed_json = None
                try:
                    parsed_json = json.loads(content)
                except json.JSONDecodeError:
                    # Regex fallback
                    import re
                    # Check for "path" and "content"
                    path_match = re.search(r'"path"\s*:\s*"([^"]+)"', content)
                    content_match = re.search(r'"content"\s*:\s*`([^`]+)`', content, re.DOTALL)
                    if not content_match:
                         content_match = re.search(r'"content"\s*:\s*"(.*)"\s*}', content, re.DOTALL)
                    
                    if path_match and content_match:
                         # Construct a pseudo tool call dict
                         parsed_json = {
                             "name": "write_file",
                             "arguments": {
                                 "path": path_match.group(1),
                                 "content": content_match.group(1)
                             }
                         }

                if isinstance(parsed_json, dict) and parsed_json.get("name") == "write_file":
                    args = parsed_json.get("arguments", {})
                    path = args.get("path")
                    file_content = args.get("content")
                    if path and file_content:
                        print(f"Fallback: Executing write_file for {path}")
                        write_file.invoke({"path": path, "content": file_content})
                        coder_state.current_step_idx += 1
                        return {"coder_state": coder_state}

            except Exception as e:
                # print(f"Fallback Parse Error: {e}") 
                pass

        coder_state.current_step_idx += 1
        # Set status to undefined or something to continue loop?
        # The loop logic is in conditional edges.
        # If we return "status": "DONE" it ends.
        # If we return normal state, it goes back to "coder" node.
        
        return {"coder_state": coder_state}
            

from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

_ = load_dotenv()

if not os.getenv("GROQ_API_KEY") and os.getenv("API_KEY"):
    os.environ["GROQ_API_KEY"] = os.getenv("API_KEY")

agentGraph = StateGraph(dict)

provider = os.getenv("AGENT_PROVIDER", "groq")
print(f"Agent Provider: {provider}")

if provider == "groq":
    print("Using cloud mode")
    llm = ChatGroq(model="moonshotai/kimi-k2-instruct-0905", temperature=0.7)
else:
    llm = ChatOllama(model="qwen2.5-coder:7b", temperature=0)

agents = Agents(llm)

agentGraph.add_node("planner_agent", agents.planner_agent)
agentGraph.add_node("architect_agent", agents.architect_agent)
agentGraph.add_node("coder_agent", agents.coder_agent)

agentGraph.add_edge("planner_agent", "architect_agent")
agentGraph.add_edge("architect_agent", "coder_agent")

# Fix: conditional edge refers to "coder_agent" which is the node name.
agentGraph.add_conditional_edges("coder_agent",
    lambda s: "END" if s.get("status") == "DONE" else "coder_agent",
    {"END": END, "coder_agent": "coder_agent"})


agentGraph.set_entry_point("planner_agent")
supra = agentGraph.compile()

if __name__ == "__main__":
    print("Graph")
    # We need to pass the initial state structure that matches what we expect
    # The state is a dict, so we can just pass the user prompt.
    result = supra.invoke({"user_prompt": "Build a colourful modern todo app in html css and js"}, {"recursion_limit": 100})
    print("Final State:", result)
