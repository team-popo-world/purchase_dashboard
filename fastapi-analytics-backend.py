# requirements.txt
"""
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pandas==2.1.3
numpy==1.25.2
python-dotenv==1.0.0
pydantic==2.5.0
python-multipart==0.0.6
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text, Column, String, Integer, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import json

# 환경 변수 로드
load_dotenv()

# 데이터베이스 설정
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/kidhabits")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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

# 🗃️ 데이터베이스 모델
class PurchaseHistory(Base):
    __tablename__ = "purchasehistory"
    
    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)  # 카테고리
    name = Column(String, nullable=False)  # 상품명
    price = Column(Integer, nullable=False)  # 개별가격
    cnt = Column(Integer, nullable=False)  # 구매개수
    timestamp = Column(DateTime, nullable=False)
    child_id = Column(String, nullable=False)

# 📊 응답 모델들
class DashboardMetrics(BaseModel):
    thisWeekTotal: int
    weeklyChange: float
    mostPopularCategory: str
    educationRatio: float
    totalPurchases: int
    avgPurchaseAmount: int
    
class CategoryData(BaseModel):
    name: str
    value: int
    color: str

class WeeklyTrendItem(BaseModel):
    day: str
    간식: int = 0
    오락: int = 0
    장난감: int = 0
    교육: int = 0
    기타: int = 0

class HourlyData(BaseModel):
    hour: str
    purchases: int

class PopularProduct(BaseModel):
    name: str
    category: str
    count: int
    totalAmount: int
    avgPrice: float

class AlertItem(BaseModel):
    type: str  # 'warning', 'info', 'success'
    title: str
    message: str

class DashboardResponse(BaseModel):
    metrics: DashboardMetrics
    weeklyTrend: List[WeeklyTrendItem]
    categoryData: List[CategoryData]
    hourlyData: List[HourlyData]
    popularProducts: List[PopularProduct]
    alerts: List[AlertItem]
    lastUpdated: datetime

# 🔧 데이터베이스 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📈 데이터 분석 클래스
class PurchaseAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.now = datetime.now()
        self.one_week_ago = self.now - timedelta(days=7)
        self.two_weeks_ago = self.now - timedelta(days=14)
        
        # 총액 계산 컬럼 추가
        self.df['total_amount'] = self.df['price'] * self.df['cnt']
        
    def get_weekly_metrics(self) -> Dict[str, Any]:
        """주간 메트릭 계산"""
        # 이번 주 데이터
        this_week = self.df[self.df['timestamp'] >= self.one_week_ago]
        last_week = self.df[
            (self.df['timestamp'] >= self.two_weeks_ago) & 
            (self.df['timestamp'] < self.one_week_ago)
        ]
        
        # 총 소비액
        this_week_total = this_week['total_amount'].sum()
        last_week_total = last_week['total_amount'].sum()
        
        # 변화율 계산
        weekly_change = 0
        if last_week_total > 0:
            weekly_change = ((this_week_total - last_week_total) / last_week_total) * 100
            
        # 가장 인기 카테고리
        category_amounts = this_week.groupby('type')['total_amount'].sum()
        most_popular = category_amounts.idxmax() if not category_amounts.empty else "데이터 없음"
        
        # 교육 아이템 비중
        education_amount = this_week[this_week['type'] == '교육']['total_amount'].sum()
        education_ratio = (education_amount / this_week_total * 100) if this_week_total > 0 else 0
        
        # 평균 구매액
        total_purchases = len(this_week)
        avg_amount = int(this_week_total / total_purchases) if total_purchases > 0 else 0
        
        return {
            'thisWeekTotal': int(this_week_total),
            'weeklyChange': round(weekly_change, 1),
            'mostPopularCategory': most_popular,
            'educationRatio': round(education_ratio, 1),
            'totalPurchases': total_purchases,
            'avgPurchaseAmount': avg_amount
        }
    
    def get_weekly_trend(self) -> List[Dict[str, Any]]:
        """주간 일별 트렌드 분석"""
        trend_data = []
        days = ['일', '월', '화', '수', '목', '금', '토']
        
        for i in range(6, -1, -1):
            target_date = self.now - timedelta(days=i)
            day_name = days[target_date.weekday() + 1 if target_date.weekday() != 6 else 0]
            
            # 해당 날짜 데이터 필터링
            day_data = self.df[
                self.df['timestamp'].dt.date == target_date.date()
            ]
            
            # 카테고리별 합계
            category_sums = day_data.groupby('type')['total_amount'].sum()
            
            day_result = {'day': day_name}
            for category in ['간식', '오락', '장난감', '교육', '기타']:
                day_result[category] = int(category_sums.get(category, 0))
                
            trend_data.append(day_result)
            
        return trend_data
    
    def get_category_distribution(self) -> List[Dict[str, Any]]:
        """카테고리별 분포 분석"""
        this_week = self.df[self.df['timestamp'] >= self.one_week_ago]
        category_amounts = this_week.groupby('type')['total_amount'].sum()
        
        colors = {
            '간식': '#ff6b6b',
            '오락': '#4ecdc4',
            '장난감': '#45b7d1',
            '교육': '#96ceb4',
            '기타': '#ffeaa7'
        }
        
        return [
            {
                'name': category,
                'value': int(amount),
                'color': colors.get(category, '#gray')
            }
            for category, amount in category_amounts.items()
        ]
    
    def get_hourly_pattern(self) -> List[Dict[str, Any]]:
        """시간대별 구매 패턴"""
        this_week = self.df[self.df['timestamp'] >= self.one_week_ago]
        hourly_counts = this_week.groupby(this_week['timestamp'].dt.hour)['cnt'].sum()
        
        hourly_data = []
        for hour in range(24):
            hourly_data.append({
                'hour': f'{hour}시',
                'purchases': int(hourly_counts.get(hour, 0))
            })
            
        return hourly_data
    
    def get_popular_products(self, limit: int = 8) -> List[Dict[str, Any]]:
        """인기 상품 분석"""
        this_week = self.df[self.df['timestamp'] >= self.one_week_ago]
        
        # 상품별 집계
        product_stats = this_week.groupby(['name', 'type']).agg({
            'cnt': 'sum',
            'total_amount': 'sum',
            'price': 'mean'
        }).reset_index()
        
        product_stats = product_stats.sort_values('cnt', ascending=False).head(limit)
        
        return [
            {
                'name': row['name'],
                'category': row['type'],
                'count': int(row['cnt']),
                'totalAmount': int(row['total_amount']),
                'avgPrice': round(row['price'], 0)
            }
            for _, row in product_stats.iterrows()
        ]
    
    def generate_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, str]]:
        """알림 생성"""
        alerts = []
        this_week = self.df[self.df['timestamp'] >= self.one_week_ago]
        
        if len(this_week) == 0:
            return alerts
            
        # 카테고리별 비중 계산
        category_ratios = this_week.groupby('type')['total_amount'].sum() / this_week['total_amount'].sum()
        
        # 간식 과다 소비 체크
        snack_ratio = category_ratios.get('간식', 0)
        if snack_ratio > 0.4:
            alerts.append({
                'type': 'warning',
                'title': '간식 소비 주의',
                'message': f'이번 주 간식 구매가 전체의 {snack_ratio*100:.0f}%를 넘었어요. 균형 잡힌 소비를 권장해요!'
            })
        
        # 교육 아이템 부족 체크
        if metrics['educationRatio'] < 15:
            alerts.append({
                'type': 'info',
                'title': '교육 아이템 추천',
                'message': '교육 관련 구매가 적어요. 학습 도서나 교육 도구를 고려해보세요!'
            })
        
        # 긍정적 변화 감지
        if metrics['weeklyChange'] < -10:
            alerts.append({
                'type': 'success',
                'title': '절약 성공',
                'message': '지난 주보다 소비가 줄었어요. 훌륭한 절약 습관이에요! 🎉'
            })
            
        return alerts

# 🚀 API 엔드포인트들

@app.get("/")
async def root():
    return {"message": "아이 습관 분석 API 서버가 실행 중입니다!"}

@app.get("/api/dashboard/{child_id}", response_model=DashboardResponse)
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
        df = pd.DataFrame(result.fetchall(), columns=columns)
        
        if df.empty:
            raise HTTPException(status_code=404, detail="해당 아이의 구매 데이터가 없습니다.")
        
        # 데이터 타입 변환
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['price'] = df['price'].astype(int)
        df['cnt'] = df['cnt'].astype(int)
        
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

@app.get("/api/children")
async def get_children_list(db: Session = Depends(get_db)):
    """등록된 아이들 목록 조회"""
    try:
        query = text("SELECT DISTINCT child_id FROM purchasehistory ORDER BY child_id")
        result = db.execute(query)
        children = [{'child_id': row[0]} for row in result.fetchall()]
        return {"children": children}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"아이 목록 조회 중 오류: {str(e)}")

@app.get("/api/categories/stats/{child_id}")
async def get_category_stats(
    child_id: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """카테고리별 상세 통계"""
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        query = text("""
            SELECT type, 
                   COUNT(*) as purchase_count,
                   SUM(price * cnt) as total_amount,
                   AVG(price * cnt) as avg_amount,
                   SUM(cnt) as total_quantity
            FROM purchasehistory 
            WHERE child_id = :child_id 
            AND timestamp >= :start_date
            GROUP BY type
            ORDER BY total_amount DESC
        """)
        
        result = db.execute(query, {
            'child_id': child_id,
            'start_date': start_date
        })
        
        stats = []
        for row in result.fetchall():
            stats.append({
                'category': row[0],
                'purchaseCount': row[1],
                'totalAmount': int(row[2]),
                'avgAmount': round(float(row[3]), 2),
                'totalQuantity': row[4]
            })
            
        return {"categoryStats": stats}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"카테고리 통계 조회 중 오류: {str(e)}")

@app.get("/api/timeline/{child_id}")
async def get_purchase_timeline(
    child_id: str,
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """구매 타임라인 조회"""
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        query = text("""
            SELECT timestamp, type, name, price, cnt, (price * cnt) as total_amount
            FROM purchasehistory 
            WHERE child_id = :child_id 
            AND timestamp >= :start_date
            ORDER BY timestamp DESC
            LIMIT 50
        """)
        
        result = db.execute(query, {
            'child_id': child_id,
            'start_date': start_date
        })
        
        timeline = []
        for row in result.fetchall():
            timeline.append({
                'timestamp': row[0].isoformat(),
                'category': row[1],
                'productName': row[2],
                'price': row[3],
                'quantity': row[4],
                'totalAmount': int(row[5])
            })
            
        return {"timeline": timeline}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"타임라인 조회 중 오류: {str(e)}")

# 🔧 헬스체크 엔드포인트
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """서버 및 데이터베이스 상태 확인"""
    try:
        # DB 연결 테스트
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"서비스 이용 불가: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )

# 🚀 실행 방법
"""
1. 의존성 설치:
   pip install fastapi uvicorn sqlalchemy psycopg2-binary pandas numpy python-dotenv pydantic

2. 환경 변수 설정 (.env 파일):
   DATABASE_URL=postgresql://username:password@localhost:5432/database_name

3. 서버 실행:
   uvicorn main:app --reload --port 8000

4. API 문서 확인:
   http://localhost:8000/docs
"""