from __future__ import annotations

import argparse
import html
import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Any, Callable, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEOUL_OUTPUT = PROJECT_ROOT / "data" / "서울" / "서울_음식점.json"
DEFAULT_BUSAN_OUTPUT = PROJECT_ROOT / "data" / "부산" / "부산_음식점.json"

SEOUL_SERVICE = "LOCALDATA_072404"
SEOUL_ENDPOINT = "http://openapi.seoul.go.kr:8088"
SEOUL_SOURCE = "서울특별시 일반음식점 인허가 정보"
SEOUL_SOURCE_URL = "https://data.seoul.go.kr/dataList/OA-16094/A/1/datasetView.do"
SEOUL_LICENSE = "공공누리 제1유형 (출처 표시)"

BUSAN_SERVICE = "getFoodKr"
BUSAN_ENDPOINT = "https://apis.data.go.kr/6260000/FoodService/getFoodKr"
BUSAN_SOURCE = "부산광역시 부산맛집정보 서비스"
BUSAN_SOURCE_URL = "https://www.data.go.kr/data/15063472/openapi.do"
BUSAN_LICENSE = "이용허락범위 제한 없음"


class CollectionError(RuntimeError):
    """A public-data request or transformation failed."""


class CoordinateTransformer(Protocol):
    def transform(self, x: float, y: float) -> tuple[float, float]: ...


JsonFetcher = Callable[[str], dict[str, Any]]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _number(value: Any) -> float | None:
    try:
        return float(_text(value)) if _text(value) else None
    except (TypeError, ValueError):
        return None


def _clean_description(value: Any) -> str:
    text = html.unescape(_text(value))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _coordinate_text(value: Any, minimum: float, maximum: float) -> str:
    number = _number(value)
    if number is None or not minimum <= number <= maximum:
        return ""
    return f"{number:.7f}".rstrip("0").rstrip(".")


def _request_json(url: str) -> dict[str, Any]:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "LocalHubDataCollector/1.0",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except (
        HTTPError,
        URLError,
        TimeoutError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ):
        # Do not include the requested URL because the API key is part of it.
        raise CollectionError("공공데이터 API 요청에 실패했습니다.") from None


def _seoul_url(api_key: str, start: int, end: int) -> str:
    encoded_key = quote(api_key.strip(), safe="")
    # Optional path arguments are APVPERMYMD, TRDSTATEGBN, BPLCNM in order.
    # A single encoded blank skips APVPERMYMD so that 01 filters active stores.
    return (
        f"{SEOUL_ENDPOINT}/{encoded_key}/json/{SEOUL_SERVICE}/{start}/{end}"
        "/%20/01/"
    )


def _seoul_transformer() -> CoordinateTransformer:
    try:
        from pyproj import Transformer
    except ImportError as error:
        raise CollectionError(
            "서울 좌표 변환에 pyproj가 필요합니다. "
            "backend/requirements-data.txt를 설치해 주세요."
        ) from error
    return Transformer.from_crs("EPSG:5174", "EPSG:4326", always_xy=True)


def normalize_seoul_item(
    row: dict[str, Any], transformer: CoordinateTransformer
) -> dict[str, str] | None:
    if _text(row.get("TRDSTATEGBN")) != "01":
        return None
    detailed_state = _text(row.get("DTLSTATEGBN"))
    if detailed_state and detailed_state != "01":
        return None

    management_number = _text(row.get("MGTNO"))
    name = _text(row.get("BPLCNM"))
    if not management_number or not name:
        return None

    longitude = ""
    latitude = ""
    x = _number(row.get("X"))
    y = _number(row.get("Y"))
    if x is not None and y is not None:
        try:
            converted_longitude, converted_latitude = transformer.transform(x, y)
        except (TypeError, ValueError, RuntimeError):
            pass
        else:
            if 124 <= converted_longitude <= 132 and 33 <= converted_latitude <= 39:
                longitude = f"{converted_longitude:.7f}"
                latitude = f"{converted_latitude:.7f}"

    details: list[str] = []
    business_type = _text(row.get("UPTAENM")) or _text(row.get("SNTUPTAENM"))
    traditional_menu = _text(row.get("JTUPSOMAINEDF"))
    if business_type:
        details.append(f"업태: {business_type}")
    if traditional_menu:
        details.append(f"주요 음식: {traditional_menu}")

    return {
        "addr1": _text(row.get("RDNWHLADDR")) or _text(row.get("SITEWHLADDR")),
        "addr2": "",
        "contentid": management_number,
        "contenttypeid": "39",
        "firstimage": "",
        "mapx": longitude,
        "mapy": latitude,
        "tel": _text(row.get("SITETEL")),
        "title": name,
        "description": " · ".join(details),
    }


