from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .File import File

class PlanState(BaseModel):
    user_query: str = Field(..., description="The initial user request")
    name: str = Field(default="", description="The name of app to be built")
    description: str = Field(default="", description="A oneline description of the app")
    techstack: List[str] = Field(default_factory=list, description="E.g. ['python', 'react', 'sqlite']")
    research_notes: Optional[str] = Field(None, description="Summary of core features and architectural decisions")
    task_queue: List[str] = Field(default_factory=list, description="Ordered list of granular technical tasks, e.g., ['Create requirements.txt', 'Setup Flask routes']")
    current_task_index: int = Field(0, description="Pointer to the current task in the queue")
    completed_tasks: List[str] = Field(default_factory=list, description="Log of what has been finished")
    features: List[str] = Field(default_factory=list, description="List of core features")
    files: List[File] = Field(default_factory=list, description="The evolving file structure")
    retry_count: int = Field(0, description="Counter for failed attempts on the current task")
    last_error: Optional[str] = Field(None, description="The specific error message from the last test run (if any)")
    logs: Dict[str, Any] = Field(default_factory=dict, description="Execution logs for each node")