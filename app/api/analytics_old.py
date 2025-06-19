from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
import pandas as pd

from ..database import get_purchase_data, get_purchase_data_async
from ..models import (
    DashboardResponse, DashboardMetrics, WeeklyTrendItem,
    CategoryData, HourlyData, PopularProduct, AlertItem,
    ChildrenResponse, ChildInfo, HealthResponse,
    EnhancedDashboardResponse, MLAnalysis, PersonalityAnalysis, 
    AnomalyAnalysis, PersonalityType, AnomalyAlert
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
        
        # 분석 수행 (ML 기능 포함)
        analyzer = PurchaseAnalyzer(df)
        
        # 종합 분석 실행
        try:
            comprehensive_data = analyzer.get_comprehensive_analysis()
            
            return DashboardResponse(
                metrics=DashboardMetrics(**comprehensive_data['metrics']),
                weeklyTrend=[WeeklyTrendItem(**item) for item in comprehensive_data['weeklyTrend']],
                categoryData=[CategoryData(**item) for item in comprehensive_data['categoryData']],
                hourlyData=[HourlyData(**item) for item in comprehensive_data['hourlyData']],
                popularProducts=[PopularProduct(**item) for item in comprehensive_data['popularProducts']],
                alerts=[AlertItem(**item) for item in comprehensive_data['alerts']],
                lastUpdated=comprehensive_data['lastUpdated']
            )
        except Exception as ml_error:
            # ML 기능 실패 시 기본 분석으로 fallback
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

@router.get("/dashboard/{child_id}/enhanced", response_model=EnhancedDashboardResponse)
async def get_enhanced_dashboard_data(
    child_id: str,
    days: int = Query(30, description="분석할 일수", ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    ML 분석을 포함한 확장된 대시보드 데이터 조회
    - child_id: 아이 식별자
    - days: 분석할 기간 (기본 30일)
    """
    try:
        # 기본 대시보드 데이터 먼저 가져오기
        basic_response = await get_dashboard_data(child_id, days, db)
        
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
        df = pd.DataFrame(rows, columns=columns)
        
        # 데이터 타입 변환
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0).astype(int)
        df['cnt'] = pd.to_numeric(df['cnt'], errors='coerce').fillna(0).astype(int)
        
        # ML 분석 수행
        analyzer = PurchaseAnalyzer(df)
        
        try:
            # 성향 분석
            personality_insights = analyzer.get_personality_insights()
            personality_analysis = PersonalityAnalysis(
                personality_type=PersonalityType(
                    name=personality_insights.get('personality_type', '분석 중'),
                    description=personality_insights.get('description', ''),
                    characteristics=personality_insights.get('characteristics', []),
                    color=personality_insights.get('color', '#6B7280'),
                    confidence=personality_insights.get('confidence', 0.0)
                ),
                features=personality_insights.get('features', {}),
                personality_score=personality_insights.get('personality_score', {})
            )
            
            # 이상 탐지
            anomaly_result = analyzer.get_anomaly_detection()
            anomaly_alerts = []
            
            if anomaly_result.get('anomalies'):
                for anomaly in anomaly_result['anomalies']:
                    anomaly_alerts.append(AnomalyAlert(
                        type=anomaly.get('type', 'warning'),
                        title=anomaly.get('title', '이상 패턴 감지'),
                        description=anomaly.get('description', ''),
                        severity=anomaly.get('severity', 'medium'),
                        icon=anomaly.get('icon', 'alert-triangle'),
                        confidence=anomaly.get('confidence', 0.0),
                        details=anomaly.get('details', {})
                    ))
            
            anomaly_analysis = AnomalyAnalysis(
                is_anomaly=anomaly_result.get('anomalies_detected', False),
                anomaly_score=anomaly_result.get('anomaly_score', 0.0),
                alerts=anomaly_alerts
            )
            
            # ML 분석 결과 통합
            ml_analysis = MLAnalysis(
                personality=personality_analysis,
                anomaly=anomaly_analysis,
                recommendations=personality_insights.get('recommendations', []) + 
                              anomaly_result.get('recommendations', []),
                last_model_update=datetime.now()
            )
            
        except Exception as ml_error:
            # ML 분석 실패 시 기본값
            ml_analysis = MLAnalysis(
                personality=PersonalityAnalysis(
                    personality_type=PersonalityType(
                        name="분석 대기 중",
                        description="충분한 데이터가 수집되면 성향 분석을 제공합니다.",
                        characteristics=[],
                        color="#6B7280",
                        confidence=0.0
                    ),
                    features={},
                    personality_score={}
                ),
                anomaly=AnomalyAnalysis(
                    is_anomaly=False,
                    anomaly_score=0.0,
                    alerts=[]
                ),
                recommendations=["더 많은 데이터가 수집되면 개인화된 추천을 제공할 예정입니다."],
                last_model_update=None
            )
        
        return EnhancedDashboardResponse(
            metrics=basic_response.metrics,
            weeklyTrend=basic_response.weeklyTrend,
            categoryData=basic_response.categoryData,
            hourlyData=basic_response.hourlyData,
            popularProducts=basic_response.popularProducts,
            alerts=basic_response.alerts,
            ml_analysis=ml_analysis,
            lastUpdated=basic_response.lastUpdated
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"확장 대시보드 분석 중 오류: {str(e)}")

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


