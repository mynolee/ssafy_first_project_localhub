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

DEFAULT_SOURCE = "한국관광공사 Tour API 4.0"
DEFAULT_LICENSE = "공공누리 제3유형 (출처 표시 + 변경 금지)"
DEFAULT_COLLECTED_AT = "2026-07-11"


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


def _data_records(
    data_root: Path,
) -> tuple[list[dict[str, Any]], dict[str, set[str]]]:
    records: list[dict[str, Any]] = []
    synchronized_source_ids: dict[str, set[str]] = {}
    for json_file in sorted(data_root.glob("**/*.json")):
        payload = json.loads(json_file.read_text(encoding="utf-8"))
        if not isinstance(payload, dict) or "items" not in payload:
            continue
        region = REGION_CODES.get(str(payload.get("region")))
        category = CATEGORY_CODES.get(str(payload.get("contentTypeId")))
        if not region or not category:
            continue
        source_id_prefix = _optional_text(payload.get("sourceIdPrefix")) or region
        source = _optional_text(payload.get("source")) or DEFAULT_SOURCE
        license_name = _optional_text(payload.get("license")) or DEFAULT_LICENSE
        collected_at = _optional_text(payload.get("collectedAt")) or DEFAULT_COLLECTED_AT
        if payload.get("sync") is True:
            synchronized_source_ids.setdefault(source_id_prefix, set())
        for item in payload.get("items", []):
            content_id = _optional_text(item.get("contentid"))
            title = _optional_text(item.get("title"))
            if not content_id or not title or not _is_valid_place_name(title):
                continue
            source_id = f"{source_id_prefix}:{content_id}"
            if source_id_prefix in synchronized_source_ids:
                synchronized_source_ids[source_id_prefix].add(source_id)
            address_parts = filter(
                None,
                (_optional_text(item.get("addr1")), _optional_text(item.get("addr2"))),
            )
            records.append(
                {
                    "source_id": source_id,
                    "region": region,
                    "name": title,
                    "category": category,
                    "address": " ".join(address_parts) or None,
                    "latitude": _optional_float(item.get("mapy")),
                    "longitude": _optional_float(item.get("mapx")),
                    "description": _optional_text(item.get("description")),
                    "image_url": _optional_text(item.get("firstimage")),
                    "phone": _optional_text(item.get("tel")),
                    "source": source,
                    "license": license_name,
                    "collected_at": collected_at,
                }
            )
    return records, synchronized_source_ids


def _legacy_records(data_root: Path) -> list[dict[str, Any]]:
    legacy_file = data_root / "seoul_places.json"
    if not legacy_file.exists():
        return []
    records = json.loads(legacy_file.read_text(encoding="utf-8"))
    for record in records:
        record.setdefault("region", "SEOUL")
    return records


def seed_places(session: Session, data_root: Path) -> int:
    records, synchronized_source_ids = _data_records(data_root)
    if not records:
        records = _legacy_records(data_root)
        if not records and not synchronized_source_ids:
            return 0

    # Remove corrupted records from database
    suspicious_names = ['국호', '국도', '급치산', '037', '9999']
    for pattern in suspicious_names:
        session.execute(delete(Place).where(Place.name.like(f"%{pattern}%")))

    session.execute(delete(Place).where(Place.source_id.like("SAMPLE-%")))
    existing_places = {
        place.source_id: place for place in session.scalars(select(Place)).all()
    }

    for prefix, desired_ids in synchronized_source_ids.items():
        namespace = f"{prefix}:"
        for source_id, place in existing_places.items():
            if source_id.startswith(namespace) and source_id not in desired_ids:
                session.delete(place)

    new_records: list[dict[str, Any]] = []
    for record in records:
        existing = existing_places.get(record["source_id"])
        if existing is None:
            new_records.append(record)
            continue
        for field, value in record.items():
            if field != "source_id" and getattr(existing, field) != value:
                setattr(existing, field, value)

    if new_records:
        session.execute(insert(Place), new_records)
    session.commit()
    return len(new_records)
