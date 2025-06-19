# 🎮 아이 습관 분석 대시보드

부모가 아이의 소비 습관과 일상을 게임의 상점 형태로 관리하는 서비스의 분석 대시보드입니다.

## 📊 주요 기능

### 대시보드 구성
- **실시간 지표**: 총 소비액, 인기 카테고리, 교육 비중, 평균 단가
- **트렌드 분석**: 일별/주간 소비 패턴 시각화
- **카테고리 분석**: 간식, 오락, 장난감, 교육, 기타별 지출 분포
- **시간대 패턴**: 구매 시간대별 행동 분석
- **인기 상품**: 가장 많이 구매하는 상품 랭킹
- **스마트 알림**: AI 기반 소비 패턴 분석 및 추천

### 기술 스택
- **Backend**: FastAPI + SQLAlchemy + Pandas
- **Frontend**: React + Recharts + TailwindCSS
- **Database**: SQLite (개발용), PostgreSQL (운영용)
- **시각화**: 인터랙티브 차트 및 대시보드

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# 저장소 클론 (이미 있다면 생략)
cd purchase_dashboard

# 셋업 스크립트 실행 (Mac/Linux)
chmod +x setup.sh
./setup.sh

# 또는 수동 설치
pip install fastapi uvicorn sqlalchemy pandas python-multipart
python create_sample_data.py
```

### 2. 서버 실행
```bash
# FastAPI 서버 시작
python run_server.py

# 서버가 http://localhost:8000 에서 실행됩니다
```

### 3. 대시보드 확인
```bash
# 브라우저에서 index.html 열기
open index.html

# 또는 직접 브라우저에서 파일 열기
```

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
