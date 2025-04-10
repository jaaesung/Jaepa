import React from 'react';
import {
  ComposedChart,
  Line,
  Area,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface TechnicalIndicatorChartProps {
  data: any[];
  indicators: string[];
  height?: number;
  symbol: string;
}

interface IndicatorConfig {
  type: 'line' | 'area' | 'bar';
  color: string;
  dataKey: string;
  name: string;
  yAxisId?: string;
  strokeDasharray?: string;
  opacity?: number;
  fill?: string;
  stroke?: string;
  dot?: boolean | object;
}

const TechnicalIndicatorChart: React.FC<TechnicalIndicatorChartProps> = ({
  data,
  indicators,
  height = 400,
  symbol
}) => {
  // 지표별 차트 설정 정의
  const indicatorConfigs: Record<string, IndicatorConfig> = {
    'price': {
      type: 'line',
      color: '#1890ff',
      dataKey: 'price',
      name: '주가',
      yAxisId: 'price',
      dot: false
    },
    'volume': {
      type: 'bar',
      color: '#8884d8',
      dataKey: 'volume',
      name: '거래량',
      yAxisId: 'volume',
      opacity: 0.5
    },
    'SMA20': {
      type: 'line',
      color: '#ff7300',
      dataKey: 'SMA20',
      name: 'SMA (20)',
      yAxisId: 'price',
      dot: false
    },
    'SMA50': {
      type: 'line',
      color: '#52c41a',
      dataKey: 'SMA50',
      name: 'SMA (50)',
      yAxisId: 'price',
      dot: false
    },
    'SMA200': {
      type: 'line',
      color: '#722ed1',
      dataKey: 'SMA200',
      name: 'SMA (200)',
      yAxisId: 'price',
      dot: false
    },
    'EMA20': {
      type: 'line',
      color: '#faad14',
      dataKey: 'EMA20',
      name: 'EMA (20)',
      yAxisId: 'price',
      dot: false,
      strokeDasharray: '5 5'
    },
    'upperBand': {
      type: 'line',
      color: '#f759ab',
      dataKey: 'upperBand',
      name: '볼린저 상단',
      yAxisId: 'price',
      strokeDasharray: '3 3',
      dot: false
    },
    'lowerBand': {
      type: 'line',
      color: '#f759ab',
      dataKey: 'lowerBand',
      name: '볼린저 하단',
      yAxisId: 'price',
      strokeDasharray: '3 3',
      dot: false
    },
    'middleBand': {
      type: 'line',
      color: '#f759ab',
      dataKey: 'middleBand',
      name: '볼린저 중앙',
      yAxisId: 'price',
      dot: false
    },
    'RSI': {
      type: 'line',
      color: '#13c2c2',
      dataKey: 'RSI',
      name: 'RSI (14)',
      yAxisId: 'oscillator',
      dot: false
    },
    'MACD': {
      type: 'line',
      color: '#1890ff',
      dataKey: 'MACD',
      name: 'MACD',
      yAxisId: 'oscillator',
      dot: false
    },
    'signal': {
      type: 'line',
      color: '#fa8c16',
      dataKey: 'signal',
      name: 'MACD 시그널',
      yAxisId: 'oscillator',
      dot: false
    },
    'histogram': {
      type: 'bar',
      color: '#000000',
      dataKey: 'histogram',
      name: 'MACD 히스토그램',
      yAxisId: 'oscillator',
      opacity: 0.5
    }
  };

  // 분석 창에 표시할 지표 필터링
  const activeIndicators = ['price'];
  
  // 볼륨을 표시할지 여부
  const showVolume = indicators.includes('volume');
  if (showVolume) {
    activeIndicators.push('volume');
  }
  
  // SMA 표시
  if (indicators.includes('SMA')) {
    activeIndicators.push('SMA20', 'SMA50', 'SMA200');
  }
  
  // EMA 표시
  if (indicators.includes('EMA')) {
    activeIndicators.push('EMA20');
  }
  
  // 볼린저 밴드 표시
  if (indicators.includes('BB')) {
    activeIndicators.push('upperBand', 'middleBand', 'lowerBand');
  }
  
  // RSI 표시
  const showRSI = indicators.includes('RSI');
  if (showRSI) {
    activeIndicators.push('RSI');
  }
  
  // MACD 표시
  const showMACD = indicators.includes('MACD');
  if (showMACD) {
    activeIndicators.push('MACD', 'signal', 'histogram');
  }
  
  // 액티브 지표에 대한 설정 가져오기
  const activeConfigs = activeIndicators
    .filter(id => indicatorConfigs[id])
    .map(id => indicatorConfigs[id]);
  
  // Y축 구성 결정
  const yAxes = [];
  
  // 가격 Y축은 항상 포함
  yAxes.push(
    <YAxis 
      key="price"
      yAxisId="price"
      domain={['auto', 'auto']}
      orientation="left"
      tick={{ fill: '#1890ff' }}
      tickFormatter={(value) => `${new Intl.NumberFormat('ko-KR', { maximumFractionDigits: 0 }).format(value)}`}
    />
  );
  
  // 오실레이터 Y축 (RSI 또는 MACD가 표시되는 경우)
  if (showRSI || showMACD) {
    yAxes.push(
      <YAxis 
        key="oscillator"
        yAxisId="oscillator"
        domain={showRSI ? [0, 100] : ['auto', 'auto']}
        orientation="right"
        tick={{ fill: '#13c2c2' }}
      />
    );
  }
  
  // 볼륨 Y축
  if (showVolume) {
    yAxes.push(
      <YAxis 
        key="volume"
        yAxisId="volume"
        domain={['auto', 'auto']}
        orientation="right"
        axisLine={false}
        tickLine={false}
        tick={false}
        tickFormatter={(value) => `${(value / 1000000).toFixed(0)}M`}
      />
    );
  }
  
  // 툴팁 커스터마이징
  const renderTooltip = (props: any) => {
    const { active, payload, label } = props;
    
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip" style={{ 
          backgroundColor: '#fff', 
          padding: '10px', 
          border: '1px solid #ccc',
          borderRadius: '4px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <p className="date" style={{ margin: '0 0 8px 0', fontWeight: 'bold' }}>
            {new Date(label).toLocaleDateString('ko-KR')}
          </p>
          {payload.map((entry: any, index: number) => {
            // 부모 컴포넌트에서 받은 설정에 따라 표시할지 여부 결정
            const config = activeConfigs.find(c => c.dataKey === entry.dataKey);
            if (!config) return null;
            
            return (
              <p key={`item-${index}`} style={{ 
                margin: '4px 0',
                color: entry.color 
              }}>
                <span style={{ marginRight: '8px', fontWeight: 500 }}>{entry.name}:</span>
                {entry.dataKey === 'volume' 
                  ? `${(entry.value / 1000000).toFixed(2)}M`
                  : entry.value
                }
              </p>
            );
          })}
        </div>
      );
    }
    
    return null;
  };
  
  // Legend 커스터마이징
  const renderLegend = (props: any) => {
    const { payload } = props;
    
    return (
      <div className="custom-legend" style={{ 
        display: 'flex', 
        flexWrap: 'wrap',
        justifyContent: 'center',
        gap: '12px',
        padding: '8px 0'
      }}>
        {payload.map((entry: any, index: number) => {
          // 부모 컴포넌트에서 받은 설정에 따라 표시할지 여부 결정
          const config = activeConfigs.find(c => c.dataKey === entry.dataKey);
          if (!config) return null;
          
          return (
            <div key={`item-${index}`} style={{ 
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}>
              <div style={{ 
                width: '12px',
                height: '12px',
                backgroundColor: entry.color,
                borderRadius: config.type === 'line' ? '0' : '50%'
              }} />
              <span style={{ fontSize: '14px', color: '#666' }}>{entry.value}</span>
            </div>
          );
        })}
      </div>
    );
  };
  
  return (
    <div className="technical-indicator-chart">
      <h3 style={{ margin: '0 0 16px 0' }}>{symbol} 기술적 분석 차트</h3>
      
      <ResponsiveContainer width="100%" height={height}>
        <ComposedChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tickFormatter={(dateStr) => {
              const date = new Date(dateStr);
              return `${date.getMonth() + 1}/${date.getDate()}`;
            }}
          />
          
          {yAxes}
          
          <Tooltip content={renderTooltip} />
          <Legend content={renderLegend} />
          
          {/* 볼륨 표시 (다른 지표보다 먼저 렌더링하여 뒤에 나타나도록) */}
          {showVolume && (
            <Bar
              dataKey="volume"
              name="거래량"
              yAxisId="volume"
              fill="#8884d8"
              opacity={0.3}
            />
          )}
          
          {/* 히스토그램 표시 (MACD 히스토그램) */}
          {showMACD && (
            <Bar
              dataKey="histogram"
              name="MACD 히스토그램"
              yAxisId="oscillator"
              fill={(data) => (data.histogram >= 0 ? '#f5222d' : '#52c41a')}
              opacity={0.6}
            />
          )}
          
          {/* 볼린저 밴드 영역 표시 */}
          {indicators.includes('BB') && (
            <Area
              type="monotone"
              dataKey="middleBand"
              stroke="none"
              fill="#f759ab"
              fillOpacity={0.1}
              yAxisId="price"
            />
          )}
          
          {/* 라인 차트들 표시 */}
          {activeConfigs
            .filter(config => config.type === 'line')
            .map((config, index) => (
              <Line
                key={config.dataKey}
                type="monotone"
                dataKey={config.dataKey}
                name={config.name}
                stroke={config.color}
                strokeDasharray={config.strokeDasharray}
                yAxisId={config.yAxisId || 'price'}
                dot={config.dot || false}
                activeDot={{ r: 6, stroke: config.color, strokeWidth: 2 }}
              />
            ))
          }
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TechnicalIndicatorChart;