from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.schemas.user import UserCreate, UserUpdate, UserStatusUpdate

router = APIRouter()


@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )

    user = crud.user.create(db, obj_in=user_in)
    return user


@router.get("/me", response_model=schemas.User)
def read_user_me(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve users.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    return user


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update a user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    # Check for duplicate username
    if user_in.username and user_in.username != user.username:
        existing_user = crud.user.get_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system.",
            )

    # Check for duplicate email
    if user_in.email and user_in.email != user.email:
        existing_user = crud.user.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="The user with this email already exists in the system.",
            )

    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.put("/{user_id}/status", response_model=schemas.User)
def update_user_status(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    status_in: UserStatusUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update user status (admin/superuser only).
    Only superusers and admins can change user status.
    """
    # Check if current user can manage users
    if not crud.user.can_manage_users(current_user):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to manage user status",
        )

    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    # Prevent non-superusers from creating superusers
    if (status_in.is_superuser is True and 
        not crud.user.is_superuser(current_user)):
        raise HTTPException(
            status_code=403,
            detail="Only superusers can grant superuser privileges",
        )

    # Prevent users from modifying their own superuser status
    if (user_id == current_user.id and 
        status_in.is_superuser is not None):
        raise HTTPException(
            status_code=400,
            detail="Cannot modify your own superuser status",
        )

    user = crud.user.update_user_status(db, db_obj=user, obj_in=status_in)
    return user


@router.delete("/{user_id}")
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    user = crud.user.remove(db=db, id=user_id)
    return {"message": "User deleted successfully"}
