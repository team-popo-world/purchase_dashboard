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

### 🛠 기술 스택
- **Backend**: FastAPI + MongoDB + Pandas
- **Database**: MongoDB
- **Package Management**: UV (Python)

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
uv run uvicorn app.main:app --reload --port 8000
```

### 4. 접속 확인
- **API 문서**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📡 API 엔드포인트

### 대시보드 데이터
```
GET /api/dashboard/{child_id}?days={days}
```
- **파라미터**: 
  - `child_id`: 아이 식별자
  - `days`: 분석 기간 (기본값: 7일)
- **응답**: 주간 메트릭, 트렌드, 분포, 패턴, 인기상품, 알림 데이터

### 시스템 상태
```
GET /health
```
- **응답**: 서버 및 데이터베이스 연결 상태

## 📁 프로젝트 구조

```
purchase_dashboard/
├── app/                    # 백엔드 애플리케이션
│   ├── main.py            # FastAPI 앱 엔트리포인트
│   ├── database.py        # MongoDB 연결 관리
│   ├── models.py          # 데이터 모델 정의
│   ├── analytics.py       # 데이터 분석 로직
│   └── api/
│       └── analytics.py   # API 엔드포인트
├── pyproject.toml         # Python 프로젝트 설정
├── requirements.txt       # Python 의존성 (호환성)
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
  timestamp: Date,        // 구매 시간
  label: String,          // 카테고리 (SNACK, ENTERTAINMENT, TOY, EDUCATION, ETC)
  productId: String       // 상품 식별자
}
```

## 🎯 카테고리 매핑

| 원본 라벨 | 한국어 카테고리 | 설명 |
|-----------|-----------------|------|
| SNACK | 간식 | 과자, 사탕 등 |
| ENTERTAINMENT | 오락 | 게임, 영상 시청 등 |
| TOY | 장난감 | 레고, 인형 등 |
| EDUCATION | 교육 | 도서, 학습 도구 등 |
| FOOD/ETC | 기타 | 기타 모든 항목 |

## 🔧 개발 참고사항

### 코드 스타일
- Python: FastAPI 권장 스타일
- API 설계: RESTful 원칙 준수

### 주요 라이브러리
- **분석**: pandas, numpy
- **웹 프레임워크**: FastAPI
- **데이터베이스**: pymongo, motor

### 환경별 설정
- **개발**: 로컬 MongoDB, Hot reload 활성화
- **프로덕션**: 환경변수로 MongoDB URI 설정

## 📈 성능 최적화

- MongoDB 쿼리 최적화 (인덱스 활용)
- API 응답 캐싱 (필요시)
- 비동기 처리로 동시성 향상
- 데이터 분석 결과 메모화

## 🤝 기여하기

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

This project is licensed under the MIT License.
