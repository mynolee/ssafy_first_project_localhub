# In지도

전국 5개 권역의 공공 관광 데이터를 지도에서 탐색하고, 익명 게시판과 AI 챗봇을 함께 이용하는 Vue 3 기반 SPA입니다.

> SSAFY 광주 4반 5팀 · 2026<br>
> 문서 기준: 현재 `main` 구현 및 기능 명세서 v1.1

## 서비스 바로가기

| 구분 | 주소 |
| --- | --- |
| Backend API | <https://ssafy-first-project-localhub.onrender.com> |
| 상태 확인 | <https://ssafy-first-project-localhub.onrender.com/health> |
| Swagger API 문서 | <https://ssafy-first-project-localhub.onrender.com/docs> |
| Frontend | Netlify 프로젝트의 Production URL 사용 |

정상 상태에서는 `/health`가 아래와 같은 값을 반환합니다. `chatMode`는 `OPENAI_API_KEY` 설정 여부에 따라 `openai` 또는 `local`이 됩니다.

```json
{
  "status": "ok",
  "chatMode": "openai"
}
```

## 프로젝트 소개

In지도는 장소 탐색, 지도, 지역 커뮤니티, 챗봇을 하나의 화면에 구성한 서비스입니다. 상단 커뮤니티에서 여행 경험을 공유하고, 하단 지역 탐색 영역에서 공공데이터 장소를 확인하며, 어느 화면에서든 플로팅 챗봇으로 저장된 장소와 게시글에 관해 질문할 수 있습니다.

공공데이터는 사용자가 화면을 열 때마다 원본 API에서 실시간으로 받지 않습니다. 미리 수집한 JSON 스냅샷을 서버 시작 시 SQLite에 시딩하여 빠르고 일관되게 조회하며, 지도 타일과 OpenAI 답변만 런타임 외부 서비스에 의존합니다.

## 주요 기능

### 지역정보와 지도

- 서울, 대전·충청, 구미·경북, 광주·전라, 부산 5개 권역 제공
- 관광지, 맛집, 축제, 문화시설, 여행코스, 레포츠, 쇼핑, 숙박 8개 카테고리 제공
- Leaflet과 OpenStreetMap 기반 카테고리별 지도 마커
- 지역·카테고리 필터와 장소 카드 선택 연동
- 장소 이미지, 주소, 설명, 전화번호, 출처, 라이선스, 수집일 표시
- 장소 API는 기본 200건, 최대 500건을 반환하며 카드 목록은 응답 중 처음 20건 표시

### 익명 커뮤니티

- 회원가입 없이 게시글 작성·목록·상세·수정·삭제
- 권역 및 8개 장소 카테고리별 필터
- 작성 비밀번호 확인 후 수정·삭제
- 상세 API 호출 때마다 조회수 증가
- JPEG, PNG, WEBP, GIF 이미지 업로드(최대 5MB)
- 좋아요 등록·취소와 브라우저별 좋아요 상태 저장
- 카테고리별 전국 합산 최근 30개 게시글 보존

### AI 챗봇

- 선택한 권역의 장소와 커뮤니티 게시글을 키워드로 검색해 답변 근거 구성
- 장소를 우선하여 장소·게시글을 합해 최대 5개 검색 결과 사용
- OpenAI API 키가 있으면 모델 답변, 없으면 로컬 안내 답변 제공
- 브라우저 탭의 `sessionStorage`에 최근 20개 메시지 저장
- API 요청에는 최근 대화 최대 10개 전달
- 게시글 비밀번호는 챗봇 검색 및 API 응답에서 제외

### 화면과 반응형 UI

- 게시판과 장소 탐색을 한 페이지에 배치한 Vue SPA
- 게시글 상세·수정도 별도 HTML 문서가 아닌 같은 SPA에서 인라인 표시
- 모바일, 태블릿, 데스크톱 반응형 레이아웃
- Netlify SPA rewrite로 하위 URL 직접 접속과 새로고침 지원

## 시스템 구성

```text
브라우저
  └─ Vue 3 SPA
      ├─ Vue Router: URL과 화면 상태
      ├─ Axios: REST API 요청
      └─ Leaflet ───────────────→ OpenStreetMap 타일
                  HTTPS
                    ↓
              FastAPI / Render
               ├─ SQLAlchemy ───→ SQLite
               ├─ JSON 스냅샷 시딩
               ├─ 업로드 이미지 저장
               └─ 챗봇 서비스 ──→ OpenAI API(선택)
```

