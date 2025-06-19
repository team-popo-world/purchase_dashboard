import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
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

interface CategoryData {
  name: string;
  value: number;
  color: string;
}

interface HourlyData {
  hour: string;
  purchases: number;
}

interface PopularProduct {
  name: string;
  category: string;
  count: number;
  avgPrice: number;
}

interface Alert {
  title: string;
  message: string;
  type: 'warning' | 'info' | 'success';
}

interface DashboardData {
  metrics: Metrics;
  weeklyTrend: WeeklyTrendItem[];
  categoryData: CategoryData[];
  hourlyData: HourlyData[];
  popularProducts: PopularProduct[];
  alerts: Alert[];
}

interface Child {
  child_id: string;
}

// API 호출 함수들
const API_BASE_URL = 'http://localhost:8000';  // 직접 FastAPI 서버 호출

const fetchDashboardData = async (childId: string, days = 30): Promise<DashboardData> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/${childId}?days=${days}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Dashboard data fetch error:', error);
    throw error;
  }
};

const fetchChildren = async (): Promise<{ children: Child[] }> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/children`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Children fetch error:', error);
    throw error;
  }
};

const KidHabitsDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [children, setChildren] = useState<Child[]>([]);
  const [selectedChild, setSelectedChild] = useState<string>('child_001');
  const [selectedPeriod, setSelectedPeriod] = useState<number>(30);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // 데이터 로드 함수
  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 아이 목록 가져오기
      const childrenResponse = await fetchChildren();
      setChildren(childrenResponse.children);

      // 대시보드 데이터 가져오기
      const dashboard = await fetchDashboardData(selectedChild, selectedPeriod);
      setDashboardData(dashboard);
      setLastUpdated(new Date());

    } catch (err) {
      console.error('Data loading error:', err);
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  // 컴포넌트 마운트 시 및 선택 변경 시 데이터 로드
  useEffect(() => {
    loadData();
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

  const { metrics, weeklyTrend, categoryData, hourlyData, popularProducts, alerts } = dashboardData;

  // 안전한 데이터 접근을 위한 기본값 설정
  const safeMetrics = metrics || {};
  const safeWeeklyTrend = weeklyTrend || [];
  const safeCategoryData = categoryData || [];
  const safeHourlyData = hourlyData || [];
  const safePopularProducts = popularProducts || [];
  const safeAlerts = alerts || [];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* 헤더 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🎮 우리 아이 습관 대시보드
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
              value={selectedChild} 
              onChange={(e) => setSelectedChild(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {children.map(child => (
                <option key={child.child_id} value={child.child_id}>
                  {child.child_id}
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
          value={`${(safeMetrics.thisWeekTotal || 0).toLocaleString()}원`}
          change={safeMetrics.weeklyChange || 0}
          icon={ShoppingCart}
          color="#4ecdc4"
          description={`총 ${safeMetrics.totalPurchases || 0}건 구매`}
        />
        <MetricCard
          title="가장 인기 카테고리"
          value={safeMetrics.mostPopularCategory || '데이터 없음'}
          change={null}
          icon={Award}
          color="#ff6b6b"
          description="이번 주 최다 구매"
        />
        <MetricCard
          title="교육 아이템 비중"
          value={`${(safeMetrics.educationRatio || 0).toFixed(1)}%`}
          change={(safeMetrics.educationRatio || 0) - 20} // 목표 20% 기준
          icon={Target}
          color="#96ceb4"
          description="권장: 20% 이상"
        />
        <MetricCard
          title="평균 구매 단가"
          value={`${(safeMetrics.avgPurchaseAmount || 0).toLocaleString()}원`}
          change={null}
          icon={TrendingUp}
          color="#45b7d1"
          description="건당 평균 금액"
        />
      </div>

      {/* 알림 섹션 */}
      {safeAlerts && safeAlerts.length > 0 && (
        <div className="mb-8 space-y-3">
          {safeAlerts.map((alert, index) => (
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* 주간 카테고리별 소비 추이 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            📊 주간 카테고리별 소비 추이
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={safeWeeklyTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip 
                formatter={(value, name) => [`${(value || 0).toLocaleString()}원`, name]} 
                labelFormatter={(label) => `${label}요일`}
              />
              <Legend />
              <Bar dataKey="간식" stackId="a" fill="#ff6b6b" />
              <Bar dataKey="오락" stackId="a" fill="#4ecdc4" />
              <Bar dataKey="장난감" stackId="a" fill="#45b7d1" />
              <Bar dataKey="교육" stackId="a" fill="#96ceb4" />
              <Bar dataKey="기타" stackId="a" fill="#ffeaa7" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 카테고리별 비중 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            🎯 카테고리별 소비 비중
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={safeCategoryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {safeCategoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color || '#8884d8'} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`${(value || 0).toLocaleString()}원`, '소비액']} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* 시간대별 구매 패턴 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            ⏰ 시간대별 구매 패턴
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={safeHourlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip formatter={(value) => [`${value || 0}건`, '구매 횟수']} />
              <Line 
                type="monotone" 
                dataKey="purchases" 
                stroke="#4ecdc4" 
                strokeWidth={3}
                dot={{ fill: '#4ecdc4' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* 인기 상품 랭킹 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            🏆 이번 주 인기 상품 TOP 8
          </h3>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {safePopularProducts.map((product, index) => (
              <div key={`product-${index}`} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="flex items-center">
                  <span className="text-lg font-bold text-gray-500 w-8">
                    {index + 1}
                  </span>
                  <div className="ml-3">
                    <p className="font-medium text-gray-900">{product.name || '상품명'}</p>
                    <p className="text-sm text-gray-500">{product.category || '카테고리'}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900">{product.count || 0}개</p>
                  <p className="text-sm text-gray-500">{Math.round(product.avgPrice || 0).toLocaleString()}원</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 요약 통계 */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          📈 주간 요약 리포트
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <p className="text-2xl font-bold text-blue-600">
              {safeMetrics.totalPurchases || 0}
            </p>
            <p className="text-sm text-blue-800">총 구매 건수</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <p className="text-2xl font-bold text-green-600">
              {safeCategoryData.length}
            </p>
            <p className="text-sm text-green-800">구매한 카테고리 수</p>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <p className="text-2xl font-bold text-purple-600">
              {safePopularProducts.length}
            </p>
            <p className="text-sm text-purple-800">구매한 상품 종류</p>
          </div>
        </div>
      </div>

      {/* 푸터 */}
      <div className="mt-12 text-center text-gray-500 text-sm">
        <p>💝 데이터 기반 건강한 소비 습관을 응원합니다!</p>
        <p className="mt-2">
          API 기반 실시간 분석 시스템으로 구동됩니다.
        </p>
      </div>
    </div>
  );
};

export default KidHabitsDashboard;