import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, ShoppingCart, Target, Award, AlertTriangle, Calendar, Clock, RefreshCw } from 'lucide-react';

// 타입 정의
interface Metrics {
  thisWeekTotal: number;
  weeklyChange: number;
  mostPopularCategory: string;
  educationRatio: number;
  totalPurchases: number;
  avgPurchaseAmount: number;
}

interface WeeklyTrendItem {
  day: string;
  간식: number;
  오락: number;
  장난감: number;
  교육: number;
  기타: number;
}

interface CategoryDataItem {
  name: string;
  value: number;
  color: string;
}

interface HourlyDataItem {
  hour: string;
  purchases: number;
}

interface PopularProduct {
  name: string;
  category: string;
  count: number;
  totalAmount: number;
  avgPrice: number;
}

interface Alert {
  type: 'warning' | 'info' | 'success';
  title: string;
  message: string;
}

interface Child {
  child_id: string;
  name: string;
  total_purchases?: number;
  last_purchase_date?: string | null;
}

interface DashboardData {
  metrics: Metrics;
  weeklyTrend: WeeklyTrendItem[];
  categoryData: CategoryDataItem[];
  hourlyData: HourlyDataItem[];
  popularProducts: PopularProduct[];
  alerts: Alert[];
  lastUpdated: string;
}

