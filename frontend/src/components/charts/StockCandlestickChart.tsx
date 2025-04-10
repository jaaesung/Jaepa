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
  ReferenceLine,
  ResponsiveContainer
} from 'recharts';

interface CandlestickData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  [key: string]: any; // 추가 기술적 지표를 위한 인덱스 시그니처
}

interface StockCandlestickChartProps {
  data: CandlestickData[];
  height?: number;
  symbol: string;
  showVolume?: boolean;
  indicators?: string[];
}

const StockCandlestickChart: React.FC<StockCandlestickChartProps> = ({
  data,
  height = 500,
  symbol,
  showVolume = true,
  indicators = []
}) => {
  // 가격 범위 계산 (여백 포함)
  const calculateYDomain = () => {
    let minVal = Math.min(...data.map(d => d.low));
    let maxVal = Math.max(...data.map(d => d.high));
    
    // 10% 여백 추가
    const padding = (maxVal - minVal) * 0.1;
    return [Math.max(0, minVal - padding), maxVal + padding];
  };
  
  // 캔들스틱 바 커스텀 렌더링
  const renderCandlestick = (props: any) => {
    const { x, y, width, height, index } = props;
    const item = data[index];
    
    // 상승 또는 하락 결정
    const isRising = item.close >= item.open;
    const color = isRising ? '#f5222d' : '#52c41a'; // 한국 시장에서는 상승은 빨간색, 하락은 녹색
    
    // 고가-저가 선 계산
    const lowY = y + height;
    const highY = y;
    const wickX = x + width / 2;
    
    // 시가-종가 바디 계산
    const openY = isRising ? y + height * (1 - (item.open - item.low) / (item.high - item.low)) : y + height * (1 - (item.close - item.low) / (item.high - item.low));
    const closeY = isRising ? y + height * (1 - (item.close - item.low) / (item.high - item.low)) : y + height * (1 - (item.open - item.low) / (item.high - item.low));
    const barHeight = Math.abs(closeY - openY);
    
    return (
      <g key={index}>
        {/* 고가-저가 심지 */}
        <line x1={wickX} y1={highY} x2={wickX} y2={lowY} stroke={color} strokeWidth={1} />
        
        {/* 시가-종가 바디 */}
        <rect
          x={x}
          y={Math.min(openY, closeY)}
          width={width}
          height={Math.max(1, barHeight)} // 최소 1px 높이 보장
          fill={color}
        />
      </g>
    );
  };
  
  // 툴팁 커스터마이징
  const renderTooltip = (props: any) => {
    const { active, payload, label } = props;
    
    if (active && payload && payload.length) {
      const item = data.find(d => d.date === label);
      if (!item) return null;
      
      const isRising = item.close >= item.open;
      const changeAmount = item.close - item.open;
      const changePercent = (changeAmount / item.open) * 100;
      
      return (
        <div className="custom-tooltip" style={{ 
          backgroundColor: '#fff', 
          padding: '10px', 
          border: '1px solid #ccc',
          borderRadius: '4px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <p style={{ fontWeight: 'bold', marginBottom: '8px' }}>
            {symbol} - {new Date(label).toLocaleDateString('ko-KR')}
          </p>
          
          <div style={{ display: 'grid', gridTemplateColumns: '80px 1fr', gap: '4px 12px' }}>
            <span style={{ color: '#666' }}>시가:</span>
            <span>{new Intl.NumberFormat('ko-KR').format(item.open)}</span>
            
            <span style={{ color: '#666' }}>고가:</span>
            <span>{new Intl.NumberFormat('ko-KR').format(item.high)}</span>
            
            <span style={{ color: '#666' }}>저가:</span>
            <span>{new Intl.NumberFormat('ko-KR').format(item.low)}</span>
            
            <span style={{ color: '#666' }}>종가:</span>
            <span>{new Intl.NumberFormat('ko-KR').format(item.close)}</span>
            
            <span style={{ color: '#666' }}>변동:</span>
            <span style={{ color: isRising ? '#f5222d' : '#52c41a' }}>
              {isRising ? '+' : ''}{new Intl.NumberFormat('ko-KR').format(changeAmount)} 
              ({isRising ? '+' : ''}{changePercent.toFixed(2)}%)
            </span>
            
            {showVolume && (
              <>
                <span style={{ color: '#666' }}>거래량:</span>
                <span>{new Intl.NumberFormat('ko-KR').format(item.volume)}</span>
              </>
            )}
            
            {/* 기술적 지표 표시 */}
            {indicators.includes('SMA') && (
              <>
                <span style={{ color: '#666' }}>SMA(20):</span>
                <span>{item.SMA20 ? new Intl.NumberFormat('ko-KR').format(item.SMA20) : 'N/A'}</span>
              </>
            )}
            
            {indicators.includes('RSI') && (
              <>
                <span style={{ color: '#666' }}>RSI(14):</span>
                <span>{item.RSI ? item.RSI.toFixed(2) : 'N/A'}</span>
              </>
            )}
            
            {indicators.includes('MACD') && (
              <>
                <span style={{ color: '#666' }}>MACD:</span>
                <span>{item.MACD ? item.MACD.toFixed(2) : 'N/A'}</span>
                
                <span style={{ color: '#666' }}>Signal:</span>
                <span>{item.signal ? item.signal.toFixed(2) : 'N/A'}</span>
              </>
            )}
          </div>
        </div>
      );
    }
    
    return null;
  };
  
  return (
    <div className="stock-candlestick-chart">
      <h3 style={{ margin: '0 0 16px 0' }}>{symbol} 주가 차트</h3>
      
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart
          data={data}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tickFormatter={(dateStr) => {
              const date = new Date(dateStr);
              return `${date.getMonth() + 1}/${date.getDate()}`;
            }}
          />
          <YAxis 
            domain={calculateYDomain()}
            tickFormatter={(value) => `${new Intl.NumberFormat('ko-KR', { maximumFractionDigits: 0 }).format(value)}`}
          />
          
          {showVolume && (
            <YAxis 
              yAxisId="volume"
              orientation="right"
              tickFormatter={(value) => `${(value / 1000000).toFixed(0)}M`}
              domain={['auto', 'auto']}
            />
          )}
          
          <Tooltip content={renderTooltip} />
          <Legend />
          
          {/* 고가-저가 선 */}
          <Line
            dataKey="high"
            stroke="transparent"
            dot={false}
            activeDot={false}
            legendType="none"
          />
          
          <Line
            dataKey="low"
            stroke="transparent"
            dot={false}
            activeDot={false}
            legendType="none"
          />
          
          {/* 시가-종가 바디 */}
          <Bar
            dataKey="open"
            name="시가/종가"
            shape={renderCandlestick}
            isAnimationActive={false}
          />
          
          {/* 볼륨 */}
          {showVolume && (
            <Bar
              dataKey="volume"
              yAxisId="volume"
              name="거래량"
              fill="#8884d8"
              opacity={0.3}
            />
          )}
          
          {/* 기술적 지표 라인 */}
          {indicators.includes('SMA') && (
            <>
              <Line
                type="monotone"
                dataKey="SMA20"
                name="SMA (20)"
                stroke="#ff7300"
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="SMA50"
                name="SMA (50)"
                stroke="#52c41a"
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="SMA200"
                name="SMA (200)"
                stroke="#722ed1"
                dot={false}
              />
            </>
          )}
          
          {indicators.includes('BB') && (
            <>
              <Line
                type="monotone"
                dataKey="upperBand"
                name="볼린저 상단"
                stroke="#f759ab"
                strokeDasharray="3 3"
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="lowerBand"
                name="볼린저 하단"
                stroke="#f759ab"
                strokeDasharray="3 3"
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="middleBand"
                name="볼린저 중간"
                stroke="#f759ab"
                dot={false}
              />
            </>
          )}
          
          {/* RSI용 참조 라인 */}
          {indicators.includes('RSI') && (
            <>
              <ReferenceLine y={70} stroke="#ff4d4f" strokeDasharray="3 3" />
              <ReferenceLine y={30} stroke="#52c41a" strokeDasharray="3 3" />
            </>
          )}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default StockCandlestickChart;