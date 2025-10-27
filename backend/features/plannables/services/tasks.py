from typing import Any, Dict

from core.entities import Task
from sqlalchemy.orm import Session


def get_user_tasks(username: str, db: Session) -> None:
    """Return all tasks for a user as JSON, or an empty list if none exist."""
    raise NotImplementedError


def get_latest_user_task(username: str, db: Session) -> None:
    """Return the most recent task for a user, or None if none exist."""
    raise NotImplementedError


def edit_task(taskID: int, task_properties: Dict[str, Any], db: Session) -> None:
    """Update a task’s attributes if valid and types match; reject otherwise."""
    raise NotImplementedError

    task = db.query(Task).filter(Task.taskID == taskID).first()
    for attribute, value in task_properties.items():
        if not hasattr(task, attribute) or attribute == "taskID":
            return {"success": False}
        if type(getattr(task, attribute)) != type(value):
            return {"success": False}
        setattr(task, attribute, value)

    db.merge(task)
    db.commit()

    return {"success": True}


def set_task_complete(task_id: int, db: Session) -> None:
    """Mark a task complete and add points."""
    raise NotImplementedError

    task: Task = db.query(Task).filter(Task.taskID == task_id).first()
    if not task or task.isCompleted:
        return {"task_changed": False}

    task.user.currentPoints += task.duration
    task.isCompleted = True
    db.commit()

    return {"task_changed": True}


def set_task_incomplete(task_id: int, db: Session) -> None:
    """Mark a task incomplete, remove points, and update achievements."""
    raise NotImplementedError

    task: Task = db.query(Task).filter(Task.taskID == task_id).first()
    if not task or not task.isCompleted:
        return {"task_changed": False, "new_achievements": False}

    task.user.currentPoints -= task.duration
    task.isCompleted = False
    db.commit()

    return {"task_changed": True}


def delete_task(task_id: int, db: Session) -> None:
    """Delete a task if it exists, otherwise return false."""
    raise NotImplementedError

    task = db.query(Task).filter(Task.taskID == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        return {"task_deleted": True}

    return {"task_deleted": False}
