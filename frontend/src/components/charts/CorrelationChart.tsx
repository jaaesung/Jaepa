import React from 'react';
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface CorrelationData {
  date: string;
  price: number;
  sentiment: number;
  volume?: number;
}

interface CorrelationChartProps {
  data: CorrelationData[];
  symbol: string;
  height?: number;
  showVolume?: boolean;
}

const CorrelationChart: React.FC<CorrelationChartProps> = ({
  data,
  symbol,
  height = 400,
  showVolume = true,
}) => {
  // 감성 데이터를 0-100 스케일로 변환 (-1~1 -> 0~100)
  const normalizedData = data.map(item => ({
    ...item,
    normalizedSentiment: (item.sentiment + 1) * 50, // -1~1 범위를 0~100 범위로 변환
  }));

  // 감성 색상 결정 함수
  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.3) return '#52c41a'; // 긍정
    if (sentiment < -0.3) return '#ff4d4f'; // 부정
    return '#faad14'; // 중립
  };

  // 평균 감성 점수 계산
  const avgSentiment = data.reduce((sum, item) => sum + item.sentiment, 0) / data.length;
  const sentimentColor = getSentimentColor(avgSentiment);

  // 평균 상관 계수 (간단한 피어슨 상관 계수 계산)
  const calculateCorrelation = () => {
    // 평균 계산
    const meanPrice = data.reduce((sum, item) => sum + item.price, 0) / data.length;
    const meanSentiment = data.reduce((sum, item) => sum + item.sentiment, 0) / data.length;

    // 표준 편차 및 공분산 계산을 위한 변수
    let sumCov = 0;
    let sumVarPrice = 0;
    let sumVarSentiment = 0;

    data.forEach(item => {
      const diffPrice = item.price - meanPrice;
      const diffSentiment = item.sentiment - meanSentiment;

      sumCov += diffPrice * diffSentiment;
      sumVarPrice += diffPrice * diffPrice;
      sumVarSentiment += diffSentiment * diffSentiment;
    });

    // 상관 계수 계산
    const correlation = sumCov / Math.sqrt(sumVarPrice * sumVarSentiment);
    return correlation;
  };

  const correlation = calculateCorrelation();
  const correlationText =
    correlation > 0 ? '긍정적 상관관계' : correlation < 0 ? '부정적 상관관계' : '상관관계 없음';

  return (
    <div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: '10px',
        }}
      >
        <h3>{symbol} 주가 및 감성 상관관계</h3>
        <div style={{ display: 'flex', gap: '20px' }}>
          <div>
            <span style={{ fontWeight: 'bold' }}>평균 감성:</span>{' '}
            <span style={{ color: sentimentColor, fontWeight: 'bold' }}>
              {(avgSentiment > 0 ? '+' : '') + avgSentiment.toFixed(2)}
            </span>
          </div>
          <div>
            <span style={{ fontWeight: 'bold' }}>상관 계수:</span>{' '}
            <span style={{ fontWeight: 'bold' }}>
              {correlation.toFixed(2)} ({correlationText})
            </span>
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={normalizedData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tickFormatter={dateStr => {
              const date = new Date(dateStr);
              return `${date.getMonth() + 1}/${date.getDate()}`;
            }}
          />
          <YAxis
            yAxisId="price"
            domain={['auto', 'auto']}
            orientation="left"
            tick={{ fill: '#1f77b4' }}
            label={{
              value: '주가',
              angle: -90,
              position: 'insideLeft',
              fill: '#1f77b4',
            }}
          />
          <YAxis
            yAxisId="sentiment"
            domain={[0, 100]}
            orientation="right"
            tick={{ fill: sentimentColor }}
            label={{
              value: '감성',
              angle: 90,
              position: 'insideRight',
              fill: sentimentColor,
            }}
          />
          {showVolume && (
            <YAxis yAxisId="volume" orientation="right" domain={['auto', 'auto']} hide={true} />
          )}
          <Tooltip
            formatter={(value, name) => {
              if (name === 'normalizedSentiment') {
                return [((value as number) / 50 - 1).toFixed(2), '감성 점수'];
              }
              if (name === 'price') {
                return [value, '주가'];
              }
              if (name === 'volume') {
                return [new Intl.NumberFormat().format(value as number), '거래량'];
              }
              return [value, name];
            }}
            labelFormatter={label => {
              const date = new Date(label);
              return date.toLocaleDateString('ko-KR');
            }}
          />
          <Legend
            payload={[
              { value: '주가', type: 'line' as const, color: '#1f77b4' },
              {
                value: '감성 점수',
                type: 'line' as const,
                color: sentimentColor,
              },
              ...(showVolume ? [{ value: '거래량', type: 'rect' as const, color: '#8884d8' }] : []),
            ]}
          />

          {showVolume && (
            <Bar dataKey="volume" yAxisId="volume" fill="#8884d8" opacity={0.3} name="거래량" />
          )}

          <Line
            type="monotone"
            dataKey="price"
            stroke="#1f77b4"
            name="주가"
            yAxisId="price"
            strokeWidth={2}
            dot={{ r: 2 }}
            activeDot={{ r: 6 }}
          />
          <Line
            type="monotone"
            dataKey="normalizedSentiment"
            stroke={sentimentColor}
            name="감성 점수"
            yAxisId="sentiment"
            strokeWidth={2}
            dot={{ r: 2 }}
            activeDot={{ r: 6 }}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CorrelationChart;