프론트엔드와 백엔드는 별도로 배포합니다. Netlify의 `VITE_API_BASE_URL`이 모든 브라우저를 같은 Render API로 연결하고, Render의 `FRONTEND_ORIGIN`이 해당 Netlify Origin의 CORS 요청을 허용합니다.

## 기술 스택

| 구분 | 기술 | 역할 |
| --- | --- | --- |
| Frontend | Vue 3, Vite 7 | 컴포넌트 기반 SPA와 프로덕션 빌드 |
| Routing | Vue Router 4 | History 모드 URL 및 화면 상태 관리 |
| HTTP | Axios | 공통 API Base URL, 15초 타임아웃, 오류 처리 |
| Map | Leaflet, OpenStreetMap | 지도 타일, 카테고리 마커, 장소 선택 |
| Backend | FastAPI, Uvicorn, Pydantic 2 | REST API, 요청 검증, 응답 직렬화 |
| ORM / DB | SQLAlchemy 2, SQLite | 장소·게시글 저장 및 조회 |
| AI | OpenAI Python SDK | 검색 컨텍스트 기반 챗봇 답변 |
| Test | Pytest | API, 시딩, 수집기 테스트 |
| Deployment | Netlify, Render | 프론트엔드·백엔드 분리 배포 |

권장 개발 환경은 Python 3.11.9와 Node.js `^20.19.0` 또는 `>=22.12.0`입니다.

## 지원 권역과 카테고리

| 타입 | 코드 | 화면 표시 |
| --- | --- | --- |
| Region | `SEOUL` | 서울 |
| Region | `DAEJEON_CHUNGCHEONG` | 대전·충청 |
| Region | `GUMI_GYEONGBUK` | 구미·경북 |
| Region | `GWANGJU_JEOLLA` | 광주·전라 |
| Region | `BUSAN` | 부산 |
| Category | `TOURIST` | 관광지 |
| Category | `RESTAURANT` | 맛집 |
| Category | `FESTIVAL` | 축제 |
| Category | `CULTURE` | 문화시설 |
| Category | `COURSE` | 여행코스 |
| Category | `LEISURE` | 레포츠 |
| Category | `SHOPPING` | 쇼핑 |
| Category | `ACCOMMODATION` | 숙박 |

권역은 대한민국 전체 행정구역을 포괄하는 구분이 아니라 프로젝트에서 선별한 지역 범위입니다. 상세 포함 지역은 [기능 명세서](docs/FUNCTIONAL_SPEC.md)에서 확인할 수 있습니다.

## 라우팅

| URL | 동작 |
| --- | --- |
| `/` | 게시판과 장소 탐색 통합 화면 |
| `/posts`, `/explore` | `/`과 같은 통합 화면 별칭 |
| `/posts/:id` | 통합 화면 안에서 게시글 상세 표시 |
| `/posts/:id/edit` | 통합 화면 안에서 게시글 수정 폼 표시 |
| `/?compose=1#community` | 게시글 작성 폼 열기 |
| `#community`, `#discover` | 커뮤니티·장소 탐색 섹션 이동 |

별도의 `/posts/new` 페이지는 없습니다. Vue Router가 History 모드를 사용하므로 Netlify의 `/* → /index.html` rewrite가 필요하며, 이 규칙은 루트 [netlify.toml](netlify.toml)에 포함되어 있습니다.

## API

기본 로컬 주소는 `http://localhost:8000`, 배포 주소는 `https://ssafy-first-project-localhub.onrender.com`입니다.

| Method | Path | 기능 |
| --- | --- | --- |
| `GET` | `/health` | 서버 상태와 챗봇 모드 확인 |
| `GET` | `/api/places` | `region`, `category`, `limit`로 장소 조회 |
| `GET` | `/api/posts` | `region`, `category`로 게시글 목록 조회 |
| `POST` | `/api/posts` | 게시글 작성 |
| `GET` | `/api/posts/{post_id}` | 게시글 상세 조회 및 조회수 증가 |
| `PATCH` | `/api/posts/{post_id}` | 비밀번호 확인 후 게시글 수정 |
| `DELETE` | `/api/posts/{post_id}` | JSON body의 `password` 확인 후 삭제 |
| `POST` | `/api/posts/{post_id}/like` | 좋아요 증가 |
| `DELETE` | `/api/posts/{post_id}/like` | 좋아요 감소 |
| `POST` | `/api/posts/{post_id}/image` | multipart 이미지 업로드 |
| `GET` | `/uploads/{filename}` | 업로드 이미지 정적 제공 |
| `POST` | `/api/chat` | 지역정보·게시글 기반 질의응답 |

