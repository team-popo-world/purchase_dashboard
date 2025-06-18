from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd

# 데이터 분석 클래스
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
