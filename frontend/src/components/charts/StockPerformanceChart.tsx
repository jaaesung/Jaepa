import React, { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Brush
} from 'recharts';
import { generateChartColors } from '../../utils/colorUtils';

interface StockData {
  date: string;
  [key: string]: number | string; // 주식 심볼에 따른 가격 데이터
}

interface StockPerformanceChartProps {
  data: StockData[];
  symbols: string[];
  height?: number;
  showBrush?: boolean;
}

const StockPerformanceChart: React.FC<StockPerformanceChartProps> = ({ 
  data, 
  symbols, 
  height = 300,
  showBrush = true
}) => {
  const colors = generateChartColors(symbols.length);
  
  // 툴팁에 날짜를 포맷팅하는 함수
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // 가격 포맷팅
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price);
  };

  // 커스텀 툴팁
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip" style={{ 
          backgroundColor: '#fff', 
          padding: '10px', 
          border: '1px solid #ccc',
          borderRadius: '4px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <p className="label" style={{ fontWeight: 'bold', marginBottom: '8px' }}>{formatDate(label)}</p>
          {payload.map((entry: any, index: number) => (
            <p key={`item-${index}`} style={{ color: entry.color, margin: '4px 0' }}>
              {entry.name}: {formatPrice(entry.value)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart
        data={data}
        margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="date"
          tickFormatter={(dateStr) => {
            const date = new Date(dateStr);
            return `${date.getMonth() + 1}/${date.getDate()}`;
          }}
          minTickGap={30}
        />
        <YAxis 
          domain={['auto', 'auto']}
          tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`}
        />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        {symbols.map((symbol, index) => (
          <Line
            key={symbol}
            type="monotone"
            dataKey={symbol}
            stroke={colors[index]}
            strokeWidth={2}
            dot={{ r: 2 }}
            activeDot={{ r: 6 }}
            name={symbol}
          />
        ))}
        {showBrush && <Brush dataKey="date" height={30} stroke="#8884d8" />}
      </LineChart>
    </ResponsiveContainer>
  );
};

export default StockPerformanceChart;