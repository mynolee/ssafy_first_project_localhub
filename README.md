# 여행씰

전국 5개 권역 공공데이터 기반 지역 정보 조회, 익명 커뮤니티, AI 챗봇을 제공하는 팀 프로젝트입니다.

## 기술 스택

- Frontend: Vue 3, Vite, Vue Router, Leaflet
- Backend: FastAPI, SQLAlchemy, SQLite, OpenAI API
- Deployment: Netlify, Render

## 로컬 실행

루트의 `.env.example`을 `.env`로 복사하고 `OPENAI_API_KEY`를 입력합니다. 키가 비어 있으면 챗봇은 검색 결과를 조합한 로컬 안내 문구로 동작합니다.

```powershell
# Backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Set-Location backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload

# Frontend (별도 터미널)
Set-Location frontend
npm.cmd install
npm.cmd run dev
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- API 문서: `http://localhost:8000/docs`

## 주요 기능

- 5개 권역 지역정보 카드와 Leaflet/OpenStreetMap 지도 마커
- 지역 필터와 관광지·맛집·축제·문화시설 익명 게시판 CRUD
- 하나의 SPA 메인 화면에서 게시판을 먼저 보여주고 지역 지도를 그 아래에 배치
- 작성 비밀번호를 통한 게시글 수정·삭제 확인
- 지역정보와 게시글만 근거로 답하는 플로팅 챗봇
- 모바일 반응형 화면과 세션 단위 대화 기록

## API

| Method | Path | 기능 |
| --- | --- | --- |
| `GET` | `/api/places` | 지역정보 목록과 지역·카테고리 필터 |
| `POST` | `/api/posts` | 게시글 작성 |
| `GET` | `/api/posts` | 게시글 목록과 지역·카테고리 필터 |
| `GET` | `/api/posts/{id}` | 게시글 상세 |
| `PATCH` | `/api/posts/{id}` | 비밀번호 확인 후 수정 |
| `DELETE` | `/api/posts/{id}` | 비밀번호 확인 후 삭제 |
| `POST` | `/api/chat` | 지역정보·게시글 기반 질의응답 |

## 테스트와 빌드

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m pytest

Set-Location ..\frontend
npm.cmd run build
```

## 배포

- `netlify.toml`: `frontend`를 Netlify에 빌드·배포하고 SPA 경로를 처리합니다.
- `render.yaml`: `backend`를 Render Web Service로 실행합니다.
- Netlify에는 `VITE_API_BASE_URL`, Render에는 `OPENAI_API_KEY`와 `FRONTEND_ORIGIN`을 환경변수로 등록해야 합니다.
- SQLite 파일은 Git에서 제외됩니다. 시연 또는 제출용 DB는 백엔드를 한 번 실행해 생성한 뒤 별도 산출물로 제출합니다.
- 백엔드 최초 실행 시 `data/`의 TourAPI JSON 12,702건을 `backend/localhub.db`에 자동 적재합니다. 기존 게시글은 보존됩니다.

상세 범위와 데이터 교체 절차는 [기능 명세서](docs/FUNCTIONAL_SPEC.md)를 참고하세요.
