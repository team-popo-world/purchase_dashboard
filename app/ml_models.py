import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class ChildPersonalityAnalyzer:
    """아이의 구매 패턴을 분석하여 성향을 예측하는 모델"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.kmeans = None
        self.personality_types = {
            0: "창의적 탐험가",
            1: "학습 중심형",
            2: "활동적 에너지",
            3: "사교적 놀이형",
            4: "신중한 계획형"
        }
        self.personality_descriptions = {
            "창의적 탐험가": {
                "description": "새로운 것에 호기심이 많고 창의적인 활동을 좋아합니다",
                "characteristics": ["높은 장난감 구매율", "다양한 카테고리 관심", "실험적 구매 패턴"],
                "recommendations": ["미술용품", "블록류", "과학실험키트", "창작도구"]
            },
            "학습 중심형": {
                "description": "교육과 학습에 관심이 높고 체계적인 성향을 보입니다",
                "characteristics": ["높은 교육 아이템 비율", "규칙적인 구매 패턴", "평균 이상 구매 단가"],
                "recommendations": ["교육서적", "학습교구", "온라인 강의", "지식 게임"]
            },
            "활동적 에너지": {
                "description": "활동적이고 에너지가 넘치며 움직이는 것을 좋아합니다",
                "characteristics": ["오락/스포츠 높은 비율", "빈번한 구매", "다양한 시간대 활동"],
                "recommendations": ["스포츠용품", "액티브 게임", "야외활동 용품", "운동기구"]
            },
            "사교적 놀이형": {
                "description": "친구들과 함께하는 활동을 좋아하고 사교적입니다",
                "characteristics": ["간식 높은 비율", "그룹 활동 선호", "주말 구매 집중"],
                "recommendations": ["보드게임", "파티용품", "간식세트", "공유 장난감"]
            },
            "신중한 계획형": {
                "description": "신중하게 생각하고 계획적으로 행동하는 성향입니다",
                "characteristics": ["낮은 구매 빈도", "높은 단가 선호", "규칙적인 패턴"],
                "recommendations": ["고품질 교구", "장기 프로젝트", "수집품", "정밀 작업 도구"]
            }
        }
    
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """구매 데이터에서 성향 분석을 위한 특성 추출"""
        if df.empty:
            return pd.DataFrame()
        
        # 총액 계산
        df['total_amount'] = df['price'] * df['cnt']
        
        # 시간 특성 추출
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6])
        
        # 사용자별 특성 계산
        user_features = []
        for user_id in df['kid_id'].unique():
            user_data = df[df['kid_id'] == user_id]
            
            # 기본 통계
            total_purchases = len(user_data)
            total_amount = user_data['total_amount'].sum()
            avg_amount = user_data['total_amount'].mean()
            
            # 카테고리별 비율
            category_counts = user_data['type'].value_counts(normalize=True)
            snack_ratio = category_counts.get('간식', 0)
            entertainment_ratio = category_counts.get('오락', 0)
            toy_ratio = category_counts.get('장난감', 0)
            education_ratio = category_counts.get('교육', 0)
            etc_ratio = category_counts.get('기타', 0)
            
            # 시간 패턴
            weekend_ratio = user_data['is_weekend'].mean()
            avg_hour = user_data['hour'].mean()
            hour_variance = user_data['hour'].var()
            
            # 구매 패턴
            days_active = user_data['timestamp'].dt.date.nunique()
            purchase_frequency = total_purchases / max(days_active, 1)
            
            # 다양성 지수 (엔트로피)
            category_entropy = -sum([p * np.log2(p) for p in category_counts.values() if p > 0])
            
            # 가격 패턴
            price_variance = user_data['price'].var()
            high_price_ratio = (user_data['price'] > user_data['price'].quantile(0.7)).mean()
            
            features = {
                'user_id': user_id,
                'total_purchases': total_purchases,
                'total_amount': total_amount,
                'avg_amount': avg_amount,
                'snack_ratio': snack_ratio,
                'entertainment_ratio': entertainment_ratio,
                'toy_ratio': toy_ratio,
                'education_ratio': education_ratio,
                'etc_ratio': etc_ratio,
                'weekend_ratio': weekend_ratio,
                'avg_hour': avg_hour,
                'hour_variance': hour_variance,
                'purchase_frequency': purchase_frequency,
                'category_entropy': category_entropy,
                'price_variance': price_variance,
                'high_price_ratio': high_price_ratio
            }
            
            user_features.append(features)
        
        return pd.DataFrame(user_features)
    
    def train_model(self, df: pd.DataFrame) -> Dict[str, Any]:
        """성향 분석 모델 훈련"""
        feature_df = self.extract_features(df)
        
        if len(feature_df) < 5:  # 최소 데이터 요구사항
            return {"error": "분석을 위한 데이터가 부족합니다"}
        
        # 특성 선택 (user_id 제외)
        feature_columns = [col for col in feature_df.columns if col != 'user_id']
        X = feature_df[feature_columns].fillna(0)
        
        # 정규화
        X_scaled = self.scaler.fit_transform(X)
        
        # 최적 클러스터 수 찾기
        best_k = 3
        best_score = -1
        
        for k in range(2, min(6, len(feature_df))):
            kmeans_temp = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans_temp.fit_predict(X_scaled)
            if len(set(labels)) > 1:  # 최소 2개 클러스터
                score = silhouette_score(X_scaled, labels)
                if score > best_score:
                    best_score = score
                    best_k = k
        
        # 최종 모델 훈련
        self.kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        labels = self.kmeans.fit_predict(X_scaled)
        
        # 클러스터별 특성 분석
        cluster_analysis = self._analyze_clusters(feature_df, labels, feature_columns)
        
        return {
            "model_trained": True,
            "n_clusters": best_k,
            "silhouette_score": best_score,
            "cluster_analysis": cluster_analysis,
            "feature_importance": self._get_feature_importance(X_scaled, labels)
        }
    
    def predict_personality(self, user_data: pd.DataFrame) -> Dict[str, Any]:
        """개별 사용자의 성향 예측"""
        if self.kmeans is None:
            return {"error": "모델이 훈련되지 않았습니다"}
        
        feature_df = self.extract_features(user_data)
        if feature_df.empty:
            return {"error": "분석할 데이터가 없습니다"}
        
        feature_columns = [col for col in feature_df.columns if col != 'user_id']
        X = feature_df[feature_columns].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        cluster = self.kmeans.predict(X_scaled)[0]
        personality_type = self._map_cluster_to_personality(cluster, feature_df.iloc[0])
        
        return {
            "personality_type": personality_type,
            "confidence": self._calculate_confidence(X_scaled[0], cluster),
            "description": self.personality_descriptions[personality_type]["description"],
            "characteristics": self.personality_descriptions[personality_type]["characteristics"],
            "recommendations": self.personality_descriptions[personality_type]["recommendations"],
            "detailed_analysis": self._get_detailed_analysis(feature_df.iloc[0])
        }
    
    def _analyze_clusters(self, feature_df: pd.DataFrame, labels: np.ndarray, feature_columns: List[str]) -> Dict:
        """클러스터별 특성 분석"""
        cluster_analysis = {}
        
        for cluster_id in range(len(set(labels))):
            cluster_mask = labels == cluster_id
            cluster_data = feature_df[cluster_mask]
            
            cluster_analysis[cluster_id] = {
                "size": int(cluster_mask.sum()),
                "avg_features": cluster_data[feature_columns].mean().to_dict()
            }
        
        return cluster_analysis
    
    def _map_cluster_to_personality(self, cluster: int, features: pd.Series) -> str:
        """클러스터를 성향 타입으로 매핑"""
        # 특성 기반 매핑 로직
        if features['education_ratio'] > 0.3:
            return "학습 중심형"
        elif features['toy_ratio'] > 0.4:
            return "창의적 탐험가"
        elif features['entertainment_ratio'] > 0.3 or features['purchase_frequency'] > 2:
            return "활동적 에너지"
        elif features['snack_ratio'] > 0.3 and features['weekend_ratio'] > 0.5:
            return "사교적 놀이형"
        else:
            return "신중한 계획형"
    
    def _calculate_confidence(self, features: np.ndarray, cluster: int) -> float:
        """예측 신뢰도 계산"""
        if self.kmeans is None:
            return 0.0
        
        distances = []
        for center in self.kmeans.cluster_centers_:
            distance = np.linalg.norm(features - center)
            distances.append(distance)
        
        min_distance = min(distances)
        max_distance = max(distances)
        
        if max_distance == min_distance:
            return 1.0
        
        confidence = 1 - (min_distance / max_distance)
        return round(confidence, 2)
    
    def _get_feature_importance(self, X: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
        """특성 중요도 계산"""
        from sklearn.metrics import adjusted_rand_score
        
        feature_names = ['total_purchases', 'avg_amount', 'snack_ratio', 'entertainment_ratio',
                        'toy_ratio', 'education_ratio', 'weekend_ratio', 'purchase_frequency',
                        'category_entropy', 'high_price_ratio']
        
        importance = {}
        baseline_score = adjusted_rand_score(labels, labels)  # Perfect score
        
        for i, feature_name in enumerate(feature_names[:X.shape[1]]):
            # 특성을 제거하고 클러스터링 재실행
            X_reduced = np.delete(X, i, axis=1)
            kmeans_temp = KMeans(n_clusters=len(set(labels)), random_state=42, n_init=10)
            labels_reduced = kmeans_temp.fit_predict(X_reduced)
            
            # 성능 변화 측정
            score_reduced = adjusted_rand_score(labels, labels_reduced)
            importance[feature_name] = max(0, baseline_score - score_reduced)
        
        # 정규화
        total_importance = sum(importance.values())
        if total_importance > 0:
            importance = {k: v/total_importance for k, v in importance.items()}
        
        return importance
    
    def _get_detailed_analysis(self, features: pd.Series) -> Dict[str, Any]:
        """상세 분석 결과"""
        return {
            "구매_패턴": {
                "총_구매횟수": int(features['total_purchases']),
                "평균_구매금액": int(features['avg_amount']),
                "구매_빈도": round(features['purchase_frequency'], 2)
            },
            "카테고리_선호도": {
                "간식": f"{features['snack_ratio']*100:.1f}%",
                "오락": f"{features['entertainment_ratio']*100:.1f}%",
                "장난감": f"{features['toy_ratio']*100:.1f}%",
                "교육": f"{features['education_ratio']*100:.1f}%"
            },
            "시간_패턴": {
                "주말_구매율": f"{features['weekend_ratio']*100:.1f}%",
                "평균_구매시간": f"{features['avg_hour']:.1f}시",
                "패턴_다양성": round(features['category_entropy'], 2)
            }
        }


class AnomalyDetector:
    """이상 행동 탐지 시스템"""
    
    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.baseline_patterns = {}
        
    def train_baseline(self, df: pd.DataFrame) -> Dict[str, Any]:
        """정상 패턴 학습"""
        if df.empty:
            return {"error": "학습할 데이터가 없습니다"}
        
        # 특성 추출
        features_df = self._extract_anomaly_features(df)
        
        if len(features_df) < 10:  # 최소 데이터 요구사항
            return {"error": "이상 탐지를 위한 충분한 데이터가 없습니다"}
        
        # 정규화
        feature_columns = [col for col in features_df.columns if col != 'kid_id']
        X = features_df[feature_columns].fillna(0)
        X_scaled = self.scaler.fit_transform(X)
        
        # Isolation Forest 훈련
        self.isolation_forest.fit(X_scaled)
        
        # 사용자별 기준 패턴 저장
        for kid_id in df['kid_id'].unique():
            user_data = df[df['kid_id'] == kid_id]
            self.baseline_patterns[kid_id] = self._calculate_baseline_stats(user_data)
        
        return {
            "model_trained": True,
            "users_analyzed": len(self.baseline_patterns),
            "features_count": len(feature_columns)
        }
    
    def detect_anomalies(self, recent_data: pd.DataFrame, kid_id: str = None) -> Dict[str, Any]:
        """이상 행동 탐지"""
        if not hasattr(self.isolation_forest, 'decision_function'):
            return {"error": "모델이 훈련되지 않았습니다"}
        
        anomalies = []
        
        if kid_id:
            # 특정 사용자 분석
            user_data = recent_data[recent_data['kid_id'] == kid_id] if 'kid_id' in recent_data.columns else recent_data
            anomaly_result = self._analyze_user_anomalies(user_data, kid_id)
            if anomaly_result:
                anomalies.append(anomaly_result)
        else:
            # 모든 사용자 분석
            for user_id in recent_data['kid_id'].unique():
                user_data = recent_data[recent_data['kid_id'] == user_id]
                anomaly_result = self._analyze_user_anomalies(user_data, user_id)
                if anomaly_result:
                    anomalies.append(anomaly_result)
        
        return {
            "anomalies_detected": len(anomalies),
            "anomalies": anomalies,
            "alerts": self._generate_alerts(anomalies)
        }
    
    def _extract_anomaly_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """이상 탐지를 위한 특성 추출"""
        df['total_amount'] = df['price'] * df['cnt']
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        # 일별 집계 특성
        daily_features = []
        
        for kid_id in df['kid_id'].unique():
            user_data = df[df['kid_id'] == kid_id]
            
            for date in user_data['timestamp'].dt.date.unique():
                day_data = user_data[user_data['timestamp'].dt.date == date]
                
                features = {
                    'kid_id': kid_id,
                    'date': date,
                    'daily_amount': day_data['total_amount'].sum(),
                    'daily_count': len(day_data),
                    'unique_categories': day_data['type'].nunique(),
                    'avg_price': day_data['price'].mean(),
                    'max_price': day_data['price'].max(),
                    'hour_range': day_data['hour'].max() - day_data['hour'].min(),
                    'late_night_purchases': (day_data['hour'] >= 22).sum(),
                    'early_morning_purchases': (day_data['hour'] <= 6).sum(),
                    'weekend_day': int(date.weekday() >= 5)
                }
                
                daily_features.append(features)
        
        return pd.DataFrame(daily_features)
    
    def _calculate_baseline_stats(self, user_data: pd.DataFrame) -> Dict[str, float]:
        """사용자별 기준 통계 계산"""
        user_data['total_amount'] = user_data['price'] * user_data['cnt']
        user_data['hour'] = user_data['timestamp'].dt.hour
        
        return {
            'avg_daily_amount': user_data.groupby(user_data['timestamp'].dt.date)['total_amount'].sum().mean(),
            'std_daily_amount': user_data.groupby(user_data['timestamp'].dt.date)['total_amount'].sum().std(),
            'avg_daily_count': user_data.groupby(user_data['timestamp'].dt.date).size().mean(),
            'std_daily_count': user_data.groupby(user_data['timestamp'].dt.date).size().std(),
            'common_hours': user_data['hour'].mode().tolist(),
            'avg_price': user_data['price'].mean(),
            'std_price': user_data['price'].std(),
            'common_categories': user_data['type'].value_counts().head(3).index.tolist()
        }
    
    def _analyze_user_anomalies(self, user_data: pd.DataFrame, kid_id: str) -> Dict[str, Any]:
        """개별 사용자 이상 행동 분석"""
        if kid_id not in self.baseline_patterns or user_data.empty:
            return None
        
        baseline = self.baseline_patterns[kid_id]
        user_data['total_amount'] = user_data['price'] * user_data['cnt']
        user_data['hour'] = user_data['timestamp'].dt.hour
        
        anomalies = []
        severity_score = 0
        
        # 일일 지출 이상
        daily_amounts = user_data.groupby(user_data['timestamp'].dt.date)['total_amount'].sum()
        for date, amount in daily_amounts.items():
            z_score = abs((amount - baseline['avg_daily_amount']) / max(baseline['std_daily_amount'], 1))
            if z_score > 2:  # 2 표준편차 초과
                anomalies.append({
                    "type": "spending_spike",
                    "date": str(date),
                    "amount": int(amount),
                    "expected": int(baseline['avg_daily_amount']),
                    "severity": min(z_score / 2, 3)
                })
                severity_score += z_score
        
        # 구매 빈도 이상
        daily_counts = user_data.groupby(user_data['timestamp'].dt.date).size()
        for date, count in daily_counts.items():
            z_score = abs((count - baseline['avg_daily_count']) / max(baseline['std_daily_count'], 1))
            if z_score > 2:
                anomalies.append({
                    "type": "frequency_anomaly",
                    "date": str(date),
                    "count": int(count),
                    "expected": int(baseline['avg_daily_count']),
                    "severity": min(z_score / 2, 3)
                })
                severity_score += z_score
        
        # 시간대 이상
        unusual_hours = user_data[~user_data['hour'].isin(baseline['common_hours'])]
        if len(unusual_hours) > 0:
            late_night = unusual_hours[unusual_hours['hour'] >= 22]
            early_morning = unusual_hours[unusual_hours['hour'] <= 6]
            
            if len(late_night) > 0:
                anomalies.append({
                    "type": "unusual_timing",
                    "subtype": "late_night",
                    "count": len(late_night),
                    "hours": late_night['hour'].unique().tolist(),
                    "severity": min(len(late_night) / 3, 3)
                })
                severity_score += len(late_night) * 0.5
            
            if len(early_morning) > 0:
                anomalies.append({
                    "type": "unusual_timing",
                    "subtype": "early_morning",
                    "count": len(early_morning),
                    "hours": early_morning['hour'].unique().tolist(),
                    "severity": min(len(early_morning) / 3, 3)
                })
                severity_score += len(early_morning) * 0.5
        
        # 새로운 카테고리 탐지
        new_categories = set(user_data['type'].unique()) - set(baseline['common_categories'])
        if new_categories:
            anomalies.append({
                "type": "new_category",
                "categories": list(new_categories),
                "severity": min(len(new_categories), 2)
            })
            severity_score += len(new_categories) * 0.3
        
        if not anomalies:
            return None
        
        return {
            "kid_id": kid_id,
            "total_anomalies": len(anomalies),
            "severity_score": round(severity_score, 2),
            "risk_level": self._calculate_risk_level(severity_score),
            "anomalies": anomalies,
            "analysis_period": {
                "start": str(user_data['timestamp'].min().date()),
                "end": str(user_data['timestamp'].max().date())
            }
        }
    
    def _calculate_risk_level(self, severity_score: float) -> str:
        """위험도 계산"""
        if severity_score < 2:
            return "낮음"
        elif severity_score < 5:
            return "보통"
        elif severity_score < 10:
            return "높음"
        else:
            return "매우 높음"
    
    def _generate_alerts(self, anomalies: List[Dict]) -> List[Dict[str, Any]]:
        """알림 생성"""
        alerts = []
        
        for anomaly in anomalies:
            if anomaly['risk_level'] in ['높음', '매우 높음']:
                alert = {
                    "type": "warning" if anomaly['risk_level'] == '높음' else "critical",
                    "title": f"이상 행동 탐지: {anomaly['kid_id']}",
                    "message": self._generate_alert_message(anomaly),
                    "severity": anomaly['severity_score'],
                    "recommended_actions": self._get_recommended_actions(anomaly)
                }
                alerts.append(alert)
        
        return alerts
    
    def _generate_alert_message(self, anomaly: Dict) -> str:
        """알림 메시지 생성"""
        risk_level = anomaly['risk_level']
        anomaly_count = anomaly['total_anomalies']
        
        if risk_level == "매우 높음":
            return f"평소와 매우 다른 소비 패턴이 감지되었습니다. {anomaly_count}개의 이상 징후가 발견되었으니 즉시 확인이 필요합니다."
        elif risk_level == "높음":
            return f"평소와 다른 소비 행동이 관찰되고 있습니다. {anomaly_count}개의 변화가 감지되었으니 관심을 가져주세요."
        else:
            return f"소비 패턴에 약간의 변화가 있었습니다. {anomaly_count}개의 변화가 관찰되었습니다."
    
    def _get_recommended_actions(self, anomaly: Dict) -> List[str]:
        """권장 조치 사항"""
        actions = []
        
        for item in anomaly['anomalies']:
            if item['type'] == 'spending_spike':
                actions.append("지출 급증 원인 확인 및 대화")
            elif item['type'] == 'frequency_anomaly':
                actions.append("구매 빈도 변화 원인 파악")
            elif item['type'] == 'unusual_timing':
                if item['subtype'] == 'late_night':
                    actions.append("늦은 시간 구매 패턴 확인")
                else:
                    actions.append("이른 시간 구매 패턴 확인")
            elif item['type'] == 'new_category':
                actions.append("새로운 관심사에 대한 대화")
        
        # 중복 제거
        return list(set(actions))
