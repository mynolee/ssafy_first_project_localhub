from datetime import datetime
from enum import Enum
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator


def to_camel(value: str) -> str:
    first, *rest = value.split("_")
    return first + "".join(word.capitalize() for word in rest)


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class PostCategory(str, Enum):
    TOURIST = "TOURIST"
    RESTAURANT = "RESTAURANT"
    FESTIVAL = "FESTIVAL"
    CULTURE = "CULTURE"


class RegionCode(str, Enum):
    SEOUL = "SEOUL"
    DAEJEON_CHUNGCHEONG = "DAEJEON_CHUNGCHEONG"
    GUMI_GYEONGBUK = "GUMI_GYEONGBUK"
    GWANGJU_JEOLLA = "GWANGJU_JEOLLA"
    BUSAN = "BUSAN"


class PlaceCategory(str, Enum):
    TOURIST = "TOURIST"
    RESTAURANT = "RESTAURANT"
    FESTIVAL = "FESTIVAL"
    CULTURE = "CULTURE"
    COURSE = "COURSE"
    LEISURE = "LEISURE"
    ACCOMMODATION = "ACCOMMODATION"
    SHOPPING = "SHOPPING"


DataT = TypeVar("DataT")


class ApiResponse(CamelModel, Generic[DataT]):
    success: bool = True
    data: DataT
    message: str


class ErrorDetail(CamelModel):
    code: str


class ErrorResponse(CamelModel):
    success: bool = False
    data: None = None
    message: str
    error: ErrorDetail


class PlaceResponse(CamelModel):
    id: int
    source_id: str
    region: RegionCode
    name: str
    category: str
    address: str | None
    latitude: float | None
    longitude: float | None
    description: str | None
    image_url: str | None
    phone: str | None


class PostCreateRequest(CamelModel):
    region: RegionCode
    category: PostCategory
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1, max_length=5000)
    author: str = Field(default="익명", min_length=1, max_length=20)
    password: str = Field(min_length=4, max_length=20)


class PostUpdateRequest(CamelModel):
    password: str = Field(min_length=4, max_length=20)
    region: RegionCode | None = None
    category: PostCategory | None = None
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1, max_length=5000)
    author: str | None = Field(default=None, min_length=1, max_length=20)

    @model_validator(mode="after")
    def require_update_field(self) -> "PostUpdateRequest":
        if not any((self.region, self.category, self.title, self.content, self.author)):
            raise ValueError("수정할 필드를 하나 이상 입력해 주세요.")
        return self


class PostDeleteRequest(CamelModel):
    password: str = Field(min_length=4, max_length=20)


class PostListResponse(CamelModel):
    id: int
    region: RegionCode
    category: PostCategory
    title: str
    author: str
    created_at: datetime
    updated_at: datetime


class PostDetailResponse(PostListResponse):
    content: str


class DeletedPostResponse(CamelModel):
    id: int


class ChatHistoryItem(CamelModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1000)


class ChatRequest(CamelModel):
    message: str = Field(min_length=1, max_length=500)
    history: list[ChatHistoryItem] = Field(default_factory=list, max_length=10)
    region: RegionCode | None = None


class ChatMatchedItem(CamelModel):
    type: Literal["PLACE", "POST"]
    id: int
    title: str
    category: str | None
    region: RegionCode


class ChatResponse(CamelModel):
    answer: str
    matched_items: list[ChatMatchedItem]
