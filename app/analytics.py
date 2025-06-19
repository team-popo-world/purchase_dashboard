from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from .ml import PersonalityAnalyzer, AnomalyDetector

# 데이터 분석 클래스
class PurchaseAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.now = datetime.now()
        self.one_week_ago = self.now - timedelta(days=7)
        self.two_weeks_ago = self.now - timedelta(days=14)
        
        # ML 모델 초기화
        self.personality_analyzer = PersonalityAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        
        # 총액 계산 컬럼 추가
        if not self.df.empty:
            self.df['total_amount'] = self.df['price'] * self.df['cnt']
        
    def get_weekly_metrics(self) -> Dict[str, Any]:
        """주간 메트릭 계산"""
        if self.df.empty:
            return {
                'thisWeekTotal': 0,
                'weeklyChange': 0.0,
                'mostPopularCategory': "데이터 없음",
                'educationRatio': 0.0,
                'totalPurchases': 0,
                'avgPurchaseAmount': 0
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
            category_amounts = this_week.groupby('type')['total_amount'].sum()
            if not category_amounts.empty:
                most_popular = category_amounts.idxmax()
        
        # 교육 아이템 비중 - label_korean을 사용
        education_ratio = 0.0
        if not this_week.empty and this_week_total > 0:
            # label_korean 컬럼을 사용하여 교육 카테고리 필터링
            if 'label_korean' in this_week.columns:
                education_amount = this_week[this_week['label_korean'] == '교육 및 문구']['total_amount'].sum()
            else:
                # 호환성을 위해 type 컬럼도 체크
                education_amount = this_week[this_week['type'] == '교육']['total_amount'].sum()
            education_ratio = (education_amount / this_week_total * 100)
        
        # 평균 구매액
        total_purchases = len(this_week)
        avg_amount = int(this_week_total / total_purchases) if total_purchases > 0 else 0
        
        return {
            'thisWeekTotal': int(this_week_total),
            'weeklyChange': round(float(weekly_change), 1),
            'mostPopularCategory': str(most_popular),
            'educationRatio': round(float(education_ratio), 1),
            'totalPurchases': int(total_purchases),
            'avgPurchaseAmount': int(avg_amount)
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
            
            # 카테고리별 합계 - label_korean 사용
            day_result = {'day': day_name}
            
            if not day_data.empty:
                if 'label_korean' in day_data.columns:
                    category_sums = day_data.groupby('label_korean')['total_amount'].sum()
                    for category in ['먹이', '간식', '오락', '장난감', '교육 및 문구', '기타']:
                        korean_name = category if category != '교육 및 문구' else '교육'
                        day_result[korean_name] = int(category_sums.get(category, 0))
                else:
                    # 호환성을 위한 기존 방식
                    category_sums = day_data.groupby('type')['total_amount'].sum()
                    for category in ['먹이', '간식', '오락', '장난감', '교육', '기타']:
                        day_result[category] = int(category_sums.get(category, 0))
            else:
                for category in ['먹이', '간식', '오락', '장난감', '교육', '기타']:
                    day_result[category] = 0
                
            trend_data.append(day_result)
            
        return trend_data
    
    def get_category_distribution(self) -> List[Dict[str, Any]]:
        """카테고리별 분포 분석"""
        this_week = self.df[self.df['timestamp'] >= self.one_week_ago]
        
        if this_week.empty:
            return []
        
        # label_korean 컬럼이 있으면 사용, 없으면 type 사용
        if 'label_korean' in this_week.columns:
            category_amounts = this_week.groupby('label_korean')['total_amount'].sum()
        else:
            category_amounts = this_week.groupby('type')['total_amount'].sum()
            
        colors = {
            '먹이': '#ff9f43',
            '간식': '#ff6b6b',
            '오락': '#4ecdc4',
            '장난감': '#45b7d1',
            '교육 및 문구': '#96ceb4',
            '교육': '#96ceb4',  # 호환성
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
        
        # 상품별 집계 - label_korean 또는 type 사용
        if 'label_korean' in this_week.columns:
            product_stats = this_week.groupby(['name', 'label_korean']).agg({
                'cnt': 'sum',
                'total_amount': 'sum',
                'price': 'mean'
            }).reset_index()
            product_stats.rename(columns={'label_korean': 'category'}, inplace=True)
        else:
            product_stats = this_week.groupby(['name', 'type']).agg({
                'cnt': 'sum',
                'total_amount': 'sum',
                'price': 'mean'
            }).reset_index()
            product_stats.rename(columns={'type': 'category'}, inplace=True)
        
        product_stats = product_stats.sort_values('cnt', ascending=False).head(limit)
        
        return [
            {
                'name': row['name'],
                'category': row['category'],
                'count': int(row['cnt']),
                'totalAmount': int(row['total_amount']),
                'avgPrice': round(float(row['price']), 0)
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
            
        # 카테고리별 비중 계산 - label_korean 또는 type 사용
        total_amount = this_week['total_amount'].sum()
        if total_amount > 0:
            if 'label_korean' in this_week.columns:
                category_ratios = this_week.groupby('label_korean')['total_amount'].sum() / total_amount
                # 간식 과다 소비 체크
                snack_ratio = category_ratios.get('간식', 0)
            else:
                category_ratios = this_week.groupby('type')['total_amount'].sum() / total_amount
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
    
    def get_personality_insights(self) -> Dict[str, Any]:
        """아이 성향 분석 결과"""
        return self.personality_analyzer.get_personality_insights(self.df)
    
    def get_anomaly_detection(self) -> Dict[str, Any]:
        """이상 행동 탐지 결과"""
        return self.anomaly_detector.detect_anomalies(self.df)
    
    def get_ml_enhanced_alerts(self) -> List[Dict[str, Any]]:
        """ML 기반 강화된 알림"""
        # 기존 알림
        basic_alerts = self.generate_smart_alerts()
        
        # 이상 탐지 알림
        anomaly_alerts = self.anomaly_detector.get_anomaly_alerts(self.df)
        
        # 성향 기반 맞춤 알림
        personality_alerts = self._get_personality_based_alerts()
        
        # 모든 알림 통합 및 중복 제거
        all_alerts = basic_alerts + anomaly_alerts + personality_alerts
        
        # 우선순위별 정렬 (alert > warning > success > info)
        priority_order = {'alert': 4, 'warning': 3, 'success': 2, 'info': 1}
        sorted_alerts = sorted(
            all_alerts, 
            key=lambda x: priority_order.get(x['type'], 0), 
            reverse=True
        )
        
        # 최대 8개까지만 반환
        return sorted_alerts[:8]
    
    def _get_personality_based_alerts(self) -> List[Dict[str, Any]]:
        """성향 기반 맞춤 알림"""
        try:
            personality_result = self.personality_analyzer.predict_personality(self.df)
            personality_type = personality_result.get('personality_type', '')
            
            alerts = []
            
            # 성향별 맞춤 메시지
            if '학습지향형' in personality_type:
                education_ratio = self.get_weekly_metrics().get('educationRatio', 0)
                if education_ratio < 20:
                    alerts.append({
                        'type': 'info',
                        'title': '🎓 학습 성향 아이 맞춤 제안',
                        'message': '교육적 가치가 높은 아이템을 더 추가해보세요!'
                    })
            
            elif '활동적' in personality_type:
                toy_ratio = sum(1 for item in self.df['type'] if item in ['오락', '장난감']) / len(self.df) * 100 if not self.df.empty else 0
                if toy_ratio < 30:
                    alerts.append({
                        'type': 'info',
                        'title': '⚡ 활동적 성향 아이 맞춤 제안',
                        'message': '야외 활동이나 체험형 아이템을 고려해보세요!'
                    })
            
            elif '창의적' in personality_type:
                creative_items = len(self.df[self.df['name'].str.contains('만들기|그리기|미술|창작', na=False)])
                if creative_items == 0:
                    alerts.append({
                        'type': 'info',
                        'title': '🎨 창의적 성향 아이 맞춤 제안',
                        'message': '창작 활동을 할 수 있는 아이템을 추가해보세요!'
                    })
            
            return alerts
            
        except Exception:
            return []
    
    def get_comprehensive_analysis(self) -> Dict[str, Any]:
        """종합 분석 결과"""
        basic_metrics = self.get_weekly_metrics()
        weekly_trend = self.get_weekly_trend()
        category_data = self.get_category_analysis()
        hourly_data = self.get_hourly_analysis()
        popular_products = self.get_popular_products()
        
        # ML 분석 결과
        try:
            personality_insights = self.get_personality_insights()
            anomaly_detection = self.get_anomaly_detection()
            ml_alerts = self.get_ml_enhanced_alerts()
        except Exception:
            # ML 기능 실패 시 기본값
            personality_insights = {'personality': {'personality_type': '분석 중'}}
            anomaly_detection = {'anomalies_detected': False, 'risk_level': 'low'}
            ml_alerts = self.generate_smart_alerts()
        
        return {
            'metrics': basic_metrics,
            'weeklyTrend': weekly_trend,
            'categoryData': category_data,
            'hourlyData': hourly_data,
            'popularProducts': popular_products,
            'alerts': ml_alerts,
            'personalityInsights': personality_insights,
            'anomalyDetection': anomaly_detection,
            'lastUpdated': self.now
        }
