from fastapi import APIRouter

from app.users.dependencies import UserServiceDep
from app.users.schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/user", tags=["User Module"])


@router.get("/", summary="Get all users", response_model=list[UserResponse])
def get_all(user_service: UserServiceDep) -> list[UserResponse]:
    return user_service.get_all()


@router.get("/{user_id}", summary="Get user by id", response_model=UserResponse)
def get_by_id(user_service: UserServiceDep, user_id: int) -> UserResponse:
    return user_service.get_by_id(user_id)


@router.post("/", summary="Create an user", response_model=UserResponse)
def create(user_service: UserServiceDep, user_request: UserCreate) -> UserResponse:
    return user_service.create(user_request)


@router.patch("/{user_id}", summary="Update an user", response_model=UserResponse)
def update(
    user_service: UserServiceDep, user_id: int, user_request: UserUpdate
) -> UserResponse:
    return user_service.update(user_id, user_request)


@router.delete("/{user_id}", summary="Soft delete an user", response_model=UserResponse)
def delete(user_service: UserServiceDep, user_id: int) -> UserResponse:
    return user_service.delete(user_id)