일반 API 성공 응답은 다음 형태를 사용하며 필드 이름은 프론트엔드에 맞춘 `camelCase`입니다.

```json
{
  "success": true,
  "data": {},
  "message": "처리 결과"
}
```

오류 응답은 `success: false`, `data: null`, 사용자 메시지와 `error.code`를 포함합니다. 전체 스키마와 직접 실행 가능한 명세는 `/docs`에서 확인할 수 있습니다.

## 공공데이터

### 데이터 범위

저장소에는 40개 JSON 스냅샷, 원본 14,139건이 있으며 빈 DB 기준 품질 검사를 통과한 14,124건이 적재됩니다.

| 권역 | JSON 원본 | 빈 DB 초기 적재 |
| --- | ---: | ---: |
| 서울 | 7,518 | 7,512 |
| 대전·충청 | 1,365 | 1,362 |
| 구미·경북 | 1,667 | 1,665 |
| 광주·전라 | 1,393 | 1,390 |
| 부산 | 2,196 | 2,195 |
| 합계 | **14,139** | **14,124** |

초기 적재 수는 비어 있는 DB를 기준으로 한 예상치입니다. 실제 기존 DB는 스냅샷 동기화 정책에 따라 수가 달라질 수 있습니다.

### 출처와 라이선스 표기

| 데이터 | 수집 범위 | 프로젝트 문서 표기 |
| --- | --- | --- |
| 한국관광공사 TourAPI 4.0 | 5개 권역 관광 데이터 | 공공누리 제3유형 |
| 서울시 일반음식점 인허가 정보 | 영업 중 120,343건 중 1,000건 | 공공누리 제1유형 |
| 부산맛집정보 서비스 | 제공된 437건 전체 | 공공누리 제1유형 |

- 음식점 스냅샷 기준일은 2026-07-16입니다.
- 서울 음식점 좌표는 수집 시 EPSG:5174에서 WGS84로 변환합니다.
- 서울 데이터는 추천 맛집 목록이 아니라 영업 중 일반음식점 인허가 자료의 제한 표본입니다.
- 장소별 외부 이미지와 TourAPI 사진은 각 원본의 개별 저작권·공공누리 조건을 함께 확인해야 합니다.
- 기능 명세서 v1.1은 부산맛집정보를 공공누리 제1유형으로 관리합니다. 현재 저장된 부산 JSON과 수집기 메타데이터에는 이전 값인 `이용허락범위 제한 없음`이 남아 있어, 데이터를 다시 생성하기 전까지 장소 상세에 이전 값이 표시될 수 있습니다.

### 서버 시작 시 시딩

- 서버가 시작될 때마다 `source_id`를 기준으로 장소를 추가하거나 갱신합니다.
- ID·제목이 없거나 제목이 2~100자가 아니면 제외하며, 테스트용·오염 키워드가 포함된 제목도 제외합니다.
- `sync: true`인 서울·부산 음식점 스냅샷은 원본에서 사라진 같은 공급자의 기존 행을 정리합니다.
- TourAPI 스냅샷은 비동기화 방식이므로 JSON에서 빠진 행이 기존 DB에 남을 수 있습니다.
- 장소 시딩은 유지 중인 DB의 게시글을 수정하지 않습니다.

## 저장소 구조

```text
.
├─ backend/
│  ├─ app/
│  │  ├─ routers/           # places, posts, chat API
│  │  ├─ services/          # 챗봇 검색 및 OpenAI 연동
│  │  ├─ main.py            # FastAPI 앱, CORS, 정적 업로드
│  │  ├─ models.py          # SQLAlchemy Place/Post 모델
│  │  ├─ schemas.py         # Pydantic 요청·응답 모델
│  │  ├─ database.py        # DB 엔진과 세션
│  │  └─ seed.py            # JSON 장소 시딩
│  ├─ tests/                # API·시딩·수집기 테스트
│  └─ tools/                # 서울·부산 음식점 수집기
├─ frontend/
│  └─ src/
│     ├─ api/               # Axios 클라이언트와 API 함수
│     ├─ components/        # 지도, 게시글 폼, 챗봇 등
│     ├─ router/            # Vue Router
│     └─ views/             # 통합 Home/Board 화면
├─ data/                    # 권역·카테고리별 JSON과 출처 문서
├─ docs/                    # 기능 명세서와 프로젝트 문서
├─ netlify.toml             # 프론트엔드 빌드 및 SPA rewrite
└─ render.yaml              # 백엔드 Render Blueprint
```

## 로컬 실행

