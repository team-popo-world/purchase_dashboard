from pydantic import BaseModel
from typing import List
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
