from datetime import datetime

from fastapi import Form
from pydantic import BaseModel


class TaskBaseForm(BaseModel):
    """
    Base form model with shared fields for creating/updating a task.
    """

    title: str
    description: str
    duration: int
    priority: int
    deadline: datetime

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        description: str = Form(...),
        duration: int = Form(...),
        priority: int = Form(...),
        deadline: datetime = Form(...),
    ) -> "TaskBaseForm":
        """Create a TaskBaseForm instance from form data."""
        return cls(
            title=title,
            description=description,
            duration=duration,
            priority=priority,
            deadline=deadline,
        )


class TaskCreateForm(TaskBaseForm):
    """
    Form model for creating a new task.
    """

    # Inherits `as_form` directly.


class TaskUpdateForm(TaskBaseForm):
    """
    Form model for updating an existing task.
    """

    editID: int

    @classmethod
    def as_form(
        cls,
        title: str = Form(...),
        description: str = Form(...),
        duration: int = Form(...),
        priority: int = Form(...),
        deadline: datetime = Form(...),
        editID: int = Form(...),
    ) -> "TaskUpdateForm":
        """Create a TaskUpdateForm instance from form data."""
        # Reuse TaskBaseForm’s constructor by unpacking.
        base = TaskBaseForm.as_form(title, description, duration, priority, deadline)
        return cls(editID=editID, **base.model_dump())
