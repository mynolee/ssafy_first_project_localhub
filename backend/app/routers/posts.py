import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
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
    PostImageResponse,
    PostLikeResponse,
    PostListResponse,
    PostUpdateRequest,
    RegionCode,
)


router = APIRouter(prefix="/api/posts", tags=["posts"])

CONTENT_TYPE_EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


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
    post = get_post_or_raise(session, post_id)
    post.view_count += 1
    session.commit()
    session.refresh(post)
    return ApiResponse(data=post, message="게시글 상세 조회 성공")


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


@router.post("/{post_id}/like", response_model=ApiResponse[PostLikeResponse])
def like_post(post_id: int, session: Session = Depends(get_db)) -> ApiResponse[PostLikeResponse]:
    post = get_post_or_raise(session, post_id)
    post.like_count += 1
    session.commit()
    session.refresh(post)
    return ApiResponse(data=PostLikeResponse(id=post.id, like_count=post.like_count), message="좋아요 등록 성공")


@router.delete("/{post_id}/like", response_model=ApiResponse[PostLikeResponse])
def unlike_post(post_id: int, session: Session = Depends(get_db)) -> ApiResponse[PostLikeResponse]:
    post = get_post_or_raise(session, post_id)
    post.like_count = max(0, post.like_count - 1)
    session.commit()
    session.refresh(post)
    return ApiResponse(data=PostLikeResponse(id=post.id, like_count=post.like_count), message="좋아요 취소 성공")


@router.post("/{post_id}/image", response_model=ApiResponse[PostImageResponse])
async def upload_post_image(
    post_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_db),
) -> ApiResponse[PostImageResponse]:
    post = get_post_or_raise(session, post_id)
    extension = CONTENT_TYPE_EXTENSIONS.get(file.content_type)
    if not extension:
        raise ApiError(400, "이미지 파일(JPEG, PNG, WEBP, GIF)만 업로드할 수 있습니다.", "INVALID_IMAGE_TYPE")

    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE:
        raise ApiError(400, "이미지 용량은 5MB를 초과할 수 없습니다.", "IMAGE_TOO_LARGE")

    upload_dir = get_settings().resolved_uploads_root
    upload_dir.mkdir(parents=True, exist_ok=True)

    if post.image_url:
        old_path = upload_dir / Path(post.image_url).name
        old_path.unlink(missing_ok=True)

    filename = f"{uuid.uuid4().hex}{extension}"
    (upload_dir / filename).write_bytes(contents)

    post.image_url = f"/uploads/{filename}"
    session.commit()
    session.refresh(post)
    return ApiResponse(data=PostImageResponse(id=post.id, image_url=post.image_url), message="이미지 업로드 성공")
