from pydantic import BaseModel, Field, ConfigDict
from .ImplementationTask import ImplementationTask

class TaskPlan(BaseModel):
    implementation_steps: list[ImplementationTask] = Field(description="A list of steps to be taken to implement the task")
    model_config = ConfigDict(extra="allow")