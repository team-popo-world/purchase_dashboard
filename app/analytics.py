from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 데이터 분석 클래스
class PurchaseAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.now = datetime.now()
        self.one_week_ago = self.now - timedelta(days=7)
        self.two_weeks_ago = self.now - timedelta(days=14)
        
        # 데이터 전처리
        if not self.df.empty:
            # 총액 계산 컬럼 추가
            self.df['total_amount'] = self.df['price'] * self.df['cnt']
            
            # label을 한국어 카테고리로 변환
            label_korean_mapping = {
                'FOOD': '먹이',      # 게임 캐릭터 먹이를 별도 카테고리로 분류
                'SNACK': '간식',
                'ENTERTAINMENT': '오락',
                'TOY': '장난감',
                'EDUCATION': '교육',
                'ETC': '기타'
            }
            
            # label_korean 컬럼 생성
            if 'label' in self.df.columns:
                self.df['label_korean'] = self.df['label'].map(label_korean_mapping).fillna('기타')
            else:
                self.df['label_korean'] = '기타'
        
    def get_weekly_metrics(self) -> Dict[str, Any]:
        """주간 메트릭 계산"""
        if self.df.empty:
            return {            'thisWeekTotal': 0,
            'weeklyChange': 0.0,
            'mostPopularCategory': "데이터 없음",
            'educationRatio': 0.0,
            'totalPurchases': 0,
            'avgPurchaseAmount': 0.0
            }
            
        # 이번 주 데이터
        this_week = self.df[self.df['timestamp'] >= self.one_week_ago]
        last_week = self.df[
            (self.df['timestamp'] >= self.two_weeks_ago) & 
            (self.df['timestamp'] < self.one_week_ago)
        ]
        
        # 총 소비액
        this_week_total = this_week['total_amount'].sum() if not this_week.empty else 0
        last_week_total = last_week['total_amount'].sum() if not last_week.empty else 0
        
        # 변화율 계산
        weekly_change = 0.0
        if last_week_total > 0:
            weekly_change = ((this_week_total - last_week_total) / last_week_total) * 100
            
        # 가장 인기 카테고리
        most_popular = "데이터 없음"
        if not this_week.empty:
            # label_korean을 사용하여 카테고리별 총액 계산
            category_amounts = this_week.groupby('label_korean')['total_amount'].sum()
            if not category_amounts.empty:
                most_popular = category_amounts.idxmax()
        
        # 교육 아이템 비중
        education_ratio = 0.0
        if not this_week.empty and this_week_total > 0:
            education_amount = this_week[this_week['label_korean'] == '교육']['total_amount'].sum()
            education_ratio = (education_amount / this_week_total * 100)
        
        # 평균 구매액
        total_purchases = len(this_week)
        avg_amount = float(this_week_total / total_purchases) if total_purchases > 0 else 0.0
        
        return {
            'thisWeekTotal': int(this_week_total),
            'weeklyChange': round(float(weekly_change), 1),
            'mostPopularCategory': str(most_popular),
            'educationRatio': round(float(education_ratio), 1),
            'totalPurchases': int(total_purchases),
            'avgPurchaseAmount': round(float(avg_amount), 2)
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
            day_result = {'day': day_name}
            
            if not day_data.empty:
                category_sums = day_data.groupby('label_korean')['total_amount'].sum()
                # 모든 카테고리 포함 (먹이 카테고리 추가)
                categories = ['간식', '오락', '장난감', '교육', '먹이', '기타']
                for category in categories:
                    day_result[category] = int(category_sums.get(category, 0))
            else:
                for category in ['간식', '오락', '장난감', '교육', '먹이', '기타']:
                    day_result[category] = 0
                
            trend_data.append(day_result)
            
        return trend_data
    
    def get_category_distribution(self) -> List[Dict[str, Any]]:
        """카테고리별 분포 분석"""
        this_week = self.df[self.df['timestamp'] >= self.one_week_ago]
        
        if this_week.empty:
            return []
        
        category_amounts = this_week.groupby('label_korean')['total_amount'].sum()
            
        colors = {
            '간식': '#ff6b6b',
            '오락': '#4ecdc4',
            '장난감': '#45b7d1',
            '교육': '#96ceb4',
            '먹이': '#ff9f40',  # 오렌지색으로 게임 캐릭터 먹이 표시
            '기타': '#ffeaa7'
        }
        
        result = []
        for category, amount in category_amounts.items():
            result.append({
                'name': category,
                'value': int(amount),
                'color': colors.get(category, '#gray')
            })
            
        return result
    
    def get_hourly_pattern(self) -> List[Dict[str, Any]]:
        """시간대별 구매 패턴"""
        this_week = self.df[self.df['timestamp'] >= self.one_week_ago]
        
        hourly_data = []
        if not this_week.empty:
            hourly_counts = this_week.groupby(this_week['timestamp'].dt.hour).size()
            for hour in range(24):
                hourly_data.append({
                    'hour': f'{hour}시',
                    'purchases': int(hourly_counts.get(hour, 0))
                })
        else:
            for hour in range(24):
                hourly_data.append({
                    'hour': f'{hour}시',
                    'purchases': 0
                })
            
        return hourly_data
    
    def get_popular_products(self, limit: int = 8) -> List[Dict[str, Any]]:
        """인기 상품 분석"""
        this_week = self.df[self.df['timestamp'] >= self.one_week_ago]
        
        if this_week.empty:
            return []
        
        # 상품별 집계
        product_stats = this_week.groupby(['name', 'label_korean']).agg({
            'cnt': 'sum',
            'total_amount': 'sum',
            'price': 'mean'
        }).reset_index()
        product_stats.rename(columns={'label_korean': 'category'}, inplace=True)
        
        product_stats = product_stats.sort_values('cnt', ascending=False).head(limit)
        
        return [
            {
                'name': row['name'],
                'category': '교육' if row['category'] == '교육 및 문구' else row['category'],
                'count': int(row['cnt']),
                'totalAmount': int(row['total_amount']),
                'avgPrice': round(float(row['price']), 1)
            }
            for _, row in product_stats.iterrows()
        ]
    
    def generate_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, str]]:
        """개선된 알림 생성"""
        alerts = []
        this_week = self.df[self.df['timestamp'] >= self.one_week_ago]
        
        # 데이터 없음 처리
        if this_week.empty:
            alerts.append({
                'type': 'info',
                'title': '첫 구매를 시작해보세요',
                'message': '아직 구매 데이터가 없어요. 첫 번째 아이템을 구매해보세요!'
            })
            return alerts
            
        # 카테고리별 비중 계산
        total_amount = this_week['total_amount'].sum()
        if total_amount > 0:
            category_ratios = this_week.groupby('label_korean')['total_amount'].sum() / total_amount
            # 간식 과다 소비 체크
            snack_ratio = category_ratios.get('간식', 0)
            if snack_ratio > 0.5:
                alerts.append({
                    'type': 'warning',
                    'title': '간식 소비 주의',
                    'message': f'이번 주 간식 구매가 전체의 {snack_ratio*100:.0f}%를 넘었어요. 균형 잡힌 소비를 권장해요!'
                })
            elif snack_ratio > 0.4:
                alerts.append({
                    'type': 'warning',
                    'title': '간식 소비 주의',
                    'message': f'이번 주 간식 구매가 전체의 {snack_ratio*100:.0f}%를 넘었어요. 균형 잡힌 소비를 권장해요!'
                })
            
            # 게임 캐릭터 먹이 소비 체크
            food_ratio = category_ratios.get('먹이', 0)
            if food_ratio > 0.3:
                alerts.append({
                    'type': 'info',
                    'title': '게임 먹이 관리',
                    'message': f'게임 캐릭터 먹이 구매가 전체의 {food_ratio*100:.0f}%예요. 게임 시간과 함께 관리해보세요! 🎮'
                })
            elif food_ratio > 0.15:
                alerts.append({
                    'type': 'info',
                    'title': '게임 균형 유지',
                    'message': '게임 캐릭터를 잘 돌보고 있어요. 다른 활동과 균형을 맞춰보세요! 🐾'
                })
            
            # 교육 아이템 관련 알림
            education_ratio = metrics.get('educationRatio', 0)
            if education_ratio >= 30:
                alerts.append({
                    'type': 'success',
                    'title': '교육 아이템 우수',
                    'message': '교육 관련 구매 비중이 목표치를 달성했어요! 🎉'
                })
            elif education_ratio >= 20:
                alerts.append({
                    'type': 'success',
                    'title': '교육 목표 달성',
                    'message': '교육 아이템 구매 목표를 달성했어요! 🎓'
                })
            elif education_ratio < 10:
                alerts.append({
                    'type': 'info',
                    'title': '교육 아이템 추천',
                    'message': '교육 관련 구매가 적어요. 학습 도서나 교육 도구를 고려해보세요!'
                })
            
            # 균형잡힌 소비 체크
            balanced_categories = sum(1 for ratio in category_ratios.values if 0.1 <= ratio <= 0.4)
            if balanced_categories >= 4:
                alerts.append({
                    'type': 'success',
                    'title': '균형잡힌 소비',
                    'message': '모든 카테고리에서 균형잡힌 소비를 보이고 있어요! 👏'
                })
        
        # 주간 변화 관련 알림
        weekly_change = metrics.get('weeklyChange', 0)
        if weekly_change < -15:
            alerts.append({
                'type': 'success',
                'title': '절약 성공',
                'message': f'지난 주보다 소비가 {abs(weekly_change):.1f}% 줄었어요. 훌륭한 절약 습관이에요! 🎉'
            })
        elif weekly_change > 30:
            alerts.append({
                'type': 'warning',
                'title': '소비 증가 주의',
                'message': f'지난 주보다 소비가 {weekly_change:.1f}% 늘었어요. 소비 패턴을 점검해보세요.'
            })
        
        # 구매 빈도 체크
        total_purchases = metrics.get('totalPurchases', 0)
        if total_purchases > 50:
            alerts.append({
                'type': 'info',
                'title': '구매 빈도 점검',
                'message': f'이번 주 총 {total_purchases}번 구매했어요. 충동 구매는 줄이고 계획적으로 구매해보세요.'
            })
            
        return alerts