def collect_seoul(
    api_key: str,
    output_path: Path = DEFAULT_SEOUL_OUTPUT,
    *,
    max_items: int | None = 1000,
    page_size: int = 1000,
    fetch_json: JsonFetcher | None = None,
    transformer: CoordinateTransformer | None = None,
    collected_at: str | None = None,
) -> dict[str, Any]:
    if not api_key.strip():
        raise CollectionError("SEOUL_OPEN_DATA_API_KEY가 비어 있습니다.")
    if max_items is not None and max_items < 1:
        raise CollectionError("max_items는 1 이상이어야 합니다.")
    if not 1 <= page_size <= 1000:
        raise CollectionError("page_size는 1에서 1000 사이여야 합니다.")

    fetch = fetch_json or _request_json
    coordinate_transformer = transformer or _seoul_transformer()
    items: list[dict[str, str]] = []
    total_available = 0
    scanned_rows = 0
    start = 1

    while True:
        end = start + page_size - 1
        payload = fetch(_seoul_url(api_key, start, end))
        root = payload.get(SEOUL_SERVICE)
        if not isinstance(root, dict):
            raise CollectionError("서울 API 응답 형식을 확인할 수 없습니다.")

        result = root.get("RESULT") or {}
        if _text(result.get("CODE")) != "INFO-000":
            raise CollectionError(
                f"서울 API가 오류를 반환했습니다: {_text(result.get('MESSAGE')) or '알 수 없는 오류'}"
            )

        try:
            total_available = int(root.get("list_total_count") or 0)
        except (TypeError, ValueError) as error:
            raise CollectionError("서울 API 전체 건수를 해석할 수 없습니다.") from error

        rows = root.get("row") or []
        if isinstance(rows, dict):
            rows = [rows]
        if not isinstance(rows, list):
            raise CollectionError("서울 API 음식점 목록 형식이 올바르지 않습니다.")

        for row in rows:
            scanned_rows += 1
            if not isinstance(row, dict):
                continue
            item = normalize_seoul_item(row, coordinate_transformer)
            if item is not None:
                items.append(item)
                if max_items is not None and len(items) >= max_items:
                    break

        if (max_items is not None and len(items) >= max_items) or not rows:
            break
        if start + len(rows) > total_available:
            break
        start += len(rows)

    result_payload: dict[str, Any] = {
        "region": "서울",
        "contentType": "음식점",
        "contentTypeId": 39,
        "sourceIdPrefix": "SEOUL_LOCALDATA",
        "source": SEOUL_SOURCE,
        "sourceUrl": SEOUL_SOURCE_URL,
        "license": SEOUL_LICENSE,
        "collectedAt": collected_at or date.today().isoformat(),
        "totalAvailable": total_available,
        "truncated": scanned_rows < total_available,
        "sync": True,
        "total": len(items),
        "items": items,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result_payload


def _busan_url(api_key: str, page: int, page_size: int) -> str:
    # The portal shows both encoded and decoded keys. Normalize either form,
    # then urlencode once so '+' and '/' are transmitted without corruption.
    decoded_key = unquote(api_key.strip())
    query = urlencode(
        {
            "serviceKey": decoded_key,
            "pageNo": page,
            "numOfRows": page_size,
            "resultType": "json",
        }
    )
    return f"{BUSAN_ENDPOINT}?{query}"


def normalize_busan_item(item: dict[str, Any]) -> dict[str, str] | None:
    sequence = _text(item.get("UC_SEQ"))
    name = _text(item.get("MAIN_TITLE"))
    if not sequence or not name:
        return None

    address = _text(item.get("ADDR1"))
    if address.startswith("부산 "):
        address = f"부산광역시 {address.removeprefix('부산 ').strip()}"
    elif address and not address.startswith("부산광역시"):
        address = f"부산광역시 {address}"

    details: list[str] = []
    subtitle = _clean_description(item.get("SUBTITLE"))
    place = _clean_description(item.get("PLACE"))
    menu = _clean_description(item.get("RPRSNTV_MENU"))
    hours = _clean_description(item.get("USAGE_DAY_WEEK_AND_TIME"))
    contents = _clean_description(item.get("ITEMCNTNTS"))
    if subtitle and subtitle != name:
        details.append(subtitle)
    if place:
        details.append(f"장소: {place}")
    if menu:
        details.append(f"대표 메뉴: {menu}")
    if hours:
        details.append(f"운영 시간: {hours}")
    if contents:
        details.append(contents)

    return {
        "addr1": address,
        "addr2": _text(item.get("ADDR2")),
        "contentid": sequence,
        "contenttypeid": "39",
        "firstimage": _text(item.get("MAIN_IMG_NORMAL"))
        or _text(item.get("MAIN_IMG_THUMB")),
        "mapx": _coordinate_text(item.get("LNG"), 124, 132),
        "mapy": _coordinate_text(item.get("LAT"), 33, 39),
        "tel": _text(item.get("CNTCT_TEL")),
        "title": name,
        "description": " · ".join(details),
    }


def collect_busan(
    api_key: str,
    output_path: Path = DEFAULT_BUSAN_OUTPUT,
    *,
    page_size: int = 100,
    fetch_json: JsonFetcher | None = None,
    collected_at: str | None = None,
) -> dict[str, Any]:
    if not api_key.strip():
        raise CollectionError("BUSAN_FOOD_API_KEY가 비어 있습니다.")
    if not 1 <= page_size <= 1000:
        raise CollectionError("page_size는 1에서 1000 사이여야 합니다.")

    fetch = fetch_json or _request_json
    items: list[dict[str, str]] = []
    total_available = 0
    scanned_rows = 0
    page = 1

    while True:
        payload = fetch(_busan_url(api_key, page, page_size))
        root = payload.get(BUSAN_SERVICE)
        if not isinstance(root, dict):
            raise CollectionError("부산 API 응답 형식을 확인할 수 없습니다.")

        header = root.get("header") or {}
        if _text(header.get("code")) != "00":
            raise CollectionError(
                f"부산 API가 오류를 반환했습니다: {_text(header.get('message')) or '알 수 없는 오류'}"
            )

        try:
            total_available = int(root.get("totalCount") or 0)
        except (TypeError, ValueError) as error:
            raise CollectionError("부산 API 전체 건수를 해석할 수 없습니다.") from error

        rows = root.get("item") or []
        if isinstance(rows, dict):
            rows = [rows]
        if not isinstance(rows, list):
            raise CollectionError("부산 API 맛집 목록 형식이 올바르지 않습니다.")

        for row in rows:
            scanned_rows += 1
            if not isinstance(row, dict):
                continue
            item = normalize_busan_item(row)
            if item is not None:
                items.append(item)

        if not rows or scanned_rows >= total_available:
            break
        page += 1

    result_payload: dict[str, Any] = {
        "region": "부산",
        "contentType": "음식점",
        "contentTypeId": 39,
        "sourceIdPrefix": "BUSAN_FOOD",
        "source": BUSAN_SOURCE,
        "sourceUrl": BUSAN_SOURCE_URL,
        "license": BUSAN_LICENSE,
        "collectedAt": collected_at or date.today().isoformat(),
        "totalAvailable": total_available,
        "truncated": scanned_rows < total_available,
        "sync": True,
        "total": len(items),
        "items": items,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result_payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="서울·부산 음식점 공공데이터를 In지도 JSON으로 수집합니다."
    )
    subparsers = parser.add_subparsers(dest="provider", required=True)
    seoul_parser = subparsers.add_parser("seoul", help="서울 영업중 일반음식점 수집")
    seoul_parser.add_argument("--output", type=Path, default=DEFAULT_SEOUL_OUTPUT)
    seoul_parser.add_argument(
        "--max-items",
        type=int,
        default=1000,
        help="저장할 최대 건수(기본 1000)",
    )
    busan_parser = subparsers.add_parser("busan", help="부산 맛집 전체 수집")
    busan_parser.add_argument("--output", type=Path, default=DEFAULT_BUSAN_OUTPUT)
    busan_parser.add_argument(
        "--page-size",
        type=int,
        default=100,
        help="API 한 번에 요청할 건수(기본 100)",
    )
    return parser


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    args = build_parser().parse_args()
    try:
        if args.provider == "seoul":
            payload = collect_seoul(
                os.getenv("SEOUL_OPEN_DATA_API_KEY", ""),
                args.output,
                max_items=args.max_items,
            )
        elif args.provider == "busan":
            payload = collect_busan(
                os.getenv("BUSAN_FOOD_API_KEY", ""),
                args.output,
                page_size=args.page_size,
            )
        else:  # pragma: no cover - argparse rejects unknown providers
            raise CollectionError("지원하지 않는 데이터 제공자입니다.")
    except CollectionError as error:
        print(f"수집 실패: {error}")
        return 1

    print(
        f"{args.provider} 음식점 {payload['total']:,}건 저장: {args.output} "
        f"(전체 {payload['totalAvailable']:,}건)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
