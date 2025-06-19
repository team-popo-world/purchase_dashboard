from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# 응답 모델들
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
    먹이: int = 0
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

# 새로운 모델들 추가
class ChildInfo(BaseModel):
    child_id: str

class ChildrenResponse(BaseModel):
    children: List[ChildInfo]

class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime

# ML 분석 결과 모델들
class PersonalityType(BaseModel):
    name: str
    description: str
    characteristics: List[str]
    color: str
    confidence: float

class PersonalityAnalysis(BaseModel):
    personality_type: PersonalityType
    features: Dict[str, float]
    personality_score: Dict[str, float]

class AnomalyAlert(BaseModel):
    type: str
    title: str
    description: str
    severity: str
    icon: str
    confidence: float
    details: Dict[str, Any]

class AnomalyAnalysis(BaseModel):
    is_anomaly: bool
    anomaly_score: float
    alerts: List[AnomalyAlert]

class MLAnalysis(BaseModel):
    personality: PersonalityAnalysis
    anomaly: AnomalyAnalysis
    recommendations: List[str]
    last_model_update: Optional[datetime]

# 확장된 대시보드 응답
class EnhancedDashboardResponse(BaseModel):
    metrics: DashboardMetrics
    weeklyTrend: List[WeeklyTrendItem]
    categoryData: List[CategoryData]
    hourlyData: List[HourlyData]
    popularProducts: List[PopularProduct]
    alerts: List[AlertItem]
    ml_analysis: MLAnalysis
    lastUpdated: datetime
