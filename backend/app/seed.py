import json
from pathlib import Path
from typing import Any

from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from app.models import Place


REGION_CODES = {
    "서울": "SEOUL",
    "대전_충청권": "DAEJEON_CHUNGCHEONG",
    "구미_경북권": "GUMI_GYEONGBUK",
    "광주_전라권": "GWANGJU_JEOLLA",
    "부산": "BUSAN",
}

CATEGORY_CODES = {
    "12": "TOURIST",
    "14": "CULTURE",
    "15": "FESTIVAL",
    "25": "COURSE",
    "28": "LEISURE",
    "32": "ACCOMMODATION",
    "38": "SHOPPING",
    "39": "RESTAURANT",
}


def _optional_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _is_valid_place_name(name: str) -> bool:
    """Check if a place name seems valid and not corrupted."""
    if not name:
        return False
    # Filter out suspicious names with unusual patterns
    suspicious_patterns = [
        '국호',  # 국호 37호선 같은 이상한 항목
        '국도',  # 국도 37호선 같은 도로명
        '급치산',  # 이상한 장소명
        '037',  # 라인 번호 같은 항목
        '9999',  # 플레이스홀더
    ]
    for pattern in suspicious_patterns:
        if pattern in name:
            return False
    # Check for reasonable length
    if len(name) < 2 or len(name) > 100:
        return False
    return True


def _optional_float(value: Any) -> float | None:
    try:
        return float(value) if str(value or "").strip() else None
    except (TypeError, ValueError):
        return None


def _tour_api_records(data_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for json_file in sorted(data_root.glob("**/*.json")):
        payload = json.loads(json_file.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or "items" not in payload:
            continue
        region = REGION_CODES.get(str(payload.get("region")))
        category = CATEGORY_CODES.get(str(payload.get("contentTypeId")))
        if not region or not category:
            continue
        for item in payload.get("items", []):
            content_id = _optional_text(item.get("contentid"))
            title = _optional_text(item.get("title"))
            if not content_id or not title or not _is_valid_place_name(title):
                continue
            address_parts = filter(
                None,
                (_optional_text(item.get("addr1")), _optional_text(item.get("addr2"))),
            )
            records.append(
                {
                    "source_id": f"{region}:{content_id}",
                    "region": region,
                    "name": title,
                    "category": category,
                    "address": " ".join(address_parts) or None,
                    "latitude": _optional_float(item.get("mapy")),
                    "longitude": _optional_float(item.get("mapx")),
                    "description": None,
                    "image_url": _optional_text(item.get("firstimage")),
                    "phone": _optional_text(item.get("tel")),
                    "source": "한국관광공사 Tour API 4.0",
                    "license": "공공누리 제3유형 (출처 표시 + 변경 금지)",
                    "collected_at": "2026-07-11",
                }
            )
    return records


def _legacy_records(data_root: Path) -> list[dict[str, Any]]:
    legacy_file = data_root / "seoul_places.json"
    if not legacy_file.exists():
        return []
    records = json.loads(legacy_file.read_text(encoding="utf-8"))
    for record in records:
        record.setdefault("region", "SEOUL")
    return records


def seed_places(session: Session, data_root: Path) -> int:
    records = _tour_api_records(data_root) or _legacy_records(data_root)
    if not records:
        return 0

    # Remove corrupted records from database
    from app.models import Place
    suspicious_names = ['국호', '국도', '급치산', '037', '9999']
    for pattern in suspicious_names:
        session.execute(delete(Place).where(Place.name.like(f"%{pattern}%")))
    
    session.execute(delete(Place).where(Place.source_id.like("SAMPLE-%")))
    existing_ids = set(session.scalars(select(Place.source_id)))
    new_records = [record for record in records if record["source_id"] not in existing_ids]
    if new_records:
        session.execute(insert(Place), new_records)
    session.commit()
    return len(new_records)