// API 호출 함수들
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const fetchDashboardData = async (childId: string, days = 30): Promise<DashboardData> => {
  try {
    console.log(`🔥 Fetching dashboard data for childId: ${childId}, days: ${days}`);
    const url = `${API_BASE_URL}/api/dashboard/${childId}?days=${days}`;
    console.log(`🔥 API URL: ${url}`);
    
    const response = await fetch(url);
    console.log(`🔥 Response status: ${response.status}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log(`🔥 Raw API response:`, data);
    
    // API 응답이 이미 올바른 형식인지 확인하고 필요시 기본값 설정
    const transformedData: DashboardData = {
      metrics: data.metrics || {
        thisWeekTotal: 0,
        weeklyChange: 0,
        mostPopularCategory: '없음',
        educationRatio: 0,
        totalPurchases: 0,
        avgPurchaseAmount: 0,
      },
      weeklyTrend: data.weeklyTrend || [],
      categoryData: data.categoryData || [],
      hourlyData: data.hourlyData || [],
      popularProducts: data.popularProducts || [],
      alerts: data.alerts || [],
      lastUpdated: data.lastUpdated || new Date().toISOString()
    };
    console.log(`🔥 Transformed data:`, transformedData);
    return transformedData;
  } catch (error) {
    console.error('🚨 Dashboard data fetch error:', error);
    throw error;
  }
};

const fetchChildren = async (): Promise<{ children: Child[] }> => {
  return {
    children: [
      {
        child_id: 'd0a188a3-e24e-4772-95f7-07e59ce8885e',
        name: '아이1',
        total_purchases: 0,
        last_purchase_date: null
      }
    ]
  };
};

const SimpleKidHabitsDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [children, setChildren] = useState<Child[]>([]);
  const [selectedChild, setSelectedChild] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<number>(30);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  console.log('=== SimpleKidHabitsDashboard RENDER ===', {
    loading,
    error,
    dashboardData: !!dashboardData,
    selectedChild,
    childrenLength: children.length,
    timestamp: new Date().toISOString()
  });

  // 초기 데이터 로드
  const loadData = async () => {
    try {
      console.log('🚀 Starting loadData...');
      setLoading(true);
      setError(null);

      // 아이 목록 가져오기
      console.log('📋 Fetching children...');
      const childrenResponse = await fetchChildren();
      console.log('📋 Children loaded:', childrenResponse);
      setChildren(childrenResponse.children);

      // 첫 번째 child 선택
      if (childrenResponse.children.length > 0) {
        const firstChild = childrenResponse.children[0].child_id;
        setSelectedChild(firstChild);
        console.log('👶 Selected first child:', firstChild);

        // 대시보드 데이터 가져오기
        console.log('📊 Fetching dashboard data...');
        const dashboard = await fetchDashboardData(firstChild, selectedPeriod);
        console.log('📊 Dashboard data loaded:', dashboard);
        setDashboardData(dashboard);
      } else {
        console.warn('⚠️ No children found!');
      }
      
      setLastUpdated(new Date());
      console.log('✅ loadData completed successfully');
    } catch (err) {
      console.error('🚨 Data loading error:', err);
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
      console.log('🏁 loadData finished (loading set to false)');
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // 선택 변경 시 대시보드 데이터 다시 로드
  useEffect(() => {
    if (selectedChild && children.length > 0) {
      const loadDashboardOnly = async () => {
        try {
          setLoading(true);
          const dashboard = await fetchDashboardData(selectedChild, selectedPeriod);
          setDashboardData(dashboard);
          setLastUpdated(new Date());
        } catch (err) {
          console.error('Dashboard reload error:', err);
          setError(err instanceof Error ? err.message : 'Unknown error occurred');
        } finally {
          setLoading(false);
        }
      };
      loadDashboardOnly();
    }
  }, [selectedChild, selectedPeriod]);

  // 메트릭 카드 컴포넌트
  interface MetricCardProps {
    title: string;
    value: string;
    change?: number | null;
    icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>;
    color: string;
    description?: string;
  }

  const MetricCard: React.FC<MetricCardProps> = ({ title, value, change, icon: Icon, color, description }) => (
    <div className="bg-white rounded-lg shadow-md p-6 border-l-4 hover:shadow-lg transition-shadow" style={{ borderLeftColor: color }}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {change !== undefined && change !== null && (
            <div className="flex items-center mt-2">
              {change > 0 ? (
                <TrendingUp className="h-4 w-4 text-green-500" />
              ) : change < 0 ? (
                <TrendingDown className="h-4 w-4 text-red-500" />
              ) : (
                <div className="h-4 w-4" />
              )}
              <span className={`ml-1 text-sm ${
                change > 0 ? 'text-green-500' : 
                change < 0 ? 'text-red-500' : 'text-gray-500'
              }`}>
                {change !== 0 ? `${Math.abs(change).toFixed(1)}% 전주 대비` : '변화 없음'}
              </span>
            </div>
          )}
          {description && (
            <p className="text-xs text-gray-500 mt-1">{description}</p>
          )}
        </div>
        <Icon className="h-12 w-12" style={{ color }} />
      </div>
    </div>
  );

  // 로딩 상태
  if (loading) {
    console.log('🔄 Rendering loading state');
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  // 에러 상태
  if (error) {
    console.log('🚨 Rendering error state:', error);
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">데이터 로드 실패</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={loadData}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center mx-auto"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  // 데이터가 없는 경우
  if (!dashboardData) {
    console.log('📊 No dashboard data available');
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <ShoppingCart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">데이터가 없습니다</h2>
          <p className="text-gray-600">선택한 기간에 구매 데이터가 없습니다.</p>
        </div>
      </div>
    );
  }

  console.log('🎉 Rendering main dashboard with data:', dashboardData);

  const { metrics, alerts } = dashboardData;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🎮 우리 아이 습관 대시보드 (간단 버전)
        </h1>
        <p className="text-gray-600">
          실시간 구매 데이터 기반 아이의 소비 패턴을 분석해보세요
        </p>
        <div className="mt-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Calendar className="h-4 w-4" />
              <span>최근 {selectedPeriod}일 데이터 기준</span>
            </div>
            {lastUpdated && (
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <Clock className="h-4 w-4" />
                <span>마지막 업데이트: {lastUpdated.toLocaleString('ko-KR')}</span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-4">
            {/* 아이 선택 */}
            <select 
              value={selectedChild || ''} 
              onChange={(e) => setSelectedChild(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {children.map(child => (
                <option key={child.child_id} value={child.child_id}>
                  {child.name}
                </option>
              ))}
            </select>
            {/* 기간 선택 */}
            <select 
              value={selectedPeriod} 
              onChange={(e) => setSelectedPeriod(Number(e.target.value))}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={7}>최근 7일</option>
              <option value={30}>최근 30일</option>
              <option value={90}>최근 90일</option>
            </select>
            {/* 새로고침 버튼 */}
            <button 
              onClick={loadData}
              className="px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              새로고침
            </button>
          </div>
        </div>
      </div>

      {/* 메인 지표 카드들 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="이번 주 총 소비"
          value={`${(metrics.thisWeekTotal || 0).toLocaleString()}원`}
          change={metrics.weeklyChange || 0}
          icon={ShoppingCart}
          color="#4ecdc4"
          description={`총 ${metrics.totalPurchases || 0}건 구매`}
        />
        <MetricCard
          title="가장 인기 카테고리"
          value={metrics.mostPopularCategory || '데이터 없음'}
          change={null}
          icon={Award}
          color="#ff6b6b"
          description="이번 주 최다 구매"
        />
        <MetricCard
          title="교육 아이템 비중"
          value={`${(metrics.educationRatio || 0).toFixed(1)}%`}
          change={(metrics.educationRatio || 0) - 20}
          icon={Target}
          color="#96ceb4"
          description="권장: 20% 이상"
        />
        <MetricCard
          title="평균 구매 단가"
          value={`${(metrics.avgPurchaseAmount || 0).toLocaleString()}원`}
          change={null}
          icon={TrendingUp}
          color="#45b7d1"
          description="건당 평균 금액"
        />
      </div>

      {/* 알림 섹션 */}
      {alerts && alerts.length > 0 && (
        <div className="mb-8 space-y-3">
          {alerts.map((alert, index) => (
            <div key={`alert-${index}`} className={`border-l-4 p-4 ${
              alert.type === 'warning' ? 'bg-yellow-50 border-yellow-400' :
              alert.type === 'info' ? 'bg-blue-50 border-blue-400' :
              'bg-green-50 border-green-400'
            }`}>
              <div className="flex">
                <AlertTriangle className={`h-5 w-5 ${
                  alert.type === 'warning' ? 'text-yellow-400' :
                  alert.type === 'info' ? 'text-blue-400' :
                  'text-green-400'
                }`} />
                <div className="ml-3">
                  <p className={`text-sm ${
                    alert.type === 'warning' ? 'text-yellow-700' :
                    alert.type === 'info' ? 'text-blue-700' :
                    'text-green-700'
                  }`}>
                    <strong>{alert.title}:</strong> {alert.message}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 간단한 텍스트 기반 통계 */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          📈 주간 요약 리포트
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <p className="text-2xl font-bold text-blue-600">
              {metrics.totalPurchases || 0}
            </p>
            <p className="text-sm text-blue-800">총 구매 건수</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <p className="text-2xl font-bold text-green-600">
              {(metrics.avgPurchaseAmount || 0).toLocaleString()}원
            </p>
            <p className="text-sm text-green-800">평균 구매 단가</p>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <p className="text-2xl font-bold text-purple-600">
              {metrics.mostPopularCategory || '없음'}
            </p>
            <p className="text-sm text-purple-800">인기 카테고리</p>
          </div>
        </div>
      </div>

      {/* 푸터 */}
      <div className="mt-12 text-center text-gray-500 text-sm">
        <p>💝 데이터 기반 건강한 소비 습관을 응원합니다!</p>
        <p className="mt-2">
          차트 없는 간단 버전 - API 기반 실시간 분석 시스템
        </p>
      </div>
    </div>
  );
};

export default SimpleKidHabitsDashboard;
