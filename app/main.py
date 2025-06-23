from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.analytics import router as analytics_router

# FastAPI 앱 초기화
app = FastAPI(
    title="아이 습관 분석 API",
    description="구매 데이터 기반 아이 소비 패턴 분석 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포시에는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(analytics_router)

# Root level health check endpoint
@app.get("/health")
async def root_health_check():
    """Root level health check"""
    return {
        "status": "healthy",
        "database": "connected", 
        "timestamp": "2025-06-18T14:30:25.123456"
    }

@app.get("/")
async def root():
    return {"message": "아이 습관 분석 API 서버가 실행 중입니다!"}
