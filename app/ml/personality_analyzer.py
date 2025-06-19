"""
아이 성향 예측 모델
구매 패턴을 분석하여 아이의 성향을 분류하고 특성을 파악합니다.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import joblib
import json
from pathlib import Path

class PersonalityAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=4, random_state=42)
        self.pca = PCA(n_components=3)
        self.model_path = Path("app/ml/models")
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # 성향 타입 정의
        self.personality_types = {
            0: {
                "name": "학습지향형",
                "description": "교육적 가치를 중시하며 체계적인 소비 패턴을 보입니다",
                "characteristics": ["교육 비중 높음", "규칙적 패턴", "신중한 선택"],
                "color": "#4F46E5"
            },
            1: {
                "name": "활동적 탐험형", 
                "description": "다양한 활동을 즐기며 활발한 소비 패턴을 보입니다",
                "characteristics": ["다양한 카테고리", "활발한 구매", "새로운 것 선호"],
                "color": "#059669"
            },
            2: {
                "name": "창의적 표현형",
                "description": "창작과 표현 활동을 좋아하며 개성 있는 선택을 합니다",
                "characteristics": ["창의적 아이템", "개성 추구", "감성적 선택"],
                "color": "#DC2626"
            },
            3: {
                "name": "안정추구형",
                "description": "안정적이고 절제된 소비 패턴을 보입니다",
                "characteristics": ["절제된 소비", "안정성 추구", "실용적 선택"],
                "color": "#7C3AED"
            }
        }
    
    def extract_features(self, df: pd.DataFrame) -> Dict[str, float]:
        """구매 데이터에서 성향 분석을 위한 특성 추출"""
        if df.empty:
            return self._get_default_features()
        
        # 기본 통계
        total_amount = (df['price'] * df['cnt']).sum()
        total_purchases = len(df)
        avg_amount = total_amount / total_purchases if total_purchases > 0 else 0
        
        # 카테고리별 분석
        category_stats = df.groupby('type').agg({
            'price': ['count', 'sum'],
            'cnt': 'sum'
        }).fillna(0)
        
        category_ratios = {}
        for category in ['간식', '오락', '장난감', '교육', '기타']:
            if category in category_stats.index:
                category_ratios[f'{category}_ratio'] = (
                    category_stats.loc[category, ('price', 'sum')] / total_amount * 100
                    if total_amount > 0 else 0
                )
                category_ratios[f'{category}_frequency'] = (
                    category_stats.loc[category, ('price', 'count')] / total_purchases * 100
                    if total_purchases > 0 else 0
                )
            else:
                category_ratios[f'{category}_ratio'] = 0
                category_ratios[f'{category}_frequency'] = 0
        
        # 시간 패턴 분석
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        morning_purchases = len(df[df['hour'].between(6, 11)])
        afternoon_purchases = len(df[df['hour'].between(12, 17)])
        evening_purchases = len(df[df['hour'].between(18, 23)])
        
        # 구매 패턴 다양성
        unique_items = df['name'].nunique()
        diversity_score = unique_items / total_purchases if total_purchases > 0 else 0
        
        # 가격 분산 (선택의 일관성 측정)
        price_variance = df['price'].var() if len(df) > 1 else 0
        
        # 주기적 패턴 (요일별 구매 패턴)
        df['weekday'] = pd.to_datetime(df['timestamp']).dt.weekday
        weekday_variance = df.groupby('weekday').size().var() if len(df) > 6 else 0
        
        features = {
            'avg_purchase_amount': avg_amount,
            'total_purchases': total_purchases,
            'diversity_score': diversity_score,
            'price_variance': price_variance,
            'weekday_variance': weekday_variance,
            'morning_ratio': morning_purchases / total_purchases * 100 if total_purchases > 0 else 0,
            'afternoon_ratio': afternoon_purchases / total_purchases * 100 if total_purchases > 0 else 0,
            'evening_ratio': evening_purchases / total_purchases * 100 if total_purchases > 0 else 0,
            **category_ratios
        }
        
        return features
    
    def _get_default_features(self) -> Dict[str, float]:
        """기본 특성값 반환"""
        features = {
            'avg_purchase_amount': 0,
            'total_purchases': 0,
            'diversity_score': 0,
            'price_variance': 0,
            'weekday_variance': 0,
            'morning_ratio': 0,
            'afternoon_ratio': 0,
            'evening_ratio': 0
        }
        
        for category in ['간식', '오락', '장난감', '교육', '기타']:
            features[f'{category}_ratio'] = 0
            features[f'{category}_frequency'] = 0
        
        return features
    
    def train_model(self, purchase_data: List[pd.DataFrame]) -> None:
        """여러 아이들의 데이터로 모델 훈련"""
        if not purchase_data:
            return
        
        # 모든 아이들의 특성 추출
        all_features = []
        for child_data in purchase_data:
            features = self.extract_features(child_data)
            all_features.append(list(features.values()))
        
        if not all_features:
            return
        
        # 데이터 정규화
        X = np.array(all_features)
        X_scaled = self.scaler.fit_transform(X)
        
        # 차원 축소
        X_pca = self.pca.fit_transform(X_scaled)
        
        # 클러스터링
        self.kmeans.fit(X_pca)
        
        # 모델 저장
        self._save_models()
    
    def predict_personality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """개별 아이의 성향 예측"""
        try:
            self._load_models()
        except:
            # 모델이 없으면 기본 분석만 수행
            return self._basic_analysis(df)
        
        features = self.extract_features(df)
        feature_vector = np.array([list(features.values())]).reshape(1, -1)
        
        # 정규화 및 차원축소
        feature_scaled = self.scaler.transform(feature_vector)
        feature_pca = self.pca.transform(feature_scaled)
        
        # 예측
        cluster = self.kmeans.predict(feature_pca)[0]
        
        # 클러스터 중심과의 거리로 확신도 계산
        distances = self.kmeans.transform(feature_pca)[0]
        confidence = 1 - (distances[cluster] / distances.sum())
        
        personality_type = self.personality_types[cluster]
        
        result = {
            'personality_type': personality_type['name'],
            'description': personality_type['description'],
            'characteristics': personality_type['characteristics'],
            'confidence': float(confidence),
            'color': personality_type['color'],
            'detailed_analysis': self._get_detailed_analysis(features),
            'recommendations': self._get_recommendations(cluster, features)
        }
        
        return result
    
    def _basic_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """모델이 없을 때 기본 분석"""
        if df.empty:
            return {
                'personality_type': '데이터 부족',
                'description': '충분한 데이터가 수집되면 성향 분석을 제공합니다.',
                'characteristics': [],
                'confidence': 0.0,
                'color': '#6B7280',
                'detailed_analysis': {},
                'recommendations': ['더 많은 구매 데이터가 필요합니다.']
            }
        
        features = self.extract_features(df)
        
        # 간단한 규칙 기반 분류
        education_ratio = features.get('교육_ratio', 0)
        snack_ratio = features.get('간식_ratio', 0)
        toy_ratio = features.get('장난감_ratio', 0)
        entertainment_ratio = features.get('오락_ratio', 0)
        total_purchases = features.get('total_purchases', 0)
        
        # 성향 결정 로직 개선
        if education_ratio > 40:
            personality = {
                'name': '학습지향형',
                'description': '교육적 가치를 중시하며 체계적인 소비 패턴을 보입니다',
                'characteristics': ['교육 비중 높음', '학습에 관심이 많음', '신중한 선택'],
                'color': '#4F46E5'
            }
            confidence = min(0.9, education_ratio / 50)
        elif snack_ratio > 50:
            personality = {
                'name': '즐거움추구형',
                'description': '즐거운 경험을 중시하며 감정적 만족을 추구합니다',
                'characteristics': ['즐거움 추구', '감정적 선택', '즉흥적 구매'],
                'color': '#F59E0B'
            }
            confidence = min(0.8, snack_ratio / 60)
        elif toy_ratio > 30 or entertainment_ratio > 25:
            personality = {
                'name': '창의적 탐험형',
                'description': '새로운 것을 탐험하고 창의적 활동을 좋아합니다',
                'characteristics': ['창의성 중시', '호기심 많음', '다양한 경험'],
                'color': '#10B981'
            }
            confidence = min(0.8, max(toy_ratio, entertainment_ratio) / 40)
        elif total_purchases < 5:
            personality = {
                'name': '신중한 선택형',
                'description': '신중하고 계획적인 소비 패턴을 보입니다',
                'characteristics': ['신중한 결정', '계획적 소비', '절제된 구매'],
                'color': '#8B5CF6'
            }
            confidence = 0.7
        else:
            personality = {
                'name': '균형잡힌 성향',
                'description': '다양한 영역에 균형잡힌 관심을 보입니다',
                'characteristics': ['균형잡힌 소비', '다양한 관심사', '적응력 높음'],
                'color': '#06B6D4'
            }
            confidence = 0.75
        
        recommendations = self._get_basic_recommendations(features, personality['name'])
        
        return {
            'personality_type': personality['name'],
            'description': personality['description'], 
            'characteristics': personality['characteristics'],
            'confidence': float(confidence),
            'color': personality['color'],
            'detailed_analysis': {
                'education_focus': education_ratio,
                'enjoyment_seeking': snack_ratio,
                'creativity_score': toy_ratio,
                'entertainment_score': entertainment_ratio,
                'purchase_frequency': total_purchases,
                'spending_pattern': self._analyze_spending_pattern(df),
                'time_pattern': self._analyze_time_pattern(df),
                'category_diversity': len(df['type'].unique()) if not df.empty else 0,
                'age_appropriateness': self._calculate_age_appropriateness(df),
                'growth_trend': self._calculate_growth_trend(df)
            },
            'recommendations': recommendations,
            'features': features,
            'personality_score': {
                'learning_oriented': education_ratio,
                'fun_seeking': snack_ratio, 
                'creative': toy_ratio,
                'balanced': 100 - max(education_ratio, snack_ratio, toy_ratio)
            }
        }
    
    def _get_detailed_analysis(self, features: Dict[str, float]) -> Dict[str, Any]:
        """상세 분석 결과"""
        analysis = {
            'spending_pattern': {
                'average_amount': round(features.get('avg_purchase_amount', 0)),
                'total_purchases': int(features.get('total_purchases', 0)),
                'diversity_score': round(features.get('diversity_score', 0), 2)
            },
            'category_preferences': {},
            'time_patterns': {
                'morning': round(features.get('morning_ratio', 0), 1),
                'afternoon': round(features.get('afternoon_ratio', 0), 1),
                'evening': round(features.get('evening_ratio', 0), 1)
            }
        }
        
        # 카테고리별 선호도
        for category in ['간식', '오락', '장난감', '교육', '기타']:
            ratio = features.get(f'{category}_ratio', 0)
            analysis['category_preferences'][category] = round(ratio, 1)
        
        return analysis
    
    def _get_recommendations(self, cluster: int, features: Dict[str, float]) -> List[str]:
        """성향별 맞춤 추천"""
        recommendations = []
        
        if cluster == 0:  # 학습지향형
            recommendations = [
                "교육용 보드게임이나 퍼즐을 추천합니다",
                "독서 관련 아이템을 늘려보세요",
                "과학 실험 키트를 시도해보세요",
                "체계적인 학습 스케줄을 유지하세요"
            ]
        elif cluster == 1:  # 활동적 탐험형
            recommendations = [
                "야외 활동 장비를 추가해보세요",
                "새로운 스포츠 용품을 시도해보세요",
                "다양한 체험 활동을 계획하세요",
                "에너지 소모가 큰 활동을 늘려보세요"
            ]
        elif cluster == 2:  # 창의적 표현형
            recommendations = [
                "미술용품이나 만들기 키트를 추천합니다",
                "음악 관련 아이템을 고려해보세요",
                "창작 활동을 격려해주세요",
                "상상력을 키우는 놀이를 늘려보세요"
            ]
        else:  # 안정추구형
            recommendations = [
                "일정한 루틴을 유지하도록 도와주세요",
                "품질 좋은 기본 아이템에 투자하세요",
                "안정감을 주는 환경을 조성하세요",
                "점진적인 변화를 시도해보세요"
            ]
        
        return recommendations
    
    def _get_basic_recommendations(self, features: Dict[str, Any], personality_type: str) -> List[str]:
        """성향별 기본 추천사항"""
        recommendations = []
        
        if personality_type == '학습지향형':
            recommendations.extend([
                "현재 교육적 소비 패턴이 우수합니다. 심화 학습 도구를 고려해보세요.",
                "다양한 학습 영역으로 관심사를 확장해보는 것을 추천합니다.",
                "창의적 활동도 균형있게 포함시켜보세요."
            ])
        elif personality_type == '즐거움추구형':
            recommendations.extend([
                "즐거움을 추구하는 성향이 좋습니다. 교육적 요소가 있는 재미있는 아이템을 고려해보세요.",
                "간식 비중을 조금 줄이고 다른 카테고리도 탐험해보세요.",
                "장기적 만족을 줄 수 있는 아이템도 고려해보세요."
            ])
        elif personality_type == '창의적 탐험형':
            recommendations.extend([
                "창의적 성향이 뛰어납니다. 예술, 만들기 관련 도구를 더 제공해보세요.",
                "다양한 경험을 위해 새로운 카테고리도 시도해보세요.",
                "창작 결과물을 공유할 수 있는 환경을 만들어주세요."
            ])
        elif personality_type == '신중한 선택형':
            recommendations.extend([
                "신중한 소비 습관이 좋습니다. 점진적으로 구매 빈도를 늘려보세요.",
                "관심 있는 영역을 찾아 집중 투자를 고려해보세요.",
                "가격 대비 만족도가 높은 아이템을 선택해보세요."
            ])
        else:  # 균형잡힌 성향
            recommendations.extend([
                "균형잡힌 소비 패턴을 보이고 있습니다.",
                "각 카테고리별로 조금씩 업그레이드를 고려해보세요.",
                "새로운 관심사를 개발할 기회를 만들어보세요."
            ])
        
        # 공통 추천사항
        total_purchases = features.get('total_purchases', 0)
        if total_purchases < 10:
            recommendations.append("구매 경험을 늘려가며 취향을 발견해보세요.")
        
        return recommendations[:3]  # 최대 3개까지만 반환
    
    def _save_models(self):
        """모델 저장"""
        joblib.dump(self.scaler, self.model_path / "scaler.pkl")
        joblib.dump(self.kmeans, self.model_path / "kmeans.pkl") 
        joblib.dump(self.pca, self.model_path / "pca.pkl")
    
    def _load_models(self):
        """저장된 모델 로드"""
        self.scaler = joblib.load(self.model_path / "scaler.pkl")
        self.kmeans = joblib.load(self.model_path / "kmeans.pkl")
        self.pca = joblib.load(self.model_path / "pca.pkl")
    
    def get_personality_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """종합적인 성향 분석 결과"""
        personality_result = self.predict_personality(df)
        
        # 추가 인사이트
        features = self.extract_features(df)
        
        insights = {
            'personality': personality_result,
            'behavioral_patterns': {
                'consistency_score': self._calculate_consistency(df),
                'growth_indicators': self._identify_growth_patterns(df),
                'risk_factors': self._identify_risk_factors(features)
            },
            'development_suggestions': self._get_development_suggestions(personality_result, features)
        }
        
        return insights
    
    def _calculate_consistency(self, df: pd.DataFrame) -> float:
        """구매 패턴의 일관성 점수"""
        if df.empty or len(df) < 5:
            return 0.0
        
        # 주간별 구매 패턴 일관성
        df['week'] = pd.to_datetime(df['timestamp']).dt.isocalendar().week
        weekly_amounts = df.groupby('week')['price'].sum()
        
        if len(weekly_amounts) < 2:
            return 0.5
        
        # 변동계수의 역수로 일관성 측정
        cv = weekly_amounts.std() / weekly_amounts.mean() if weekly_amounts.mean() > 0 else 1
        consistency = 1 / (1 + cv)
        
        return round(consistency, 2)
    
    def _identify_growth_patterns(self, df: pd.DataFrame) -> List[str]:
        """성장 지표 패턴 식별"""
        patterns = []
        
        if df.empty:
            return patterns
        
        # 교육 아이템 증가 추세
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        recent_data = df[df['date'] >= (datetime.now().date() - timedelta(days=14))]
        education_recent = len(recent_data[recent_data['type'] == '교육'])
        
        if education_recent > 0:
            patterns.append("교육적 관심이 증가하고 있습니다")
        
        # 다양성 증가
        recent_categories = recent_data['type'].nunique()
        if recent_categories >= 3:
            patterns.append("다양한 영역에 관심을 보이고 있습니다")
        
        # 자립적 선택 (단가가 적절한 범위)
        avg_price = recent_data['price'].mean() if not recent_data.empty else 0
        if 1000 <= avg_price <= 5000:
            patterns.append("적절한 가격대의 선택을 하고 있습니다")
        
        return patterns
    
    def _identify_risk_factors(self, features: Dict[str, float]) -> List[str]:
        """주의가 필요한 패턴 식별"""
        risks = []
        
        # 과도한 간식 구매
        if features.get('간식_ratio', 0) > 60:
            risks.append("간식 비중이 높습니다. 균형잡힌 소비를 고려해보세요")
        
        # 너무 적은 교육 투자
        if features.get('교육_ratio', 0) < 10 and features.get('total_purchases', 0) > 5:
            risks.append("교육적 아이템 비중을 늘려보세요")
        
        # 불규칙한 패턴
        if features.get('weekday_variance', 0) > 5:
            risks.append("구매 패턴이 불규칙합니다. 루틴을 만들어보세요")
        
        return risks
    
    def _get_development_suggestions(self, personality: Dict, features: Dict) -> List[str]:
        """발달 단계별 제안사항"""
        suggestions = []
        
        personality_type = personality.get('personality_type', '')
        
        if '학습지향형' in personality_type:
            suggestions.extend([
                "심화 학습 도구를 단계적으로 도입해보세요",
                "자기주도 학습 습관을 기를 수 있는 환경을 조성하세요"
            ])
        elif '활동적' in personality_type:
            suggestions.extend([
                "체력을 기를 수 있는 활동을 늘려보세요",
                "팀워크를 기를 수 있는 그룹 활동을 고려하세요"
            ])
        elif '창의적' in personality_type:
            suggestions.extend([
                "표현력을 기를 수 있는 도구를 제공하세요",
                "상상력을 자극하는 다양한 경험을 제공하세요"
            ])
        
        return suggestions
