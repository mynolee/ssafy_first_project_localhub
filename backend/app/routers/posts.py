from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.errors import ApiError
from app.models import Post
from app.schemas import (
    ApiResponse,
    DeletedPostResponse,
    PostCategory,
    PostCreateRequest,
    PostDeleteRequest,
    PostDetailResponse,
    PostListResponse,
    PostUpdateRequest,
    RegionCode,
)


router = APIRouter(prefix="/api/posts", tags=["posts"])


def get_post_or_raise(session: Session, post_id: int) -> Post:
    post = session.get(Post, post_id)
    if not post:
        raise ApiError(404, "게시글을 찾을 수 없습니다.", "POST_NOT_FOUND")
    return post


def verify_password(post: Post, password: str) -> None:
    if post.password != password:
        raise ApiError(403, "수정용 비밀번호가 일치하지 않습니다.", "INVALID_PASSWORD")


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[PostDetailResponse])
def create_post(
    request: PostCreateRequest,
    session: Session = Depends(get_db),
) -> ApiResponse[PostDetailResponse]:
    post = Post(**request.model_dump(mode="json"))
    session.add(post)
    session.commit()
    session.refresh(post)
    return ApiResponse(data=post, message="게시글 작성 성공")


@router.get("", response_model=ApiResponse[list[PostListResponse]])
def list_posts(
    region: RegionCode | None = None,
    category: PostCategory | None = None,
    session: Session = Depends(get_db),
) -> ApiResponse[list[PostListResponse]]:
    statement = select(Post).order_by(Post.created_at.desc(), Post.id.desc())
    if region:
        statement = statement.where(Post.region == region.value)
    if category:
        statement = statement.where(Post.category == category.value)
    posts = session.scalars(statement).all()
    return ApiResponse(data=list(posts), message="게시글 목록 조회 성공")


@router.get("/{post_id}", response_model=ApiResponse[PostDetailResponse])
def get_post(post_id: int, session: Session = Depends(get_db)) -> ApiResponse[PostDetailResponse]:
    return ApiResponse(data=get_post_or_raise(session, post_id), message="게시글 상세 조회 성공")


@router.patch("/{post_id}", response_model=ApiResponse[PostDetailResponse])
def update_post(
    post_id: int,
    request: PostUpdateRequest,
    session: Session = Depends(get_db),
) -> ApiResponse[PostDetailResponse]:
    post = get_post_or_raise(session, post_id)
    verify_password(post, request.password)
    updates = request.model_dump(exclude={"password"}, exclude_none=True, mode="json")
    for field, value in updates.items():
        setattr(post, field, value)
    session.commit()
    session.refresh(post)
    return ApiResponse(data=post, message="게시글 수정 성공")


@router.delete("/{post_id}", response_model=ApiResponse[DeletedPostResponse])
def delete_post(
    post_id: int,
    request: PostDeleteRequest,
    session: Session = Depends(get_db),
) -> ApiResponse[DeletedPostResponse]:
    post = get_post_or_raise(session, post_id)
    verify_password(post, request.password)
    session.delete(post)
    session.commit()
    return ApiResponse(data=DeletedPostResponse(id=post_id), message="게시글 삭제 성공")
