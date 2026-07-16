import json
from pathlib import Path

import pytest

from tools.collect_food_data import (
    CollectionError,
    collect_busan,
    collect_seoul,
    normalize_busan_item,
    normalize_seoul_item,
)


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


def test_normalize_busan_item_maps_food_service_fields() -> None:
    item = normalize_busan_item(
        {
            "UC_SEQ": 70,
            "MAIN_TITLE": "만드리곤드레밥",
            "SUBTITLE": "강서구의 건강한 한 끼",
            "PLACE": "강서구",
            "LAT": 35.177387,
            "LNG": 128.95245,
            "ADDR1": "강서구 공항앞길85번길 13",
            "ADDR2": "1층",
            "CNTCT_TEL": "051-941-3669",
            "RPRSNTV_MENU": "돌솥곤드레정식",
            "USAGE_DAY_WEEK_AND_TIME": "매일 11:00~20:00",
            "MAIN_IMG_NORMAL": "https://example.com/food.jpg",
            "ITEMCNTNTS": "<p>부산의 향토 식재료를 사용합니다.</p>",
        }
    )

    assert item is not None
    assert item["contentid"] == "70"
    assert item["title"] == "만드리곤드레밥"
    assert item["addr1"] == "부산광역시 강서구 공항앞길85번길 13"
    assert item["mapx"] == "128.95245"
    assert item["mapy"] == "35.177387"
    assert item["firstimage"] == "https://example.com/food.jpg"
    assert "대표 메뉴: 돌솥곤드레정식" in item["description"]
    assert "<p>" not in item["description"]


def test_collect_busan_handles_list_and_single_item_pages(tmp_path: Path) -> None:
    requested_urls: list[str] = []

    def fake_fetch(url: str) -> dict:
        requested_urls.append(url)
        page = len(requested_urls)
        rows: list[dict] | dict
        if page == 1:
            rows = [
                {"UC_SEQ": 1, "MAIN_TITLE": "첫 식당"},
                {"UC_SEQ": 2, "MAIN_TITLE": "둘째 식당"},
            ]
        else:
            rows = {"UC_SEQ": 3, "MAIN_TITLE": "셋째 식당"}
        return {
            "getFoodKr": {
                "header": {"code": "00", "message": "NORMAL_CODE"},
                "item": rows,
                "numOfRows": 2,
                "pageNo": page,
                "totalCount": 3,
            }
        }

    output = tmp_path / "부산_음식점.json"
    payload = collect_busan(
        "encoded%2Bkey%2Fvalue%3D",
        output,
        page_size=2,
        fetch_json=fake_fetch,
        collected_at="2026-07-16",
    )

    assert len(requested_urls) == 2
    assert "serviceKey=encoded%2Bkey%2Fvalue%3D" in requested_urls[0]
    assert "pageNo=2" in requested_urls[1]
    assert payload["total"] == 3
    assert payload["totalAvailable"] == 3
    assert payload["truncated"] is False
    assert json.loads(output.read_text(encoding="utf-8")) == payload


def test_collect_busan_rejects_missing_key(tmp_path: Path) -> None:
    with pytest.raises(CollectionError, match="BUSAN_FOOD_API_KEY"):
        collect_busan("", tmp_path / "unused.json")
