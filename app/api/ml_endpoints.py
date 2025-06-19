"""
머신러닝 관련 API 엔드포인트
아이 성향 예측과 이상 행동 탐지 API를 제공합니다.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

from ..database import get_purchase_data
from ..analytics import PurchaseAnalyzer
from ..ml.personality_analyzer import PersonalityAnalyzer
from ..ml.anomaly_detector import AnomalyDetector

router = APIRouter(prefix="/ml", tags=["machine-learning"])

@router.get("/personality-analysis")
async def get_personality_analysis() -> Dict[str, Any]:
    """
    아이의 성향 분석 결과를 반환합니다.
    
    Returns:
        Dict: 성향 분석 결과
            - personality_type: 성향 유형
            - description: 성향 설명
            - characteristics: 특성 목록
            - confidence: 신뢰도
            - detailed_analysis: 상세 분석
            - recommendations: 추천사항
    """
    try:
        # 구매 데이터 가져오기
        df = get_purchase_data()
        
        if df.empty:
            return {
                "status": "no_data",
                "message": "분석할 구매 데이터가 없습니다.",
                "personality": {
                    "personality_type": "데이터 부족",
                    "description": "충분한 데이터가 수집되면 성향 분석을 제공합니다.",
                    "characteristics": [],
                    "confidence": 0.0,
                    "color": "#6B7280"
                }
            }
        
        # PersonalityAnalyzer 사용으로 변경
        personality_analyzer = PersonalityAnalyzer()
        personality_insights = personality_analyzer.get_personality_insights(df)
        
        return {
            "status": "success",
            "message": "성향 분석이 완료되었습니다.",
            "data": personality_insights,
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"성향 분석 중 오류가 발생했습니다: {str(e)}"
        )
        
        return {
            "status": "success",
            "message": "성향 분석이 완료되었습니다.",
            "data": personality_insights,
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"성향 분석 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/anomaly-detection")
async def get_anomaly_detection() -> Dict[str, Any]:
    """
    이상 행동 탐지 결과를 반환합니다.
    
    Returns:
        Dict: 이상 탐지 결과
            - anomalies_detected: 이상 징후 감지 여부
            - anomaly_count: 감지된 이상 징후 수
            - risk_level: 위험 수준 (low/medium/high)
            - anomalies: 이상 징후 목록
            - recommendations: 권장사항
    """
    try:
        # 구매 데이터 가져오기
        df = get_purchase_data()
        
        if df.empty:
            return {
                "status": "no_data",
                "message": "분석할 구매 데이터가 없습니다.",
                "detection_result": {
                    "anomalies_detected": False,
                    "anomaly_count": 0,
                    "risk_level": "low",
                    "summary": "데이터가 충분하지 않습니다."
                }
            }
        
        # AnomalyDetector 사용으로 변경
        anomaly_detector = AnomalyDetector()
        anomaly_result = anomaly_detector.detect_anomalies(df)
        
        return {
            "status": "success",
            "message": "이상 행동 탐지가 완료되었습니다.",
            "data": anomaly_result,
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"이상 탐지 중 오류가 발생했습니다: {str(e)}"
        )
        
        return {
            "status": "success",
            "message": "이상 행동 탐지가 완료되었습니다.",
            "data": anomaly_result,
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"이상 탐지 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/smart-insights")
async def get_smart_insights() -> Dict[str, Any]:
    """
    AI 기반 종합 인사이트를 반환합니다.
    
    Returns:
        Dict: 종합 인사이트
            - personality_analysis: 성향 분석
            - anomaly_detection: 이상 탐지
            - behavioral_patterns: 행동 패턴
            - recommendations: 종합 추천사항
    """
    try:
        # 구매 데이터 가져오기
        df = get_purchase_data()
        
        if df.empty:
            return {
                "status": "no_data",
                "message": "분석할 구매 데이터가 없습니다.",
                "insights": {
                    "summary": "데이터가 충분하지 않습니다.",
                    "recommendations": [
                        "더 많은 구매 데이터가 수집되면 정확한 분석을 제공할 수 있습니다.",
                        "꾸준한 기록을 통해 아이의 성향을 파악해보세요."
                    ]
                }
            }
        
        # 종합 분석 실행
        analyzer = PurchaseAnalyzer(df)
        comprehensive_analysis = analyzer.get_comprehensive_analysis()
        
        # 핵심 인사이트 추출
        personality = comprehensive_analysis.get('personalityInsights', {}).get('personality', {})
        anomaly = comprehensive_analysis.get('anomalyDetection', {})
        
        # 종합 점수 계산
        data_quality_score = min(len(df) / 20, 1.0)  # 20개 이상이면 만점
        personality_confidence = personality.get('confidence', 0.0)
        risk_level = anomaly.get('risk_level', 'low')
        
        risk_scores = {'low': 0.9, 'medium': 0.6, 'high': 0.3}
        safety_score = risk_scores.get(risk_level, 0.9)
        
        insights = {
            "summary": _generate_insight_summary(personality, anomaly, len(df)),
            "scores": {
                "data_quality": round(data_quality_score * 100),
                "personality_confidence": round(personality_confidence * 100),
                "safety_score": round(safety_score * 100)
            },
            "key_findings": _extract_key_findings(comprehensive_analysis),
            "action_items": _generate_action_items(personality, anomaly),
            "trend_analysis": _analyze_trends(df)
        }
        
        return {
            "status": "success",
            "message": "AI 인사이트 분석이 완료되었습니다.",
            "data": {
                "personality_analysis": personality,
                "anomaly_detection": anomaly,
                "insights": insights
            },
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"인사이트 분석 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/recommendations")
async def get_ai_recommendations() -> Dict[str, Any]:
    """
    AI 기반 맞춤 추천을 반환합니다.
    
    Returns:
        Dict: 맞춤 추천사항
    """
    try:
        df = get_purchase_data()
        
        if df.empty:
            return {
                "status": "no_data",
                "recommendations": [
                    "구매 데이터를 수집하여 맞춤 추천을 받아보세요!",
                    "다양한 카테고리의 아이템을 균형있게 구매해보세요."
                ]
            }
        
        analyzer = PurchaseAnalyzer(df)
        
        # 성향 기반 추천
        personality_insights = analyzer.get_personality_insights()
        personality_recs = personality_insights.get('personality', {}).get('recommendations', [])
        
        # 이상 탐지 기반 추천
        anomaly_alerts = analyzer.get_ml_enhanced_alerts()
        safety_recs = []
        for alert in anomaly_alerts:
            if alert.get('type') in ['warning', 'alert']:
                safety_recs.extend(alert.get('recommendations', []))
        
        # 데이터 기반 추천
        data_recs = _generate_data_driven_recommendations(df)
        
        return {
            "status": "success",
            "recommendations": {
                "personality_based": personality_recs[:3],
                "safety_focused": list(set(safety_recs))[:3],
                "data_driven": data_recs[:3],
                "general": [
                    "정기적으로 구매 패턴을 리뷰해보세요",
                    "아이와 함께 구매 계획을 세워보세요",
                    "교육과 놀이의 균형을 맞춰보세요"
                ]
            },
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"추천 생성 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/behavior-patterns")
async def get_behavior_patterns() -> Dict[str, Any]:
    """
    행동 패턴 분석 결과를 반환합니다.
    
    Returns:
        Dict: 행동 패턴 분석 결과
    """
    try:
        df = get_purchase_data()
        
        if df.empty:
            return {
                "status": "no_data",
                "message": "분석할 구매 데이터가 없습니다."
            }
        
        # 행동 패턴 분석
        patterns = _analyze_behavioral_patterns(df)
        
        return {
            "status": "success",
            "data": patterns,
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"행동 패턴 분석 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/personality-trends")
async def get_personality_trends(days: Optional[int] = 30) -> Dict[str, Any]:
    """
    성향 변화 추이를 분석합니다.
    
    Args:
        days: 분석할 일수 (기본값: 30일)
    
    Returns:
        Dict: 성향 변화 추이
    """
    try:
        df = get_purchase_data()
        
        if df.empty:
            return {
                "status": "no_data",
                "message": "분석할 구매 데이터가 없습니다."
            }
        
        # 기간별 성향 분석
        trends = _analyze_personality_trends(df, days)
        
        return {
            "status": "success",
            "data": trends,
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"성향 추이 분석 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/risk-assessment")
async def get_risk_assessment() -> Dict[str, Any]:
    """
    종합적인 위험도 평가를 수행합니다.
    
    Returns:
        Dict: 위험도 평가 결과
    """
    try:
        df = get_purchase_data()
        
        if df.empty:
            return {
                "status": "no_data",
                "message": "분석할 구매 데이터가 없습니다."
            }
        
        # 위험도 평가
        risk_assessment = _comprehensive_risk_assessment(df)
        
        return {
            "status": "success",
            "data": risk_assessment,
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"위험도 평가 중 오류가 발생했습니다: {str(e)}"
        )

def _generate_insight_summary(personality: Dict, anomaly: Dict, data_count: int) -> str:
    """인사이트 요약 생성"""
    personality_type = personality.get('personality_type', '분석 중')
    risk_level = anomaly.get('risk_level', 'low')
    
    summary_parts = []
    
    # 성향 기반 요약
    if personality_type != '분석 중':
        summary_parts.append(f"아이는 '{personality_type}' 성향을 보이고 있습니다.")
    
    # 위험도 기반 요약
    if risk_level == 'high':
        summary_parts.append("주의가 필요한 구매 패턴이 감지되었습니다.")
    elif risk_level == 'medium':
        summary_parts.append("일부 변화된 패턴이 관찰되고 있습니다.")
    else:
        summary_parts.append("안정적인 구매 패턴을 보이고 있습니다.")
    
    # 데이터 품질 기반 요약
    if data_count < 10:
        summary_parts.append("더 정확한 분석을 위해 추가 데이터가 필요합니다.")
    
    return " ".join(summary_parts)

def _extract_key_findings(analysis: Dict) -> List[str]:
    """핵심 발견사항 추출"""
    findings = []
    
    # 성향 관련 발견사항
    personality = analysis.get('personalityInsights', {}).get('personality', {})
    if personality.get('confidence', 0) > 0.7:
        findings.append(f"높은 신뢰도로 '{personality.get('personality_type')}' 성향이 확인되었습니다")
    
    # 이상 탐지 관련 발견사항
    anomaly = analysis.get('anomalyDetection', {})
    if anomaly.get('anomalies_detected', False):
        findings.append(f"{anomaly.get('anomaly_count', 0)}개의 이상 패턴이 감지되었습니다")
    
    # 메트릭 관련 발견사항
    metrics = analysis.get('metrics', {})
    education_ratio = metrics.get('educationRatio', 0)
    if education_ratio > 25:
        findings.append("교육적 구매 비중이 매우 높습니다")
    elif education_ratio < 10:
        findings.append("교육적 구매 비중이 낮습니다")
    
    return findings[:5]  # 최대 5개

def _generate_action_items(personality: Dict, anomaly: Dict) -> List[str]:
    """실행 가능한 액션 아이템 생성"""
    actions = []
    
    # 성향 기반 액션
    personality_type = personality.get('personality_type', '')
    if '학습지향형' in personality_type:
        actions.append("체계적인 학습 계획을 수립해보세요")
    elif '활동적' in personality_type:
        actions.append("야외 활동 시간을 늘려보세요")
    elif '창의적' in personality_type:
        actions.append("창작 활동 도구를 추가해보세요")
    
    # 이상 탐지 기반 액션
    risk_level = anomaly.get('risk_level', 'low')
    if risk_level == 'high':
        actions.append("즉시 구매 패턴을 점검하고 조정하세요")
    elif risk_level == 'medium':
        actions.append("구매 패턴의 변화 원인을 파악해보세요")
    
    return actions

def _analyze_trends(df: pd.DataFrame) -> Dict[str, Any]:
    """트렌드 분석"""
    if df.empty:
        return {"trend": "insufficient_data"}
    
    # 최근 2주간의 데이터로 트렌드 분석
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    recent_dates = sorted(df['date'].unique())[-14:]  # 최근 14일
    
    if len(recent_dates) < 7:
        return {"trend": "insufficient_data"}
    
    # 전반부와 후반부 비교
    mid_point = len(recent_dates) // 2
    early_dates = recent_dates[:mid_point]
    late_dates = recent_dates[mid_point:]
    
    early_data = df[df['date'].isin(early_dates)]
    late_data = df[df['date'].isin(late_dates)]
    
    early_spending = (early_data['price'] * early_data['cnt']).sum()
    late_spending = (late_data['price'] * late_data['cnt']).sum()
    
    if early_spending == 0:
        trend = "increasing"
    else:
        change_pct = ((late_spending - early_spending) / early_spending) * 100
        if change_pct > 20:
            trend = "increasing"
        elif change_pct < -20:
            trend = "decreasing"
        else:
            trend = "stable"
    
    return {
        "trend": trend,
        "change_percentage": round(change_pct if 'change_pct' in locals() else 0, 1),
        "trend_description": {
            "increasing": "구매가 증가하는 추세입니다",
            "decreasing": "구매가 감소하는 추세입니다",
            "stable": "안정적인 구매 패턴을 보입니다"
        }.get(trend, "데이터가 부족합니다")
    }

def _generate_data_driven_recommendations(df: pd.DataFrame) -> List[str]:
    """데이터 기반 추천 생성"""
    recommendations = []
    
    # 카테고리 분석 기반 추천
    category_counts = df['type'].value_counts()
    total_purchases = len(df)
    
    for category, count in category_counts.items():
        ratio = count / total_purchases
        if category == '간식' and ratio > 0.5:
            recommendations.append("간식 비중이 높습니다. 다른 카테고리도 고려해보세요")
        elif category == '교육' and ratio < 0.1:
            recommendations.append("교육 아이템 구매를 늘려보세요")
    
    # 가격대 분석 기반 추천
    avg_price = df['price'].mean()
    if avg_price > 10000:
        recommendations.append("고가 아이템이 많습니다. 적정 가격대를 고려해보세요")
    elif avg_price < 1000:
        recommendations.append("저가 아이템 위주입니다. 품질도 함께 고려해보세요")
    
    return recommendations

def _analyze_behavioral_patterns(df: pd.DataFrame) -> Dict[str, Any]:
    """행동 패턴 분석"""
    if df.empty:
        return {"patterns": "insufficient_data"}
    
    # 예시: 구매 빈도수에 따른 패턴 분류
    purchase_frequency = df['date'].value_counts().reset_index()
    purchase_frequency.columns = ['date', 'frequency']
    purchase_frequency = purchase_frequency.sort_values(by='date')
    
    # 주간 패턴 분석
    weekly_pattern = purchase_frequency.groupby(purchase_frequency['date'].dt.day_name()).sum().reset_index()
    weekly_pattern['day_of_week'] = pd.Categorical(weekly_pattern['date'], categories=[
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], ordered=True)
    weekly_pattern = weekly_pattern.sort_values('day_of_week')
    
    # 월간 패턴 분석
    monthly_pattern = purchase_frequency.groupby(purchase_frequency['date'].dt.to_period("M")).sum().reset_index()
    monthly_pattern['date'] = monthly_pattern['date'].dt.to_timestamp()
    
    return {
        "daily_pattern": purchase_frequency.to_dict(orient='records'),
        "weekly_pattern": weekly_pattern.to_dict(orient='records'),
        "monthly_pattern": monthly_pattern.to_dict(orient='records')
    }

def _analyze_personality_trends(df: pd.DataFrame, days: int) -> Dict[str, Any]:
    """성향 변화 추이 분석"""
    if df.empty:
        return {"trends": "insufficient_data"}
    
    # 날짜 범위 설정
    end_date = df['date'].max()
    start_date = end_date - timedelta(days=days)
    
    # 기간 내 데이터 필터링
    df_period = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    if df_period.empty:
        return {"trends": "insufficient_data"}
    
    # 성향 분석 모델 초기화
    personality_analyzer = PersonalityAnalyzer()
    
    # 기간별 성향 분석 결과 저장
    trends = []
    
    for single_date in pd.date_range(start=start_date, end=end_date):
        daily_data = df_period[df_period['date'] == single_date]
        
        if daily_data.empty:
            continue
        
        personality_insights = personality_analyzer.get_personality_insights(daily_data)
        trends.append({
            "date": single_date.isoformat(),
            "personality": personality_insights.get('personality'),
            "confidence": personality_insights.get('confidence')
        })
    
    return {"trends": trends}

def _comprehensive_risk_assessment(df: pd.DataFrame) -> Dict[str, Any]:
    """종합 위험도 평가"""
    if df.empty:
        return {"risk_assessment": "insufficient_data"}
    
    # 예시: 최근 30일간의 구매 데이터 기반 위험도 평가
    end_date = df['date'].max()
    start_date = end_date - timedelta(days=30)
    df_recent = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    
    if df_recent.empty:
        return {"risk_assessment": "insufficient_data"}
    
    # 위험도 평가 지표 계산
    total_spending = (df_recent['price'] * df_recent['cnt']).sum()
    unique_items = df_recent['item_id'].nunique()
    high_risk_items = df_recent[df_recent['risk_level'] == 'high']['item_id'].nunique()
    
    return {
        "total_spending_last_30_days": total_spending,
        "unique_items_purchased": unique_items,
        "high_risk_items_purchased": high_risk_items
    }
