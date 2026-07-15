from dataclasses import dataclass

from openai import AsyncOpenAI, RateLimitError
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.errors import ApiError
from app.models import Place, Post
from app.schemas import ChatHistoryItem, ChatMatchedItem, RegionCode


CATEGORY_KEYWORDS = {
    "RESTAURANT": ("맛집", "음식", "식당", "먹거리"),
    "TOURIST": ("관광", "여행", "명소", "가볼만"),
    "FESTIVAL": ("축제", "공연", "행사"),
    "CULTURE": ("문화", "박물관", "미술관", "전시"),
    "SHOPPING": ("쇼핑", "시장"),
    "ACCOMMODATION": ("숙박", "호텔", "잠잘"),
}


@dataclass
class SearchContext:
    prompt_text: str
    matched_items: list[ChatMatchedItem]


def _detected_category(message: str) -> str | None:
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in message for keyword in keywords):
            return category
    return None


def find_context(
    session: Session,
    message: str,
    region: RegionCode | None = None,
    limit: int = 5,
) -> SearchContext:
    category = _detected_category(message)
    search_term = f"%{message.strip()}%"
    place_query = select(Place)
    post_query = select(Post)

    if region:
        place_query = place_query.where(Place.region == region.value)
        post_query = post_query.where(Post.region == region.value)

    if category:
        place_query = place_query.where(Place.category == category)
        if category in {"RESTAURANT", "TOURIST", "FESTIVAL", "CULTURE", "SHOPPING", "ACCOMMODATION"}:
            post_query = post_query.where(Post.category == category)
    else:
        place_query = place_query.where(
            or_(
                Place.name.ilike(search_term),
                Place.address.ilike(search_term),
                Place.description.ilike(search_term),
            )
        )
        post_query = post_query.where(
            or_(Post.title.ilike(search_term), Post.content.ilike(search_term))
        )

    places = session.scalars(place_query.limit(limit)).all()
    remaining = max(0, limit - len(places))
    posts = session.scalars(post_query.order_by(Post.created_at.desc()).limit(remaining)).all()

    lines: list[str] = []
    matched_items: list[ChatMatchedItem] = []
    for place in places:
        lines.append(
            f"[장소 #{place.id}] {place.name} | {place.category} | "
            f"주소: {place.address or '정보 없음'} | 소개: {place.description or '정보 없음'}"
        )
        matched_items.append(
            ChatMatchedItem(
                type="PLACE",
                id=place.id,
                title=place.name,
                category=place.category,
                region=place.region,
            )
        )
    for post in posts:
        lines.append(
            f"[게시글 #{post.id}] {post.title} | {post.category} | "
            f"작성자: {post.author} | 내용: {post.content}"
        )
        matched_items.append(
            ChatMatchedItem(
                type="POST",
                id=post.id,
                title=post.title,
                category=post.category,
                region=post.region,
            )
        )

    return SearchContext(prompt_text="\n".join(lines), matched_items=matched_items)


def fallback_answer(context: SearchContext) -> str:
    if not context.matched_items:
        return "제공된 서울 지역 정보와 게시글에서 질문에 맞는 근거를 찾지 못했어요. 다른 키워드로 질문해 주세요."
    titles = ", ".join(item.title for item in context.matched_items)
    return f"현재 제공된 LocalHub 데이터에서는 {titles} 정보를 확인할 수 있어요. 자세한 내용은 카드나 게시글에서 확인해 주세요."


async def create_answer(
    settings: Settings,
    question: str,
    history: list[ChatHistoryItem],
    context: SearchContext,
) -> str:
    if not settings.openai_api_key:
        return fallback_answer(context)

    system_prompt = (
        "당신은 서울 지역 정보 도우미 LocalHub입니다. 아래 제공 데이터 안에서만 한국어로 답하세요. "
        "근거가 없으면 정보가 없다고 명확히 말하세요. 게시글의 비밀번호나 추측한 정보는 절대 언급하지 마세요.\n\n"
        f"제공 데이터:\n{context.prompt_text or '관련 데이터 없음'}"
    )
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(item.model_dump() for item in history[-10:])
    messages.append({"role": "user", "content": question})

    try:
        response = await AsyncOpenAI(api_key=settings.openai_api_key).chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content or fallback_answer(context)
    except RateLimitError as error:
        raise ApiError(429, "OpenAI API 요청 한도를 초과했습니다.", "OPENAI_RATE_LIMIT") from error
    except ApiError:
        raise
    except Exception as error:
        raise ApiError(502, "챗봇 응답 생성에 실패했습니다.", "OPENAI_REQUEST_FAILED") from error
