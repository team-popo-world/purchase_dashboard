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
- **Container**: Docker + Docker Compose
- **Package Management**: UV (Python)

## 🚀 빠른 시작

### 전제 조건
- Python 3.9+
- Docker & Docker Compose (권장)
- UV (Python package manager)

### 1. 저장소 클론 및 설정
```bash
git clone <repository-url>
cd purchase_dashboard
```

## 🐳 Docker로 실행 (권장)

### 1. 환경 변수 설정
```bash
cp .env.example .env
# .env 파일을 편집하여 필요한 설정 변경
```

### 2. Docker Compose로 전체 스택 실행
```bash
# 개발 환경 (백그라운드 실행)
docker-compose up -d

# 로그 확인
docker-compose logs -f app

# 중지
docker-compose down
```

### 3. 접속 확인
- **API 문서**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 💻 로컬 개발 환경

### 1. MongoDB 설정
```bash
# MongoDB 컨테이너만 실행
docker-compose up -d mongodb
```

### 2. Python 환경 설정
```bash
# UV로 의존성 설치
uv sync
```

### 3. 환경 변수 설정 (로컬 개발용)
`.env.example` 파일을 `.env`로 복사하고 로컬 설정으로 수정:

```bash
cp .env.example .env
```

로컬 개발용 `.env` 파일 내용:
```env
# 로컬 MongoDB 설정
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=finance_app
COLLECTION_NAME=purchase_history

# 서버 설정
HOST=0.0.0.0
PORT=8001
RELOAD=true
ENV=development
```

### 4. 로컬 서버 실행

```bash
# UV 환경에서 실행
uv run uvicorn app.main:app --reload --port 8001
```

### 5. 로컬 접속 확인
- **API 문서**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 🔧 유용한 명령어

### Docker 관리
```bash
# 전체 스택 시작
docker-compose up -d

# 로그 실시간 확인
docker-compose logs -f app
docker-compose logs -f mongodb

# 컨테이너 상태 확인
docker-compose ps

# 개별 서비스 재시작
docker-compose restart app

# 코드 변경 후 재빌드
docker-compose build --no-cache app
docker-compose up -d

# 전체 중지 및 정리
docker-compose down
docker-compose down -v  # 볼륨까지 삭제
```

### 데이터베이스 관리
```bash
# MongoDB 컨테이너 접속
docker-compose exec mongodb mongosh

# 특정 데이터베이스 접속
docker-compose exec mongodb mongosh purchase_dashboard
```

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
├── mongo-init/            # MongoDB 초기화 스크립트
│   └── init-mongo.js      # 데이터베이스 초기 설정
├── docker-compose.yml     # 개발용 Docker 설정
├── docker-compose.prod.yml # 프로덕션용 Docker 설정
├── Dockerfile             # 애플리케이션 Docker 이미지
├── pyproject.toml         # Python 프로젝트 설정 (UV)
├── requirements.txt       # Python 의존성 (호환성)
├── deploy.sh              # 배포 스크립트
├── DEPLOYMENT.md          # 배포 가이드
├── .env.example           # 환경 변수 템플릿
└── .env                   # 환경 변수 설정 (로컬)
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

### 환경 변수

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `MONGO_URI` | MongoDB 연결 URI | `mongodb://localhost:27017/` |
| `MONGO_DB_NAME` | 데이터베이스 이름 | `finance_app` |
| `COLLECTION_NAME` | 컬렉션 이름 | `purchase_history` |
| `HOST` | 서버 호스트 | `0.0.0.0` |
| `PORT` | 서버 포트 | `8001` |
| `ENV` | 환경 설정 | `development` |

## 🎯 카테고리 매핑

| 원본 라벨 | 한국어 카테고리 | 설명 |
|-----------|-----------------|------|
| SNACK | 간식 | 과자, 사탕 등 |
| ENTERTAINMENT | 오락 | 게임, 영상 시청 등 |
| TOY | 장난감 | 레고, 인형 등 |
| EDUCATION | 교육 및 문구 | 도서, 학습 도구 등 |
| FOOD | 먹이 | 게임 캐릭터 먹이 |
| ETC | 기타 | 기타 모든 항목 |

## � 배포

### Docker Compose 배포
상세한 배포 가이드는 [DEPLOYMENT.md](DEPLOYMENT.md)를 참고하세요.

```bash
# 프로덕션 환경 배포
docker-compose -f docker-compose.prod.yml up -d

# 배포 스크립트 사용
./deploy.sh
```

### 주요 배포 고려사항
- EC2 보안 그룹: 포트 80 개방 (API 직접 노출)
- 환경 변수 보안 설정
- MongoDB 인증 설정

## �🔧 개발 참고사항

### 코드 스타일
- Python: FastAPI 권장 스타일
- API 설계: RESTful 원칙 준수

### 주요 라이브러리
- **분석**: pandas, numpy
- **웹 프레임워크**: FastAPI
- **데이터베이스**: pymongo, motor (비동기)
- **패키지 관리**: UV
- **컨테이너**: Docker, Docker Compose

### 개발 워크플로우
1. 로컬에서 UV로 개발
2. Docker Compose로 통합 테스트
3. GitHub Actions 등으로 CI/CD (선택사항)

### 환경별 설정
- **개발**: 로컬 MongoDB, Hot reload 활성화
- **테스트**: Docker Compose로 격리된 환경
- **프로덕션**: 환경변수로 보안 설정

## 📈 성능 최적화

- MongoDB 쿼리 최적화 (인덱스 활용)
- API 응답 캐싱 (필요시)
- 비동기 처리로 동시성 향상
- 데이터 분석 결과 메모화
- Docker 멀티 스테이지 빌드로 이미지 최적화

## 🛡️ 보안 고려사항

- FastAPI 내장 CORS 설정
- 환경 변수로 민감 정보 관리
- MongoDB 인증 활성화 (프로덕션)
- 애플리케이션 레벨 Rate Limiting (필요시 추가)

## 🤝 기여하기

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

This project is licensed under the MIT License.
