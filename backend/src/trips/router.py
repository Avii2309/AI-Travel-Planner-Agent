"""HTTP API for authenticated trip planning CRUD."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Response, status

from src.auth.security import CurrentUserDependency
from src.presentation.api.dependencies import DatabaseSessionDependency
from src.trips.schemas import TripCreate, TripResponse, TripUpdate
from src.trips.service import (
    TripNotFoundError,
    create_trip,
    delete_trip,
    get_trip,
    list_trips,
    update_trip,
)

router = APIRouter(prefix="/trips", tags=["trips"])
PaginationOffset = Annotated[int, Query(ge=0, description="Number of trips to skip")]
PaginationLimit = Annotated[int, Query(ge=1, le=100, description="Maximum trips to return")]


def _not_found_exception() -> HTTPException:
    """Use the same response for missing and non-owned resources."""

    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")


@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED, summary="Create a trip")
async def create(
    request: TripCreate,
    session: DatabaseSessionDependency,
    current_user: CurrentUserDependency,
) -> TripResponse:
    """Create a trip owned by the authenticated user."""

    return await create_trip(session, current_user, request)


@router.get("", response_model=list[TripResponse], summary="List my trips")
async def list_owned_trips(
    session: DatabaseSessionDependency,
    current_user: CurrentUserDependency,
    offset: PaginationOffset = 0,
    limit: PaginationLimit = 100,
) -> list[TripResponse]:
    """List paginated trips owned by the authenticated user."""

    return list(await list_trips(session, current_user, offset=offset, limit=limit))


@router.get("/{trip_id}", response_model=TripResponse, summary="Get one of my trips")
async def get_owned_trip(
    trip_id: UUID,
    session: DatabaseSessionDependency,
    current_user: CurrentUserDependency,
) -> TripResponse:
    """Return an owned trip."""

    try:
        return await get_trip(session, current_user, trip_id)
    except TripNotFoundError as error:
        raise _not_found_exception() from error


@router.put("/{trip_id}", response_model=TripResponse, summary="Update one of my trips")
async def update_owned_trip(
    trip_id: UUID,
    request: TripUpdate,
    session: DatabaseSessionDependency,
    current_user: CurrentUserDependency,
) -> TripResponse:
    """Partially update an owned trip while preserving valid dates."""

    try:
        return await update_trip(session, current_user, trip_id, request)
    except TripNotFoundError as error:
        raise _not_found_exception() from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete one of my trips")
async def delete_owned_trip(
    trip_id: UUID,
    session: DatabaseSessionDependency,
    current_user: CurrentUserDependency,
) -> Response:
    """Permanently delete an owned trip."""

    try:
        await delete_trip(session, current_user, trip_id)
    except TripNotFoundError as error:
        raise _not_found_exception() from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
