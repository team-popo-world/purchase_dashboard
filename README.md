# 아이 습관 분석 API

구매 데이터 기반 아이 소비 패턴 분석 시스템

## 프로젝트 구조

```
purchase_dashboard/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 앱 설정
│   ├── database.py            # 데이터베이스 설정 및 모델
│   ├── models.py              # Pydantic 모델
│   ├── analytics.py           # 데이터 분석 로직
│   └── api/
│       ├── __init__.py
│       └── analytics.py       # API 엔드포인트
├── main.py                    # 서버 실행 파일
├── requirements.txt           # 의존성 목록
├── .env.example              # 환경변수 예시
└── README.md                 # 이 파일
```

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 데이터베이스 URL을 설정하세요:

```bash
cp .env.example .env
```

`.env` 파일 내용:
```
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

### 3. 서버 실행

```bash
# 개발 모드로 실행
python main.py

# 또는 uvicorn으로 직접 실행
uvicorn app.main:app --reload --port 8000
```

### 4. API 문서 확인

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

### 대시보드 데이터
- `GET /api/dashboard/{child_id}`: 대시보드 데이터 조회
- `GET /api/children`: 등록된 아이들 목록
- `GET /api/categories/stats/{child_id}`: 카테고리별 상세 통계
- `GET /api/timeline/{child_id}`: 구매 타임라인

### 헬스체크
- `GET /health`: 서버 및 데이터베이스 상태 확인

## 주요 기능

1. **주간 메트릭 분석**: 이번 주 소비 총액, 변화율, 인기 카테고리 등
2. **일별 트렌드**: 카테고리별 주간 소비 패턴
3. **카테고리 분포**: 간식, 오락, 장난감, 교육, 기타 카테고리별 분포
4. **시간대별 패턴**: 24시간 구매 패턴 분석
5. **인기 상품**: 가장 많이 구매된 상품 순위
6. **스마트 알림**: 소비 패턴 기반 개인화된 알림

## 데이터베이스 스키마

```sql
CREATE TABLE purchasehistory (
    id VARCHAR PRIMARY KEY,
    type VARCHAR NOT NULL,          -- 카테고리 (간식, 오락, 장난감, 교육, 기타)
    name VARCHAR NOT NULL,          -- 상품명
    price INTEGER NOT NULL,         -- 개별가격
    cnt INTEGER NOT NULL,           -- 구매개수
    timestamp TIMESTAMP NOT NULL,   -- 구매시간
    child_id VARCHAR NOT NULL       -- 아이 식별자
);
```

## 개발 참고사항

- 데이터베이스 연결이 필요하므로 테스트 시 PostgreSQL 서버가 실행 중이어야 합니다
- 모든 내용은 기존 코드를 그대로 유지하면서 모듈화되었습니다
- 환경변수를 통해 데이터베이스 설정을 관리합니다
