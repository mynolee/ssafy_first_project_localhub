from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Place
from app.schemas import ApiResponse, PlaceCategory, PlaceResponse


router = APIRouter(prefix="/api/places", tags=["places"])


@router.get("", response_model=ApiResponse[list[PlaceResponse]])
def list_places(
    category: PlaceCategory | None = None,
    session: Session = Depends(get_db),
) -> ApiResponse[list[PlaceResponse]]:
    statement = select(Place).order_by(Place.name)
    if category:
        statement = statement.where(Place.category == category.value)
    places = session.scalars(statement).all()
    return ApiResponse(data=list(places), message="지역 정보 조회 성공")

