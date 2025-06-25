from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# 응답 모델들
class DashboardMetrics(BaseModel):
    thisWeekTotal: int
    weeklyChange: float
    mostPopularCategory: str
    educationRatio: float
    totalPurchases: int
    avgPurchaseAmount: float
    
class CategoryData(BaseModel):
    name: str
    value: int
    color: str

class WeeklyTrendItem(BaseModel):
    day: str
    간식: int = 0
    오락: int = 0
    장난감: int = 0
    교육_및_문구: int = Field(0, alias='교육 및 문구')
    먹이: int = 0  # 게임 캐릭터 먹이 카테고리 추가
    기타: int = 0
    
    class Config:
        populate_by_name = True

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
