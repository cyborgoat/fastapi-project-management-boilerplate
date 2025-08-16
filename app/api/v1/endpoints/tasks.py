from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Task])
def read_tasks(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve tasks.
    """
    tasks = crud.task.get_multi_by_owner(db=db, owner_id=current_user.id, skip=skip, limit=limit)
    return tasks


@router.post("/", response_model=schemas.Task)
def create_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: schemas.TaskCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new task.
    """
    # Verify the project exists and user has access
    project = crud.project.get(db=db, id=task_in.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not crud.project.is_owner(db=db, db_obj=project, user_id=current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    task = crud.task.create_with_assignee(db=db, obj_in=task_in, assignee_id=current_user.id)
    return task


@router.get("/{task_id}", response_model=schemas.Task)
def read_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get task by ID.
    """
    task = crud.task.get(db=db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # Check if user has access through project ownership or task assignment
    if not (task.assignee_id == current_user.id or 
            crud.project.is_owner(db=db, db_obj=task.project, user_id=current_user.id)):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return task


@router.put("/{task_id}", response_model=schemas.Task)
def update_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    task_in: schemas.TaskUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an existing task.
    """
    task = crud.task.get(db=db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # Check if user has access through project ownership or task assignment
    if not (task.assignee_id == current_user.id or 
            crud.project.is_owner(db=db, db_obj=task.project, user_id=current_user.id)):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    task = crud.task.update(db=db, db_obj=task, obj_in=task_in)
    return task


@router.delete("/{task_id}")
def delete_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a task.
    """
    task = crud.task.get(db=db, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # Check if user has access through project ownership or task assignment
    if not (task.assignee_id == current_user.id or 
            crud.project.is_owner(db=db, db_obj=task.project, user_id=current_user.id)):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    task = crud.task.remove(db=db, id=task_id)
    return {"message": "Task deleted successfully"}


@router.get("/project/{project_id}", response_model=List[schemas.Task])
def get_tasks_by_project(
    *,
    db: Session = Depends(deps.get_db),
    project_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get tasks by project.
    """
    project = crud.project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    # Check if user has access to the project
    if not crud.project.is_owner(db=db, db_obj=project, user_id=current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    tasks = crud.task.get_multi_by_project(db=db, project_id=project_id, skip=skip, limit=limit)
    return tasks
