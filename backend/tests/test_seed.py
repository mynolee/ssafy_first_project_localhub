import json
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Place
from app.seed import seed_places


def _place(source_id: str, name: str) -> Place:
    return Place(
        source_id=source_id,
        region="SEOUL",
        name=name,
        category="RESTAURANT",
        source="오래된 출처",
    )


def test_seed_uses_payload_metadata_updates_and_synchronizes(tmp_path: Path) -> None:
    payload = {
        "region": "서울",
        "contentType": "음식점",
        "contentTypeId": 39,
        "sourceIdPrefix": "SEOUL_LOCALDATA",
        "source": "서울특별시 일반음식점 인허가 정보",
        "license": "공공누리 제1유형 (출처 표시)",
        "collectedAt": "2026-07-16",
        "sync": True,
        "items": [
            {
                "contentid": "current",
                "title": "현재 식당",
                "contenttypeid": "39",
                "addr1": "서울특별시 중구 세종대로 110",
                "addr2": "",
                "mapx": "126.9780",
                "mapy": "37.5665",
                "firstimage": "",
                "tel": "02-120",
                "description": "업태: 한식",
            },
            {
                "contentid": "new",
                "title": "새 식당",
                "contenttypeid": "39",
            },
        ],
    }
    data_file = tmp_path / "서울" / "서울_음식점.json"
    data_file.parent.mkdir()
    data_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all(
            [
                _place("SEOUL_LOCALDATA:current", "수정 전 이름"),
                _place("SEOUL_LOCALDATA:closed", "폐업 식당"),
            ]
        )
        session.commit()

        inserted = seed_places(session, tmp_path)
        places = {
            place.source_id: place
            for place in session.scalars(select(Place).order_by(Place.source_id))
        }

    assert inserted == 1
    assert set(places) == {"SEOUL_LOCALDATA:current", "SEOUL_LOCALDATA:new"}
    current = places["SEOUL_LOCALDATA:current"]
    assert current.name == "현재 식당"
    assert current.description == "업태: 한식"
    assert current.source == "서울특별시 일반음식점 인허가 정보"
    assert current.license == "공공누리 제1유형 (출처 표시)"
    assert current.collected_at == "2026-07-16"


def test_seed_empty_sync_snapshot_removes_previous_provider_rows(tmp_path: Path) -> None:
    payload = {
        "region": "서울",
        "contentType": "음식점",
        "contentTypeId": 39,
        "sourceIdPrefix": "SEOUL_LOCALDATA",
        "sync": True,
        "items": [],
    }
    data_file = tmp_path / "empty.json"
    data_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(_place("SEOUL_LOCALDATA:old", "이전 식당"))
        session.commit()

        inserted = seed_places(session, tmp_path)
        remaining = session.scalars(select(Place)).all()

    assert inserted == 0
    assert remaining == []
