from datetime import datetime
from enum import IntEnum
from pydantic import BaseModel, Field


class TaskPriority(IntEnum):
    """Integer-backed priority levels for tasks."""
    LOW = 0
    MID = 1
    HIGH = 2


class TaskCreateRequest(BaseModel):
    """
    Request schema for creating a new task.
    """
    title: str = Field(..., description="Title of the task")
    description: str = Field(..., description="Detailed description of the task")
    duration: int = Field(..., description="Duration of the task in hours")
    priority: TaskPriority = Field(..., description="Priority level of the task")
    deadline: datetime = Field(..., description="Deadline for the task")
    username: str = Field(..., description="Username of the task owner")


class TaskUpdateRequest(BaseModel):
    """
    Request schema for updating an existing task.
    """
    title: str = Field(..., description="Updated title of the task")
    description: str = Field(..., description="Updated description of the task")
    duration: int = Field(..., description="Updated duration of the task in hours")
    priority: TaskPriority = Field(..., description="Updated priority level")
    deadline: datetime = Field(..., description="Updated deadline for the task")


class TaskResponse(BaseModel):
    """
    Schema for returning task data.
    """
    id: int
    title: str
    description: str
    duration: int
    priority: TaskPriority
    deadline: datetime
    username: str

    class Config:
        orm_mode = True
