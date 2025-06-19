"""
이상 행동 탐지 시스템
아이의 평상시 구매 패턴과 다른 이상 행동을 감지하고 알림을 제공합니다.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.covariance import EllipticEnvelope
import joblib
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class AnomalyDetector:
    def __init__(self):
        self.isolation_forest = IsolationForest(
            contamination=0.1, 
            random_state=42,
            n_estimators=100
        )
        self.elliptic_envelope = EllipticEnvelope(
            contamination=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.model_path = Path("app/ml/models")
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # 이상 행동 유형 정의
        self.anomaly_types = {
            'spending_spike': {
                'title': '급격한 지출 증가',
                'description': '평소보다 지출이 크게 증가했습니다',
                'severity': 'warning',
                'icon': '💰'
            },
            'category_shift': {
                'title': '구매 패턴 변화',
                'description': '평소와 다른 카테고리의 구매가 증가했습니다',
                'severity': 'info',
                'icon': '🔄'
            },
            'frequency_change': {
                'title': '구매 빈도 변화',
                'description': '구매 빈도가 급격히 변화했습니다',
                'severity': 'warning',
                'icon': '📊'
            },
            'time_pattern_shift': {
                'title': '시간 패턴 변화',
                'description': '평소와 다른 시간대에 구매가 집중되었습니다',
                'severity': 'info',
                'icon': '⏰'
            },
            'impulse_buying': {
                'title': '충동 구매 의심',
                'description': '짧은 시간에 많은 구매가 발생했습니다',
                'severity': 'warning',
                'icon': '⚡'
            },
            'emotional_shopping': {
                'title': '감정적 소비 패턴',
                'description': '스트레스나 감정 변화로 인한 소비 패턴이 감지되었습니다',
                'severity': 'alert',
                'icon': '😔'
            }
        }
    
    def extract_behavioral_features(self, df: pd.DataFrame, window_days: int = 7) -> Dict[str, float]:
        """행동 분석을 위한 특성 추출"""
        if df.empty:
            return self._get_default_behavioral_features()
        
        # 기간별 데이터 분할
        now = datetime.now()
        recent_period = now - timedelta(days=window_days)
        
        recent_data = df[pd.to_datetime(df['timestamp']) >= recent_period]
        historical_data = df[pd.to_datetime(df['timestamp']) < recent_period]
        
        if recent_data.empty:
            return self._get_default_behavioral_features()
        
        # 최근 기간 특성
        recent_features = self._calculate_period_features(recent_data)
        
        # 기준 특성 (과거 데이터가 있는 경우)
        if not historical_data.empty:
            historical_features = self._calculate_period_features(historical_data)
            # 변화량 계산
            change_features = self._calculate_change_features(recent_features, historical_features)
        else:
            change_features = {}
        
        # 전체 특성 통합
        features = {
            **recent_features,
            **change_features,
            'data_availability': len(historical_data) / len(df) if len(df) > 0 else 0
        }
        
        return features
    
    def _calculate_period_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """특정 기간의 구매 특성 계산"""
        if df.empty:
            return self._get_default_period_features()
        
        # 기본 통계
        df['total_amount'] = df['price'] * df['cnt']
        total_spent = df['total_amount'].sum()
        total_purchases = len(df)
        avg_amount = total_spent / total_purchases if total_purchases > 0 else 0
        
        # 카테고리 분포
        category_dist = df['type'].value_counts(normalize=True).to_dict()
        
        # 시간 패턴
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        df['weekday'] = pd.to_datetime(df['timestamp']).dt.weekday
        
        time_variance = df['hour'].var() if len(df) > 1 else 0
        weekday_variance = df['weekday'].var() if len(df) > 1 else 0
        
        # 구매 간격
        df_sorted = df.sort_values('timestamp')
        time_diffs = pd.to_datetime(df_sorted['timestamp']).diff().dt.total_seconds() / 3600  # 시간 단위
        avg_interval = time_diffs.mean() if len(time_diffs) > 1 else 24
        min_interval = time_diffs.min() if len(time_diffs) > 1 else 24
        
        # 가격 분산
        price_variance = df['price'].var() if len(df) > 1 else 0
        price_range = df['price'].max() - df['price'].min() if len(df) > 1 else 0
        
        # 충동성 지표 (짧은 시간 내 다수 구매)
        impulse_score = len(df[time_diffs < 1]) / total_purchases if total_purchases > 0 else 0
        
        features = {
            'total_spent': total_spent,
            'total_purchases': total_purchases,
            'avg_amount': avg_amount,
            'time_variance': time_variance,
            'weekday_variance': weekday_variance,
            'avg_interval': avg_interval,
            'min_interval': min_interval,
            'price_variance': price_variance,
            'price_range': price_range,
            'impulse_score': impulse_score,
            'unique_items': df['name'].nunique(),
            'unique_categories': df['type'].nunique()
        }
        
        # 카테고리별 비율 추가
        for category in ['간식', '오락', '장난감', '교육', '기타']:
            features[f'{category}_ratio'] = category_dist.get(category, 0) * 100
        
        return features
    
    def _calculate_change_features(self, recent: Dict, historical: Dict) -> Dict[str, float]:
        """최근 데이터와 과거 데이터의 변화량 계산"""
        changes = {}
        
        key_metrics = [
            'total_spent', 'total_purchases', 'avg_amount', 'time_variance',
            'avg_interval', 'price_variance', 'impulse_score'
        ]
        
        for metric in key_metrics:
            recent_val = recent.get(metric, 0)
            historical_val = historical.get(metric, 0)
            
            if historical_val != 0:
                change_pct = ((recent_val - historical_val) / historical_val) * 100
            else:
                change_pct = 100 if recent_val > 0 else 0
            
            changes[f'{metric}_change'] = change_pct
        
        # 카테고리 변화
        for category in ['간식', '오락', '장난감', '교육', '기타']:
            recent_ratio = recent.get(f'{category}_ratio', 0)
            historical_ratio = historical.get(f'{category}_ratio', 0)
            changes[f'{category}_shift'] = recent_ratio - historical_ratio
        
        return changes
    
    def _get_default_behavioral_features(self) -> Dict[str, float]:
        """기본 행동 특성값"""
        features = {
            'total_spent': 0, 'total_purchases': 0, 'avg_amount': 0,
            'time_variance': 0, 'weekday_variance': 0, 'avg_interval': 24,
            'min_interval': 24, 'price_variance': 0, 'price_range': 0,
            'impulse_score': 0, 'unique_items': 0, 'unique_categories': 0,
            'data_availability': 0
        }
        
        for category in ['간식', '오락', '장난감', '교육', '기타']:
            features[f'{category}_ratio'] = 0
            features[f'{category}_shift'] = 0
        
        for metric in ['total_spent', 'total_purchases', 'avg_amount', 'time_variance',
                      'avg_interval', 'price_variance', 'impulse_score']:
            features[f'{metric}_change'] = 0
        
        return features
    
    def _get_default_period_features(self) -> Dict[str, float]:
        """기본 기간 특성값"""
        features = {
            'total_spent': 0, 'total_purchases': 0, 'avg_amount': 0,
            'time_variance': 0, 'weekday_variance': 0, 'avg_interval': 24,
            'min_interval': 24, 'price_variance': 0, 'price_range': 0,
            'impulse_score': 0, 'unique_items': 0, 'unique_categories': 0
        }
        
        for category in ['간식', '오락', '장난감', '교육', '기타']:
            features[f'{category}_ratio'] = 0
        
        return features
    
    def train_anomaly_model(self, historical_data: List[pd.DataFrame]) -> None:
        """과거 데이터로 이상 탐지 모델 훈련"""
        if not historical_data:
            return
        
        # 모든 기간의 특성 추출
        all_features = []
        for period_data in historical_data:
            features = self.extract_behavioral_features(period_data)
            all_features.append(list(features.values()))
        
        if len(all_features) < 5:  # 최소 데이터 요구사항
            return
        
        # 정규화
        X = np.array(all_features)
        X_scaled = self.scaler.fit_transform(X)
        
        # 모델 훈련
        self.isolation_forest.fit(X_scaled)
        
        # 안정적인 데이터가 충분한 경우에만 EllipticEnvelope 사용
        if len(all_features) >= 10:
            try:
                self.elliptic_envelope.fit(X_scaled)
            except:
                pass  # 수렴하지 않는 경우 건너뛰기
        
        # 모델 저장
        self._save_anomaly_models()
    
    def detect_anomalies(self, df: pd.DataFrame) -> Dict[str, Any]:
        """이상 행동 탐지"""
        features = self.extract_behavioral_features(df)
        
        # 기본 규칙 기반 탐지
        rule_based_anomalies = self._detect_rule_based_anomalies(features, df)
        
        # 머신러닝 기반 탐지 (모델이 있는 경우)
        ml_based_anomalies = []
        try:
            self._load_anomaly_models()
            ml_based_anomalies = self._detect_ml_based_anomalies(features)
        except:
            pass  # 모델이 없거나 로드에 실패한 경우
        
        # 모든 이상 징후 통합
        all_anomalies = rule_based_anomalies + ml_based_anomalies
        
        # 중복 제거 및 우선순위 정렬
        unique_anomalies = self._deduplicate_and_prioritize(all_anomalies)
        
        result = {
            'anomalies_detected': len(unique_anomalies) > 0,
            'anomaly_count': len(unique_anomalies),
            'anomalies': unique_anomalies,
            'risk_level': self._calculate_risk_level(unique_anomalies),
            'summary': self._generate_summary(unique_anomalies),
            'recommendations': self._generate_recommendations(unique_anomalies)
        }
        
        return result
    
    def _detect_rule_based_anomalies(self, features: Dict, df: pd.DataFrame) -> List[Dict]:
        """규칙 기반 이상 탐지"""
        anomalies = []
        
        # 1. 급격한 지출 증가
        spending_change = features.get('total_spent_change', 0)
        if spending_change > 200:  # 200% 이상 증가
            anomalies.append({
                'type': 'spending_spike',
                'severity': 'warning',
                'confidence': min(spending_change / 300, 1.0),
                'details': f'지출이 {spending_change:.1f}% 증가했습니다',
                'timestamp': datetime.now()
            })
        
        # 2. 구매 빈도 급변
        frequency_change = features.get('total_purchases_change', 0)
        if abs(frequency_change) > 150:  # 150% 이상 변화
            anomalies.append({
                'type': 'frequency_change',
                'severity': 'warning',
                'confidence': min(abs(frequency_change) / 200, 1.0),
                'details': f'구매 빈도가 {frequency_change:.1f}% 변화했습니다',
                'timestamp': datetime.now()
            })
        
        # 3. 카테고리 급격한 변화
        for category in ['간식', '오락', '장난감', '교육', '기타']:
            shift = features.get(f'{category}_shift', 0)
            if abs(shift) > 30:  # 30% 이상 비중 변화
                anomalies.append({
                    'type': 'category_shift',
                    'severity': 'info',
                    'confidence': min(abs(shift) / 50, 1.0),
                    'details': f'{category} 카테고리 비중이 {shift:+.1f}% 변화했습니다',
                    'timestamp': datetime.now()
                })
        
        # 4. 충동 구매 패턴
        impulse_score = features.get('impulse_score', 0)
        if impulse_score > 0.3:  # 30% 이상이 1시간 내 구매
            anomalies.append({
                'type': 'impulse_buying',
                'severity': 'warning',
                'confidence': min(impulse_score / 0.5, 1.0),
                'details': f'구매의 {impulse_score*100:.1f}%가 짧은 시간 내에 발생했습니다',
                'timestamp': datetime.now()
            })
        
        # 5. 시간 패턴 변화
        time_variance_change = features.get('time_variance_change', 0)
        if abs(time_variance_change) > 100:
            anomalies.append({
                'type': 'time_pattern_shift',
                'severity': 'info',
                'confidence': min(abs(time_variance_change) / 150, 1.0),
                'details': '구매 시간 패턴이 평소와 다릅니다',
                'timestamp': datetime.now()
            })
        
        # 6. 감정적 소비 패턴 (복합 지표)
        emotional_indicators = [
            impulse_score > 0.25,
            spending_change > 150,
            features.get('간식_shift', 0) > 20,  # 간식 급증
            features.get('min_interval', 24) < 2  # 매우 짧은 구매 간격
        ]
        
        if sum(emotional_indicators) >= 2:
            anomalies.append({
                'type': 'emotional_shopping',
                'severity': 'alert',
                'confidence': sum(emotional_indicators) / 4,
                'details': '감정적 변화로 인한 소비 패턴이 감지되었습니다',
                'timestamp': datetime.now()
            })
        
        return anomalies
    
    def _detect_ml_based_anomalies(self, features: Dict) -> List[Dict]:
        """머신러닝 기반 이상 탐지"""
        anomalies = []
        
        feature_vector = np.array([list(features.values())]).reshape(1, -1)
        feature_scaled = self.scaler.transform(feature_vector)
        
        # Isolation Forest 예측
        isolation_prediction = self.isolation_forest.predict(feature_scaled)[0]
        isolation_score = self.isolation_forest.decision_function(feature_scaled)[0]
        
        if isolation_prediction == -1:  # 이상치로 분류
            confidence = min(abs(isolation_score) / 0.3, 1.0)
            anomalies.append({
                'type': 'ml_detected_anomaly',
                'severity': 'warning',
                'confidence': confidence,
                'details': f'AI가 이상 패턴을 감지했습니다 (점수: {isolation_score:.3f})',
                'timestamp': datetime.now()
            })
        
        return anomalies
    
    def _deduplicate_and_prioritize(self, anomalies: List[Dict]) -> List[Dict]:
        """중복 제거 및 우선순위 정렬"""
        if not anomalies:
            return []
        
        # 심각도별 우선순위
        severity_order = {'alert': 3, 'warning': 2, 'info': 1}
        
        # 정렬: 심각도 > 신뢰도 순
        sorted_anomalies = sorted(
            anomalies,
            key=lambda x: (severity_order.get(x['severity'], 0), x['confidence']),
            reverse=True
        )
        
        # 최대 5개까지만 반환
        return sorted_anomalies[:5]
    
    def _calculate_risk_level(self, anomalies: List[Dict]) -> str:
        """전체 위험 수준 계산"""
        if not anomalies:
            return 'low'
        
        alert_count = sum(1 for a in anomalies if a['severity'] == 'alert')
        warning_count = sum(1 for a in anomalies if a['severity'] == 'warning')
        
        if alert_count > 0:
            return 'high'
        elif warning_count >= 2:
            return 'medium'
        elif warning_count > 0:
            return 'medium'
        else:
            return 'low'
    
    def _generate_summary(self, anomalies: List[Dict]) -> str:
        """이상 징후 요약"""
        if not anomalies:
            return "정상적인 구매 패턴을 보이고 있습니다."
        
        alert_count = sum(1 for a in anomalies if a['severity'] == 'alert')
        warning_count = sum(1 for a in anomalies if a['severity'] == 'warning')
        
        if alert_count > 0:
            return f"주의가 필요한 {alert_count}개의 패턴이 감지되었습니다."
        elif warning_count > 0:
            return f"{warning_count}개의 변화 패턴이 관찰되었습니다."
        else:
            return "일부 변화가 있지만 정상 범위 내입니다."
    
    def _generate_recommendations(self, anomalies: List[Dict]) -> List[str]:
        """이상 징후별 권장사항"""
        recommendations = set()
        
        for anomaly in anomalies:
            anomaly_type = anomaly['type']
            
            if anomaly_type == 'spending_spike':
                recommendations.add("예산 한도를 다시 검토해보세요")
                recommendations.add("아이와 소비 계획을 함께 세워보세요")
            
            elif anomaly_type == 'impulse_buying':
                recommendations.add("구매 전 잠시 생각할 시간을 가져보세요")
                recommendations.add("구매 목록을 미리 작성하는 습관을 만들어보세요")
            
            elif anomaly_type == 'emotional_shopping':
                recommendations.add("아이의 감정 상태를 살펴보세요")
                recommendations.add("스트레스나 변화가 있었는지 확인해보세요")
                recommendations.add("감정을 표현할 다른 방법을 찾아보세요")
            
            elif anomaly_type == 'category_shift':
                recommendations.add("새로운 관심사가 생겼는지 대화해보세요")
                recommendations.add("카테고리 균형을 맞춰보세요")
            
            elif anomaly_type == 'frequency_change':
                recommendations.add("구매 패턴의 변화 원인을 파악해보세요")
                recommendations.add("규칙적인 구매 스케줄을 만들어보세요")
        
        # 일반적인 권장사항 추가
        if anomalies:
            recommendations.add("정기적으로 구매 패턴을 리뷰해보세요")
        
        return list(recommendations)
    
    def get_anomaly_alerts(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """알림용 이상 징후 정보"""
        detection_result = self.detect_anomalies(df)
        alerts = []
        
        if not detection_result['anomalies_detected']:
            return alerts
        
        for anomaly in detection_result['anomalies']:
            anomaly_info = self.anomaly_types.get(anomaly['type'], {
                'title': '패턴 변화 감지',
                'description': '구매 패턴에 변화가 있습니다',
                'severity': anomaly['severity'],
                'icon': '🔍'
            })
            
            alert = {
                'type': anomaly['severity'],
                'title': f"{anomaly_info['icon']} {anomaly_info['title']}",
                'message': anomaly.get('details', anomaly_info['description']),
                'confidence': anomaly['confidence'],
                'timestamp': anomaly['timestamp'],
                'recommendations': self._get_specific_recommendations(anomaly['type'])
            }
            
            alerts.append(alert)
        
        return alerts
    
    def _get_specific_recommendations(self, anomaly_type: str) -> List[str]:
        """특정 이상 유형에 대한 구체적 권장사항"""
        recommendations_map = {
            'spending_spike': [
                "이번 주 예산을 재검토해보세요",
                "큰 구매 전에는 하루 정도 생각해보세요"
            ],
            'impulse_buying': [
                "구매 전 목록 작성 습관을 만들어보세요",
                "아이와 함께 구매 이유를 이야기해보세요"
            ],
            'emotional_shopping': [
                "아이의 감정 상태를 체크해보세요",
                "대화를 통해 스트레스 원인을 찾아보세요"
            ],
            'category_shift': [
                "새로운 관심사에 대해 대화해보세요",
                "다양한 카테고리의 균형을 맞춰보세요"
            ]
        }
        
        return recommendations_map.get(anomaly_type, [
            "패턴 변화의 원인을 파악해보세요",
            "아이와 함께 소비 습관을 점검해보세요"
        ])
    
    def _save_anomaly_models(self):
        """이상 탐지 모델 저장"""
        joblib.dump(self.isolation_forest, self.model_path / "isolation_forest.pkl")
        joblib.dump(self.scaler, self.model_path / "anomaly_scaler.pkl")
        try:
            joblib.dump(self.elliptic_envelope, self.model_path / "elliptic_envelope.pkl")
        except:
            pass
    
    def _load_anomaly_models(self):
        """저장된 이상 탐지 모델 로드"""
        self.isolation_forest = joblib.load(self.model_path / "isolation_forest.pkl")
        self.scaler = joblib.load(self.model_path / "anomaly_scaler.pkl")
        try:
            self.elliptic_envelope = joblib.load(self.model_path / "elliptic_envelope.pkl")
        except:
            pass
