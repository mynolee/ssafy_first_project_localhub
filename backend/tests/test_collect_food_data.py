import json
from pathlib import Path

import pytest

from tools.collect_food_data import CollectionError, collect_seoul, normalize_seoul_item


class FakeTransformer:
    def transform(self, x: float, y: float) -> tuple[float, float]:
        assert (x, y) == (198810.7659, 448800.9733)
        return 126.9823456, 37.5432109


def test_normalize_seoul_item_maps_active_restaurant() -> None:
    item = normalize_seoul_item(
        {
            "MGTNO": "3020000-101-2001-00001",
            "TRDSTATEGBN": "01",
            "DTLSTATEGBN": "01",
            "SITETEL": "02-1234-5678",
            "SITEWHLADDR": "서울특별시 용산구 후암동 1",
            "RDNWHLADDR": "서울특별시 용산구 후암로 1",
            "BPLCNM": "서울식당",
            "UPTAENM": "한식",
            "JTUPSOMAINEDF": "비빔밥",
            "X": "198810.7659",
            "Y": "448800.9733",
        },
        FakeTransformer(),
    )

    assert item == {
        "addr1": "서울특별시 용산구 후암로 1",
        "addr2": "",
        "contentid": "3020000-101-2001-00001",
        "contenttypeid": "39",
        "firstimage": "",
        "mapx": "126.9823456",
        "mapy": "37.5432109",
        "tel": "02-1234-5678",
        "title": "서울식당",
        "description": "업태: 한식 · 주요 음식: 비빔밥",
    }


def test_normalize_seoul_item_ignores_closed_restaurant() -> None:
    assert (
        normalize_seoul_item(
            {"MGTNO": "closed", "BPLCNM": "폐업식당", "TRDSTATEGBN": "03"},
            FakeTransformer(),
        )
        is None
    )


def test_collect_seoul_paginates_and_records_truncation(tmp_path: Path) -> None:
    requested_urls: list[str] = []

    def fake_fetch(url: str) -> dict:
        requested_urls.append(url)
        page = len(requested_urls)
        rows = [
            {
                "MGTNO": f"id-{page}-{index}",
                "BPLCNM": f"식당 {page}-{index}",
                "TRDSTATEGBN": "01",
                "DTLSTATEGBN": "01",
            }
            for index in range(2)
        ]
        return {
            "LOCALDATA_072404": {
                "list_total_count": 5,
                "RESULT": {"CODE": "INFO-000", "MESSAGE": "정상 처리되었습니다"},
                "row": rows,
            }
        }

    output = tmp_path / "서울_음식점.json"
    payload = collect_seoul(
        "secret-key",
        output,
        max_items=3,
        page_size=2,
        fetch_json=fake_fetch,
        transformer=FakeTransformer(),
        collected_at="2026-07-16",
    )

    assert len(requested_urls) == 2
    assert all("secret-key" in url for url in requested_urls)
    assert all("/%20/01/" in url for url in requested_urls)
    assert payload["total"] == 3
    assert payload["totalAvailable"] == 5
    assert payload["truncated"] is True
    assert json.loads(output.read_text(encoding="utf-8")) == payload


def test_collect_seoul_rejects_missing_key_without_leaking_value(tmp_path: Path) -> None:
    with pytest.raises(CollectionError, match="SEOUL_OPEN_DATA_API_KEY"):
        collect_seoul("", tmp_path / "unused.json", transformer=FakeTransformer())
