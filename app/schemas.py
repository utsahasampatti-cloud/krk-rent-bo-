from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from uuid import UUID

RoomsEnum = Literal["one", "two", "three", "four", "five_more"]
PetsEnum = Literal["Tak", "Nie"]

class Filters(BaseModel):
    city: str = "Kraków"

    # Райони: польські назви з діакритикою, напр "Nowa Huta", "Grzegórzki"
    districts: List[str] = Field(default_factory=list)

    # Ціна
    price_min: Optional[int] = None
    price_max: Optional[int] = None

    # Кімнати (multi enum)
    rooms: List[RoomsEnum] = Field(default_factory=list)

    # Тварини (OLX expects польською)
    pets: Optional[PetsEnum] = None

    # Паркінг (values мають бути URL-encoded в query_builder)
    parking: List[str] = Field(default_factory=list)

    # Ліфт
    elevator: Optional[bool] = None

class SearchRequest(BaseModel):
    user_id: int
    filters: Filters
    limit: int = 10

class SearchResponse(BaseModel):
    job_id: str

class ListingOut(BaseModel):
    id: UUID
    title: str
    price_value: Optional[float] = None
    location: Optional[str] = None
    url: str

class StateRequest(BaseModel):
    user_id: int
    listing_id: UUID
    state: Literal["liked", "skipped"]