### 1. 저장소와 환경변수 준비

```powershell
git clone https://github.com/mynolee/ssafy_first_project_localhub.git
Set-Location ssafy_first_project_localhub
Copy-Item .env.example .env
```

`OPENAI_API_KEY`는 선택입니다. 비워 두면 나머지 기능은 그대로 실행되고 챗봇만 로컬 폴백 모드로 동작합니다. 공공데이터 인증키도 기존 스냅샷으로 앱을 실행할 때는 필요하지 않습니다.

### 2. 백엔드 실행

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Set-Location backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

백엔드는 `http://localhost:8000`, Swagger 문서는 `http://localhost:8000/docs`에서 열립니다. 첫 실행에는 장소 시딩 때문에 시간이 조금 더 걸릴 수 있습니다.

### 3. 프론트엔드 실행

새 PowerShell 터미널에서 실행합니다.

```powershell
Set-Location frontend
npm.cmd install
npm.cmd run dev
```

프론트엔드는 기본적으로 `http://localhost:5173`에서 열립니다. 개발 모드의 Axios 클라이언트는 브라우저와 같은 호스트의 8000번 포트로 요청하므로, 백엔드도 함께 실행해야 합니다.

## 환경변수

### Backend / Render

| 변수 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `DATABASE_URL` | 선택 | `sqlite:///./localhub.db` | SQLAlchemy DB 연결 문자열 |
| `FRONTEND_ORIGIN` | 배포 시 필수 | 로컬 5173 Origin | 허용할 프론트엔드 Origin, 여러 개는 쉼표로 구분 |
| `OPENAI_API_KEY` | 선택 | 빈 값 | OpenAI 챗봇 사용 키 |
| `OPENAI_MODEL` | 선택 | `gpt-4.1-mini` | 챗봇 모델 |
| `DATA_ROOT` | 선택 | 프로젝트의 `data/` | JSON 스냅샷 루트 경로 |
| `PYTHON_VERSION` | Render 필수 | `3.11.9` | Render Python 런타임 고정 |

`FRONTEND_ORIGIN`에는 경로 없이 실제 Origin만 넣습니다. 예: `https://your-site.netlify.app`. `PORT`는 Render가 자동으로 제공합니다.

### Frontend / Netlify

| 변수 | 필수 | 예시 | 설명 |
| --- | --- | --- | --- |
| `VITE_API_BASE_URL` | 배포 시 필수 | `https://ssafy-first-project-localhub.onrender.com` | 브라우저가 사용할 Render API 주소 |

`VITE_` 변수는 빌드 결과에 공개됩니다. `OPENAI_API_KEY`나 공공데이터 인증키 같은 비밀값을 Netlify 프론트엔드 환경변수에 넣으면 안 됩니다. 값을 변경한 뒤에는 Netlify를 다시 배포해야 합니다.

### 오프라인 데이터 수집 전용

| 변수 | 용도 |
| --- | --- |
| `SEOUL_OPEN_DATA_API_KEY` | 서울 일반음식점 스냅샷 갱신 |
| `BUSAN_FOOD_API_KEY` | 부산맛집정보 스냅샷 갱신 |

## 음식점 스냅샷 갱신

앱 런타임과 분리된 관리 작업입니다. 인증키를 루트 `.env`에 설정한 뒤 실행합니다.

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-data.txt
Set-Location backend
..\.venv\Scripts\python.exe -m tools.collect_food_data seoul --max-items 1000
..\.venv\Scripts\python.exe -m tools.collect_food_data busan
```

- 수집기는 서울·부산 음식점만 지원합니다. TourAPI 스냅샷 재수집기는 이 저장소에 포함되어 있지 않습니다.
- 인증키는 `.env`에서만 읽으며 생성 JSON이나 Git 커밋에 포함하지 않습니다.
- 서울 API 키는 요청 URL 경로에 포함되므로 요청 URL 전체를 로그나 이슈에 공개하지 않습니다.
- 갱신 후 백엔드를 재시작해 스냅샷을 DB에 반영하고 테스트를 실행합니다.

## 테스트와 빌드

```powershell
# Backend
Set-Location backend
..\.venv\Scripts\python.exe -m pytest

# Frontend
Set-Location ..\frontend
npm.cmd run build
```

프론트엔드 빌드 결과는 `frontend/dist/`에 생성됩니다.

## 배포

### Render 백엔드

루트 [render.yaml](render.yaml)의 Blueprint 설정은 다음과 같습니다.

| 항목 | 값 |
| --- | --- |
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/health` |
| Python | `3.11.9` |

