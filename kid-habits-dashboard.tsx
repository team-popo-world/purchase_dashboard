import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, ShoppingCart, Target, Award, AlertTriangle, Calendar, Clock } from 'lucide-react';

// 실제 DB 구조에 맞는 샘플 데이터 생성
const generateRealisticData = () => {
  const categories = ['간식', '오락', '장난감', '교육', '기타'];
  const productsByCategory = {
    '간식': ['초코송이', '사탕', '과자', '아이스크림', '젤리'],
    '오락': ['TV 시청 1시간권', '게임시간', '유튜브 시청권', '영화감상권'],
    '장난감': ['레고', '인형', '자동차 장난감', '퍼즐', '슬라임'],
    '교육': ['책', '문구세트', '학습지', '교육앱 이용권'],
    '기타': ['스티커', '색연필', '만들기키트', '포스터']
  };

  // PurchaseHistory 테이블 구조에 맞는 구매 이력 데이터
  const purchaseHistory = [];
  const now = new Date();
  
  // 최근 30일간의 구매 데이터 생성
  for (let i = 0; i < 150; i++) {
    const category = categories[Math.floor(Math.random() * categories.length)];
    const products = productsByCategory[category];
    const product = products[Math.floor(Math.random() * products.length)];
    
    const daysAgo = Math.floor(Math.random() * 30);
    const timestamp = new Date(now.getTime() - (daysAgo * 24 * 60 * 60 * 1000));
    
    // 시간대별 가중치 (7-21시에 더 많은 구매)
    const hour = Math.floor(Math.random() * 24);
    const hourWeight = (hour >= 7 && hour <= 21) ? 0.8 : 0.2;
    
    if (Math.random() < hourWeight) {
      purchaseHistory.push({
        id: `purchase_${i}`,
        type: category,
        name: product,
        price: Math.floor(Math.random() * 400) + 50, // 50-450원
        cnt: Math.floor(Math.random() * 3) + 1, // 1-3개
        timestamp: timestamp,
        child_id: 'child_001'
      });
    }
  }

  return purchaseHistory.sort((a, b) => b.timestamp - a.timestamp);
};

