from typing import Any, Dict, List

from core.entities import Task
from sqlalchemy.orm import Session

from sqlalchemy import desc

from backend.database import Task
from backend.schemas.tasks import TaskCreateRequest, TaskUpdateRequest
from backend.schemas.tasks import TaskPriority

class TaskNotFoundError(Exception):
    """Raised when a task with the given ID does not exist."""


def create_task(db: Session, request: TaskCreateRequest) -> Task:
    """Create a new task for a given user."""
    task = Task(
        title=request.title,
        description=request.description,
        duration=request.duration,
        priority=request.priority,
        deadline=request.deadline,
        username=request.username,
    )

    db.add(task)
    db.refresh(task)
    return task


def update_task(db: Session, taskID: int, request: TaskUpdateRequest) -> Task:
    """Update an existing task."""
    task = db.query(Task).filter(Task.id == taskID).first()
    if not task:
        raise TaskNotFoundError(f"Task with ID {taskID} not found.")

    # Update fields
    task.title = request.title
    task.description = request.description
    task.priority = request.priority
    task.deadline = request.deadline


    db.refresh(task)

    return task


def delete_task(db: Session, taskID: int) -> None:
    """Delete a task by ID. Raises TaskNotFoundError if it doesn’t exist."""
    task = db.query(Task).filter(Task.id == taskID).first()
    if not task:
        raise TaskNotFoundError(f"Task with ID {taskID} not found.")

    db.delete(task)


def list_user_tasks(db: Session, username: str) -> List[Task]:
    """Return all tasks belonging to a specific user."""
    return db.query(Task).filter(Task.username == username).all()


def get_latest_user_task(db: Session, username: str) -> Task:
    """Return the most recently created or updated task for a user."""
    latest_task = (
        db.query(Task)
        .filter(Task.username == username)
        .order_by(desc(Task.id))
        .first()
    )

    if not latest_task:
        raise TaskNotFoundError(f"No tasks found for user '{username}'.")

    return latest_task