Render 환경변수에 `FRONTEND_ORIGIN`을 실제 Netlify Origin으로 설정하고, 필요하면 `OPENAI_API_KEY`를 추가합니다. Python을 기본 최신 버전에 맡기면 일부 고정 패키지의 wheel이 없어 빌드가 실패할 수 있으므로 `PYTHON_VERSION=3.11.9`를 유지합니다.

### Netlify 프론트엔드

루트 [netlify.toml](netlify.toml)이 아래 설정을 제공합니다.

| 항목 | 값 |
| --- | --- |
| Base directory | `frontend` |
| Build command | `npm run build` |
| Publish directory | `dist` |
| Environment | `VITE_API_BASE_URL=https://ssafy-first-project-localhub.onrender.com` |

1. GitHub 저장소를 Netlify 프로젝트에 연결합니다.
2. `VITE_API_BASE_URL`을 Render 주소로 등록합니다.
3. 배포된 Netlify Origin을 Render의 `FRONTEND_ORIGIN`에 등록합니다.
4. 양쪽을 재배포하고 브라우저 개발자 도구에서 API 요청 주소와 CORS 오류 여부를 확인합니다.
5. Render `/health`와 Netlify의 `/posts/1` 같은 하위 경로 새로고침을 확인합니다.

## 여러 사용자 간 게시글 공유 조건

모든 사용자가 같은 Netlify 사이트를 열고, 그 사이트가 동일한 `VITE_API_BASE_URL`의 Render API와 동일한 DB를 사용해야 게시글이 공유됩니다.

- 이 앱은 WebSocket, SSE, polling을 사용하지 않으므로 다른 사용자가 쓴 글이 자동으로 나타나지 않습니다. 새로고침하거나 목록을 다시 조회해야 합니다.
- 각 브라우저에서 자기 글만 보이면 배포 빌드의 API 주소가 `localhost`인지, 서로 다른 Render 서비스인지 먼저 확인합니다.
- 새로고침해도 글이 사라지거나 사용자마다 결과가 바뀌면 Render 인스턴스의 SQLite 보존 문제를 확인합니다.
- 다중 사용자 운영에는 외부 관리형 PostgreSQL과 외부 객체 스토리지를 연결하는 구성이 필요합니다. 현재 requirements에는 PostgreSQL 드라이버와 객체 스토리지 연동이 포함되어 있지 않아 추가 구현이 필요합니다.

## 현재 구현의 제약과 운영 주의사항

- Render 무료 인스턴스의 로컬 SQLite 파일과 `backend/uploads/`는 영구 저장소가 아닙니다. 재배포·재시작·인스턴스 교체 후 게시글과 이미지가 사라질 수 있습니다.
- 게시글 비밀번호는 현재 해시가 아닌 평문으로 저장됩니다. 시연용 비밀번호만 사용하고 실제 계정 비밀번호를 재사용하지 않습니다.
- 이미지 업로드 API는 게시글 비밀번호를 확인하지 않으며, 일반 게시글 삭제 시 연결된 파일이 즉시 함께 삭제되지 않습니다.
- 좋아요는 계정 인증 없이 서버 카운터를 변경하고, 중복 방지는 브라우저 `localStorage` 수준입니다.
- 조회수는 고유 방문자 수가 아니라 게시글 상세 API가 호출된 횟수입니다.
- 게시글은 카테고리별 전국 합산 30개까지만 보존되며, 새 글 작성 직후에만 제한을 검사합니다.
- 게시글 검색, 페이지네이션, 댓글, 로그인, 관리자 화면, 실시간 동기화는 현재 범위에 없습니다.
- 챗봇은 벡터 DB 기반 RAG가 아니라 SQL 키워드 검색을 사용합니다.
- 공개된 챗봇 API에는 인증·사용량 제한이 없어 OpenAI 비용과 오남용 방지 대책이 별도로 필요합니다.
- OpenStreetMap 타일, 외부 장소 이미지, OpenAI API는 각 외부 서비스의 가용성과 정책에 영향을 받습니다.
- 저장소에는 프로젝트 소스 코드 사용 조건을 정한 별도의 `LICENSE` 파일이 없습니다.

## 문서

- [기능 명세서 v1.1 (Markdown)](docs/FUNCTIONAL_SPEC.md)
- [기능 명세서 v1.1 (PDF)](docs/기능명세서_수정본_v1.1.pdf)
- 권역별 데이터 출처와 스키마: `data/<권역>/SOURCE.md`, `data/<권역>/SCHEMA.md`