const KidHabitsDashboard = () => {
  const [purchaseData, setPurchaseData] = useState([]);
  const [selectedPeriod, setSelectedPeriod] = useState('week');
  const [selectedChild, setSelectedChild] = useState('child_001');

  useEffect(() => {
    setPurchaseData(generateRealisticData());
  }, []);

  // 데이터 분석 함수들
  const analyzeData = () => {
    const now = new Date();
    const oneWeekAgo = new Date(now.getTime() - (7 * 24 * 60 * 60 * 1000));
    const twoWeeksAgo = new Date(now.getTime() - (14 * 24 * 60 * 60 * 1000));

    // 이번 주 데이터
    const thisWeekData = purchaseData.filter(item => 
      new Date(item.timestamp) >= oneWeekAgo
    );

    // 지난 주 데이터
    const lastWeekData = purchaseData.filter(item => 
      new Date(item.timestamp) >= twoWeeksAgo && 
      new Date(item.timestamp) < oneWeekAgo
    );

    // 총 소비액 계산
    const thisWeekTotal = thisWeekData.reduce((sum, item) => sum + (item.price * item.cnt), 0);
    const lastWeekTotal = lastWeekData.reduce((sum, item) => sum + (item.price * item.cnt), 0);
    const weeklyChange = lastWeekTotal > 0 ? ((thisWeekTotal - lastWeekTotal) / lastWeekTotal * 100) : 0;

    // 카테고리별 분석
    const categoryAnalysis = {};
    thisWeekData.forEach(item => {
      if (!categoryAnalysis[item.type]) {
        categoryAnalysis[item.type] = { count: 0, amount: 0 };
      }
      categoryAnalysis[item.type].count += item.cnt;
      categoryAnalysis[item.type].amount += (item.price * item.cnt);
    });

    const mostPopularCategory = Object.entries(categoryAnalysis)
      .sort(([,a], [,b]) => b.amount - a.amount)[0];

    // 주간 일별 데이터
    const weeklyTrend = [];
    const days = ['일', '월', '화', '수', '목', '금', '토'];
    
    for (let i = 6; i >= 0; i--) {
      const targetDate = new Date(now.getTime() - (i * 24 * 60 * 60 * 1000));
      const dayData = { day: days[targetDate.getDay()] };
      
      ['간식', '오락', '장난감', '교육', '기타'].forEach(category => {
        const dayTotal = purchaseData
          .filter(item => {
            const itemDate = new Date(item.timestamp);
            return itemDate.toDateString() === targetDate.toDateString() && 
                   item.type === category;
          })
          .reduce((sum, item) => sum + (item.price * item.cnt), 0);
        dayData[category] = dayTotal;
      });
      
      weeklyTrend.push(dayData);
    }

    // 카테고리별 파이차트 데이터
    const categoryPieData = Object.entries(categoryAnalysis).map(([category, data]) => ({
      name: category,
      value: data.amount,
      color: {
        '간식': '#ff6b6b',
        '오락': '#4ecdc4', 
        '장난감': '#45b7d1',
        '교육': '#96ceb4',
        '기타': '#ffeaa7'
      }[category] || '#gray'
    }));

    // 시간대별 구매 패턴
    const hourlyPattern = Array(24).fill(0);
    thisWeekData.forEach(item => {
      const hour = new Date(item.timestamp).getHours();
      hourlyPattern[hour] += item.cnt;
    });

    const hourlyData = hourlyPattern.map((count, hour) => ({
      hour: `${hour}시`,
      purchases: count
    }));

    // 인기 상품 분석
    const productStats = {};
    thisWeekData.forEach(item => {
      if (!productStats[item.name]) {
        productStats[item.name] = {
          name: item.name,
          category: item.type,
          count: 0,
          totalAmount: 0,
          avgPrice: 0
        };
      }
      productStats[item.name].count += item.cnt;
      productStats[item.name].totalAmount += (item.price * item.cnt);
      productStats[item.name].avgPrice = productStats[item.name].totalAmount / productStats[item.name].count;
    });

    const popularProducts = Object.values(productStats)
      .sort((a, b) => b.count - a.count)
      .slice(0, 8);

    // 교육 아이템 비중 계산
    const educationAmount = categoryAnalysis['교육']?.amount || 0;
    const educationRatio = thisWeekTotal > 0 ? (educationAmount / thisWeekTotal * 100) : 0;

    return {
      thisWeekTotal,
      weeklyChange,
      mostPopularCategory: mostPopularCategory ? mostPopularCategory[0] : '데이터 없음',
      educationRatio,
      weeklyTrend,
      categoryPieData,
      hourlyData,
      popularProducts,
      categoryAnalysis
    };
  };

  const analysis = analyzeData();

  // 메트릭 카드 컴포넌트
  const MetricCard = ({ title, value, change, icon: Icon, color, description }) => (
    <div className="bg-white rounded-lg shadow-md p-6 border-l-4 hover:shadow-lg transition-shadow" style={{ borderLeftColor: color }}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {change !== undefined && (
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

  // 알림 생성 로직
  const generateAlerts = () => {
    const alerts = [];
    
    // 간식 과다 소비 체크
    const snackRatio = analysis.categoryAnalysis['간식']?.amount || 0;
    const totalAmount = analysis.thisWeekTotal;
    if (totalAmount > 0 && (snackRatio / totalAmount) > 0.4) {
      alerts.push({
        type: 'warning',
        title: '간식 소비 주의',
        message: '이번 주 간식 구매가 전체의 40%를 넘었어요. 균형 잡힌 소비를 권장해요!'
      });
    }

    // 교육 아이템 부족 체크
    if (analysis.educationRatio < 15) {
      alerts.push({
        type: 'info',
        title: '교육 아이템 추천',
        message: '교육 관련 구매가 적어요. 학습 도서나 교육 도구를 고려해보세요!'
      });
    }

    // 긍정적 변화 감지
    if (analysis.weeklyChange < -10) {
      alerts.push({
        type: 'success',
        title: '절약 성공',
        message: '지난 주보다 소비가 줄었어요. 훌륭한 절약 습관이에요! 🎉'
      });
    }

    return alerts;
  };

  const alerts = generateAlerts();

  if (purchaseData.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">구매 데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

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
        <div className="mt-4 flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Calendar className="h-4 w-4" />
            <span>최근 7일 데이터 기준</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Clock className="h-4 w-4" />
            <span>마지막 업데이트: {new Date().toLocaleString('ko-KR')}</span>
          </div>
        </div>
      </div>

      {/* 메인 지표 카드들 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title="이번 주 총 소비"
          value={`${analysis.thisWeekTotal.toLocaleString()}원`}
          change={analysis.weeklyChange}
          icon={ShoppingCart}
          color="#4ecdc4"
          description={`총 ${purchaseData.filter(item => 
            new Date(item.timestamp) >= new Date(Date.now() - 7*24*60*60*1000)
          ).length}건 구매`}
        />
        <MetricCard
          title="가장 인기 카테고리"
          value={analysis.mostPopularCategory}
          change={0}
          icon={Award}
          color="#ff6b6b"
          description="이번 주 최다 구매"
        />
        <MetricCard
          title="교육 아이템 비중"
          value={`${analysis.educationRatio.toFixed(1)}%`}
          change={analysis.educationRatio - 20} // 목표 20% 기준
          icon={Target}
          color="#96ceb4"
          description="권장: 20% 이상"
        />
        <MetricCard
          title="평균 구매 단가"
          value={`${Math.round(analysis.thisWeekTotal / Math.max(1, purchaseData.filter(item => 
            new Date(item.timestamp) >= new Date(Date.now() - 7*24*60*60*1000)
          ).length)).toLocaleString()}원`}
          change={0}
          icon={TrendingUp}
          color="#45b7d1"
          description="건당 평균 금액"
        />
      </div>

      {/* 알림 섹션 */}
      {alerts.length > 0 && (
        <div className="mb-8 space-y-3">
          {alerts.map((alert, index) => (
            <div key={index} className={`border-l-4 p-4 ${
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
            <BarChart data={analysis.weeklyTrend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip 
                formatter={(value, name) => [`${value.toLocaleString()}원`, name]} 
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
                data={analysis.categoryPieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {analysis.categoryPieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [`${value.toLocaleString()}원`, '소비액']} />
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
            <LineChart data={analysis.hourlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip formatter={(value) => [`${value}건`, '구매 횟수']} />
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
            {analysis.popularProducts.map((product, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="flex items-center">
                  <span className="text-lg font-bold text-gray-500 w-8">
                    {index + 1}
                  </span>
                  <div className="ml-3">
                    <p className="font-medium text-gray-900">{product.name}</p>
                    <p className="text-sm text-gray-500">{product.category}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900">{product.count}개</p>
                  <p className="text-sm text-gray-500">{Math.round(product.avgPrice).toLocaleString()}원</p>
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
              {purchaseData.filter(item => 
                new Date(item.timestamp) >= new Date(Date.now() - 7*24*60*60*1000)
              ).length}
            </p>
            <p className="text-sm text-blue-800">총 구매 건수</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <p className="text-2xl font-bold text-green-600">
              {Object.keys(analysis.categoryAnalysis).length}
            </p>
            <p className="text-sm text-green-800">구매한 카테고리 수</p>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <p className="text-2xl font-bold text-purple-600">
              {new Set(purchaseData
                .filter(item => new Date(item.timestamp) >= new Date(Date.now() - 7*24*60*60*1000))
                .map(item => item.name)
              ).size}
            </p>
            <p className="text-sm text-purple-800">구매한 상품 종류</p>
          </div>
        </div>
      </div>

      {/* 푸터 */}
      <div className="mt-12 text-center text-gray-500 text-sm">
        <p>💝 데이터 기반 건강한 소비 습관을 응원합니다!</p>
        <p className="mt-2">
          총 {purchaseData.length}건의 구매 데이터를 분석했습니다.
        </p>
      </div>
    </div>
  );
};

export default KidHabitsDashboard;