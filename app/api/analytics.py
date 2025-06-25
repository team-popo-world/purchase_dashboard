from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
import pandas as pd

from ..database import get_purchase_data, get_purchase_data_async, async_collection
from ..models import (
    DashboardResponse, DashboardMetrics, WeeklyTrendItem,
    CategoryData, HourlyData, PopularProduct, AlertItem,
    ChildrenResponse, ChildInfo, HealthResponse
)
from ..analytics import PurchaseAnalyzer
from ..utils import get_kst_now

router = APIRouter(prefix="/api", tags=["analytics"])

@router.get("/dashboard/{child_id}", response_model=DashboardResponse)
async def get_dashboard_data(
    child_id: str,
    days: int = Query(7, description="분석할 일수", ge=1, le=365)
):
    """
    대시보드 데이터 조회
    - child_id: 아이 식별자
    - days: 분석할 기간 (기본 7일)
    """
    try:
        # MongoDB에서 데이터 조회
        df = get_purchase_data(child_id=child_id, days=days)
        
        if df.empty:
            # 빈 데이터 응답
            return DashboardResponse(
                metrics=DashboardMetrics(
                    thisWeekTotal=0,
                    weeklyChange=0.0,
                    mostPopularCategory="데이터 없음",
                    educationRatio=0.0,
                    totalPurchases=0,
                    avgPurchaseAmount=0.0
                ),
                weeklyTrend=[],
                categoryData=[],
                hourlyData=[],
                popularProducts=[],
                alerts=[{
                    'type': 'info',
                    'title': '첫 구매를 시작해보세요',
                    'message': '아직 구매 데이터가 없어요!'
                }],
                lastUpdated=get_kst_now()
            )
        
        # 분석기 생성
        analyzer = PurchaseAnalyzer(df)
        
        # 메트릭 계산
        metrics_data = analyzer.get_weekly_metrics()
        metrics = DashboardMetrics(**metrics_data)
        
        # 주간 트렌드
        weekly_trend = [WeeklyTrendItem(**item) for item in analyzer.get_weekly_trend()]
        
        # 카테고리 분포
        category_data = [CategoryData(**item) for item in analyzer.get_category_distribution()]
        
        # 시간대별 패턴
        hourly_data = [HourlyData(**item) for item in analyzer.get_hourly_pattern()]
        
        # 인기 상품
        popular_products = [PopularProduct(**item) for item in analyzer.get_popular_products()]
        
        # 알림 생성
        alerts = [AlertItem(**alert) for alert in analyzer.generate_alerts(metrics_data)]
        
        return DashboardResponse(
            metrics=metrics,
            weeklyTrend=weekly_trend,
            categoryData=category_data,
            hourlyData=hourly_data,
            popularProducts=popular_products,
            alerts=alerts,
            lastUpdated=get_kst_now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대시보드 데이터 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/children", response_model=ChildrenResponse)
async def get_children_list():
    """모든 아이 목록 조회"""
    try:
        # MongoDB에서 고유한 childId 조회
        pipeline = [
            {"$group": {"_id": "$childId"}},
            {"$sort": {"_id": 1}}
        ]
        
        children_cursor = async_collection.aggregate(pipeline)
        children_list = await children_cursor.to_list(length=None)
        
        children = [ChildInfo(child_id=child["_id"]) for child in children_list if child["_id"]]
        
        return ChildrenResponse(children=children)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"아이 목록 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """헬스 체크 엔드포인트"""
    try:
        # MongoDB 연결 테스트
        count = await async_collection.count_documents({})
        
        return HealthResponse(
            status="healthy",
            database=f"MongoDB 연결 정상 (총 {count}건의 데이터)",
            timestamp=get_kst_now()
        )
        
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            database=f"MongoDB 연결 오류: {str(e)}",
            timestamp=get_kst_now()
        )
