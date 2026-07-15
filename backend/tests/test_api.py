import os
import asyncio
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["OPENAI_API_KEY"] = ""
os.environ["DATA_ROOT"] = str(Path(__file__).parents[1] / "app" / "data")

from httpx import ASGITransport, AsyncClient

from app.main import app


def test_places_are_seeded() -> None:
    async def scenario() -> None:
        async with app.router.lifespan_context(app):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/api/places?region=SEOUL&category=TOURIST")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]
        assert all(place["category"] == "TOURIST" for place in body["data"])

    asyncio.run(scenario())


def test_local_frontend_origins_are_allowed() -> None:
    async def scenario() -> None:
        async with app.router.lifespan_context(app):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                for origin in ("http://localhost:5173", "http://127.0.0.1:5173"):
                    response = await client.get("/api/posts", headers={"Origin": origin})
                    assert response.status_code == 200
                    assert response.headers["access-control-allow-origin"] == origin

    asyncio.run(scenario())


def test_post_crud_and_password_protection() -> None:
    async def scenario() -> None:
        async with app.router.lifespan_context(app):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                created = await client.post(
                    "/api/posts",
                    json={
                        "category": "RESTAURANT",
                        "region": "SEOUL",
                        "title": "테스트 맛집",
                        "content": "테스트 게시글입니다.",
                        "author": "테스터",
                        "password": "1234",
                    },
                )
                assert created.status_code == 201
                post_id = created.json()["data"]["id"]
                assert "password" not in created.json()["data"]

                denied = await client.patch(
                    f"/api/posts/{post_id}",
                    json={"password": "9999", "title": "수정 실패"},
                )
                assert denied.status_code == 403
                assert denied.json()["error"]["code"] == "INVALID_PASSWORD"

                updated = await client.patch(
                    f"/api/posts/{post_id}",
                    json={"password": "1234", "title": "수정 성공"},
                )
                assert updated.status_code == 200
                assert updated.json()["data"]["title"] == "수정 성공"

                invalid = await client.patch(
                    f"/api/posts/{post_id}",
                    json={"password": "1234"},
                )
                assert invalid.status_code == 422
                assert invalid.json()["error"]["code"] == "VALIDATION_ERROR"

                deleted = await client.request(
                    "DELETE",
                    f"/api/posts/{post_id}",
                    json={"password": "1234"},
                )
                assert deleted.status_code == 200
                assert deleted.json()["data"]["id"] == post_id

    asyncio.run(scenario())


def test_chat_uses_local_fallback_without_api_key() -> None:
    async def scenario() -> None:
        async with app.router.lifespan_context(app):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    "/api/chat", json={"message": "관광지 추천해줘", "history": []}
                )

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["answer"]
        assert body["data"]["matchedItems"]

    asyncio.run(scenario())
