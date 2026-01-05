from langgraph.graph import END
from states import PlanState

def should_continue(state: PlanState):
    """
    Decides if we should loop back to coder or end.
    """
    if state.current_task_index < len(state.task_queue):
        return "coder_node"
    return END
