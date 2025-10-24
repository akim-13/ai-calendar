from fastapi import APIRouter
from backend.database import DBSession
from backend.schemas.tasks import (
    TaskCreateRequest,
    TaskUpdateRequest,
    TaskResponse,
)
from backend.services import tasks
from backend.services.tasks import TaskNotFoundError
from fastapi import HTTPException, status

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/create", response_model=TaskResponse)
def create(db: DBSession, request: TaskCreateRequest) -> TaskResponse:
    """Create a new task."""
    task = tasks.create_task(db, request)
    return TaskResponse.from_orm(task)


@router.put("/update/{taskID}", response_model=TaskResponse)
def update(db: DBSession, taskID: int, request: TaskUpdateRequest) -> TaskResponse:
    """Update an existing task."""
    task = tasks.update_task(db, taskID, request)
    return TaskResponse.from_orm(task)


@router.delete("/delete/{taskID}", status_code=status.HTTP_204_NO_CONTENT)
def delete(db: DBSession, taskID: int) -> None:
    """Delete a task."""
    try:
        tasks.delete_task(db, taskID)
    except TaskNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/user/{username}", response_model=list[TaskResponse])
def list_user_tasks(db: DBSession, username: str) -> list[TaskResponse]:
    """List all tasks for a user."""
    task_list = tasks.list_user_tasks(db, username)
    return [TaskResponse.from_orm(t) for t in task_list]


@router.get("/user/{username}/latest", response_model=TaskResponse)
def get_latest_user_task(db: DBSession, username: str) -> TaskResponse:
    """Get the most recent task for a user."""
    task = tasks.get_latest_user_task(db, username)
    return TaskResponse.from_orm(task)
