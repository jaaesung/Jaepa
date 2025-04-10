import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface SentimentData {
  symbol: string;
  positive: number;
  neutral: number;
  negative: number;
}

interface SentimentChartProps {
  data: SentimentData[];
  height?: number;
}

const SentimentChart: React.FC<SentimentChartProps> = ({
  data,
  height = 300,
}) => {
  const colors = {
    positive: "#52c41a", // 녹색
    neutral: "#faad14", // 노란색
    negative: "#ff4d4f", // 빨간색
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="symbol" />
        <YAxis />
        <Tooltip
          formatter={(value: any, name) => {
            return [`${(Number(value) * 100).toFixed(2)}%`, name];
          }}
        />
        <Legend />
        <Bar
          dataKey="positive"
          name="긍정"
          stackId="a"
          fill={colors.positive}
        />
        <Bar dataKey="neutral" name="중립" stackId="a" fill={colors.neutral} />
        <Bar
          dataKey="negative"
          name="부정"
          stackId="a"
          fill={colors.negative}
        />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default SentimentChart;
