from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd

from ..database import get_db
from ..models import (
    DashboardResponse, DashboardMetrics, WeeklyTrendItem,
    CategoryData, HourlyData, PopularProduct, AlertItem,
    ChildrenResponse, ChildInfo, HealthResponse
)
from ..analytics import PurchaseAnalyzer

router = APIRouter(prefix="/api", tags=["analytics"])

@router.get("/dashboard/{child_id}", response_model=DashboardResponse)
async def get_dashboard_data(
    child_id: str,
    days: int = Query(30, description="분석할 일수", ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    대시보드 데이터 조회
    - child_id: 아이 식별자
    - days: 분석할 기간 (기본 30일)
    """
    try:
        # 날짜 범위 계산
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # SQL 쿼리 실행
        query = text("""
            SELECT id, type, name, price, cnt, timestamp, child_id
            FROM purchasehistory 
            WHERE child_id = :child_id 
            AND timestamp >= :start_date 
            AND timestamp <= :end_date
            ORDER BY timestamp DESC
        """)
        
        result = db.execute(query, {
            'child_id': child_id,
            'start_date': start_date,
            'end_date': end_date
        })
        
        # DataFrame으로 변환
        columns = ['id', 'type', 'name', 'price', 'cnt', 'timestamp', 'child_id']
        rows = result.fetchall()
        
        if not rows:
            raise HTTPException(status_code=404, detail="해당 아이의 구매 데이터가 없습니다.")
            
        df = pd.DataFrame(rows, columns=columns)
        
        # 데이터 타입 변환 (안전하게)
        try:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0).astype(int)
            df['cnt'] = pd.to_numeric(df['cnt'], errors='coerce').fillna(0).astype(int)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"데이터 타입 변환 오류: {str(e)}")
        
        # 분석 수행
        analyzer = PurchaseAnalyzer(df)
        
        metrics = analyzer.get_weekly_metrics()
        weekly_trend = analyzer.get_weekly_trend()
        category_data = analyzer.get_category_distribution()
        hourly_data = analyzer.get_hourly_pattern()
        popular_products = analyzer.get_popular_products()
        alerts = analyzer.generate_alerts(metrics)
        
        return DashboardResponse(
            metrics=DashboardMetrics(**metrics),
            weeklyTrend=[WeeklyTrendItem(**item) for item in weekly_trend],
            categoryData=[CategoryData(**item) for item in category_data],
            hourlyData=[HourlyData(**item) for item in hourly_data],
            popularProducts=[PopularProduct(**item) for item in popular_products],
            alerts=[AlertItem(**item) for item in alerts],
            lastUpdated=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 분석 중 오류가 발생했습니다: {str(e)}")

@router.get("/children", response_model=ChildrenResponse)
async def get_children_list(db: Session = Depends(get_db)):
    """등록된 아이들 목록 조회"""
    try:
        query = text("SELECT DISTINCT child_id FROM purchasehistory ORDER BY child_id")
        result = db.execute(query)
        children = [ChildInfo(child_id=row[0]) for row in result.fetchall()]
        return ChildrenResponse(children=children)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"아이 목록 조회 중 오류: {str(e)}")

@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """서버 및 데이터베이스 상태 확인"""
    try:
        # DB 연결 테스트
        db.execute(text("SELECT 1"))
        return HealthResponse(
            status="healthy",
            database="connected",
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"서비스 이용 불가: {str(e)}")


