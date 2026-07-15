from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database import get_db
from app.schemas import ApiResponse, ChatRequest, ChatResponse
from app.services.chat_service import create_answer, find_context


router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ApiResponse[ChatResponse])
async def chat(
    request: ChatRequest,
    session: Session = Depends(get_db),
) -> ApiResponse[ChatResponse]:
    context = find_context(session, request.message, request.region)
    answer = await create_answer(get_settings(), request.message, request.history, context)
    return ApiResponse(
        data=ChatResponse(answer=answer, matched_items=context.matched_items),
        message="챗봇 응답 생성 성공",
    )
