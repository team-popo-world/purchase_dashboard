# 🎮 구매 패턴 분석 API

아이들의 구매 습관과 소비 패턴을 분석하는 백엔드 API 서버입니다.

## ✨ 주요 기능

### 📊 API 기능
- **주간 메트릭**: 총 소비액, 전주 대비 변화율, 인기 카테고리, 교육 비중
- **일별 트렌드**: 주간 카테고리별 소비 패턴 데이터
- **카테고리 분포**: 간식, 오락, 장난감, 교육, 기타별 지출 분포
- **시간대 패턴**: 24시간 구매 시간대별 행동 분석
- **인기 상품**: 가장 많이 구매하는 상품 랭킹 (Top 8)
- **스마트 알림**: 소비 패턴 기반 개인화된 추천 및 경고
- **한국 시간 지원**: 모든 타임스탬프가 KST(UTC+9) 기준으로 처리

### 🛠 기술 스택
- **Backend**: FastAPI + MongoDB + Pandas
- **Database**: MongoDB
- **Package Management**: UV (Python)
- **Timezone**: pytz (한국 시간 지원)

## 🚀 빠른 시작

### 전제 조건
- Python 3.9+
- MongoDB 실행 중
- UV (Python package manager)

### 1. 저장소 클론 및 설정
```bash
git clone <repository-url>
cd purchase_dashboard

# Python 환경 설정
uv sync
```

### 2. 환경 변수 설정
`.env.example` 파일을 `.env`로 복사하고 MongoDB 설정:

```bash
cp .env.example .env
```

`.env` 파일 내용:
```env
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=finance_app
COLLECTION_NAME=purchase_history
```

### 3. 서버 실행

```bash
# UV 환경에서 실행
uv run uvicorn app.main:app --reload --port 8001
```

### 4. 접속 확인
- **API 문서**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 📡 API 엔드포인트

### 대시보드 데이터
```
GET /api/dashboard/{child_id}?days={days}
```
- **파라미터**: 
  - `child_id`: 아이 식별자
  - `days`: 분석 기간 (기본값: 7일)
- **응답**: 주간 메트릭, 트렌드, 분포, 패턴, 인기상품, 알림 데이터
- **타임스탬프**: 모든 시간 데이터는 한국 시간(KST) 기준

### 아이 목록 조회
```
GET /api/children
```
- **응답**: 시스템에 등록된 모든 아이 목록

### 시스템 상태
```
GET /health
GET /api/health
```
- **응답**: 서버 및 데이터베이스 연결 상태 (한국 시간 포함)

## 📁 프로젝트 구조

```
purchase_dashboard/
├── app/                    # 백엔드 애플리케이션
│   ├── main.py            # FastAPI 앱 엔트리포인트
│   ├── database.py        # MongoDB 연결 관리
│   ├── models.py          # 데이터 모델 정의
│   ├── analytics.py       # 데이터 분석 로직
│   ├── utils.py           # 한국 시간 유틸리티 함수
│   └── api/
│       └── analytics.py   # API 엔드포인트
├── pyproject.toml         # Python 프로젝트 설정
├── requirements.txt       # Python 의존성 (호환성)
├── uv.lock               # UV 의존성 잠금 파일
└── .env                   # 환경 변수 설정
```

## 🗃 데이터베이스 스키마

MongoDB 컬렉션 구조:
```javascript
{
  _id: ObjectId,
  childId: String,        // 아이 식별자
  name: String,           // 상품명
  price: Number,          // 개별 가격
  cnt: Number,            // 구매 개수
  timestamp: Date,        // 구매 시간 (UTC 저장, API에서 KST 변환)
  label: String,          // 카테고리 (SNACK, ENTERTAINMENT, TOY, EDUCATION, ETC)
  productId: String       // 상품 식별자
}
```

### 📅 시간대 처리
- **데이터베이스**: UTC 시간으로 저장
- **API 응답**: 한국 시간(KST, UTC+9)으로 변환
- **분석 기준**: 한국 시간 기준으로 일별/시간별 패턴 계산

## 🎯 카테고리 매핑

| 원본 라벨 | 한국어 카테고리 | 설명 |
|-----------|-----------------|------|
| SNACK | 간식 | 과자, 사탕 등 |
| ENTERTAINMENT | 오락 | 게임, 영상 시청 등 |
| TOY | 장난감 | 레고, 인형 등 |
| EDUCATION | 교육 및 문구 | 도서, 학습 도구 등 |
| FOOD | 먹이 | 게임 캐릭터 먹이 |
| ETC | 기타 | 기타 모든 항목 |

## 🔧 개발 참고사항

### 코드 스타일
- Python: FastAPI 권장 스타일
- API 설계: RESTful 원칙 준수

### 주요 라이브러리
- **분석**: pandas, numpy
- **웹 프레임워크**: FastAPI
- **데이터베이스**: pymongo, motor
- **시간대**: pytz (한국 시간 KST 지원)

### 환경별 설정
- **개발**: 로컬 MongoDB, Hot reload 활성화
- **프로덕션**: 환경변수로 MongoDB URI 설정
- **시간대**: 모든 타임스탬프는 한국 시간(KST, UTC+9) 기준

### 🕒 시간 처리 특징
- **일관성**: 모든 API 응답에서 통일된 한국 시간 제공
- **정확성**: 사용자 시간대에 맞는 정확한 분석 결과
- **호환성**: ISO 8601 형식 + 타임존 오프셋 (`+09:00`) 지원

## 📋 API 응답 예시

### Health Check 응답
```json
{
  "status": "healthy",
  "database": "MongoDB 연결 정상 (총 405건의 데이터)",
  "timestamp": "2025-06-25T14:06:36.418737+09:00"
}
```

### 대시보드 응답 (일부)
```json
{
  "metrics": {
    "thisWeekTotal": 15000,
    "weeklyChange": 12.5,
    "mostPopularCategory": "간식",
    "educationRatio": 25.0
  },
  "lastUpdated": "2025-06-25T14:06:42.975744+09:00"
}
```

## 📝 변경 로그

### v1.1.0 (2025-06-25)
- ✨ **한국 시간 지원**: 모든 타임스탬프가 KST(UTC+9) 기준으로 변경
- 🔧 **새로운 유틸리티**: `app/utils.py` 한국 시간 변환 함수 추가
- 📊 **정확한 분석**: 한국 시간 기준으로 일별/시간별 패턴 분석
- 🌐 **API 개선**: 아이 목록 조회 엔드포인트 추가
- 🐛 **버그 수정**: 교육 카테고리 라벨 통일 ('교육 및 문구')

### v1.0.0 (2025-06-XX)
- 🎉 **초기 릴리스**: 구매 패턴 분석 API 기본 기능 구현
