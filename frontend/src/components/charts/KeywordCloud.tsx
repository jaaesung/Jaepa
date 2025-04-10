import React, { useMemo } from "react";
import { getSentimentColor } from "../../utils/colorUtils";

interface KeywordData {
  text: string;
  value: number;
  sentiment: number; // -1.0 ~ 1.0 범위의 감성 점수
}

interface KeywordCloudProps {
  data: KeywordData[];
  width?: number;
  height?: number;
  maxFontSize?: number;
  minFontSize?: number;
}

const KeywordCloud: React.FC<KeywordCloudProps> = ({
  data,
  width = 500,
  height = 300,
  maxFontSize = 48,
  minFontSize = 14,
}) => {
  // 값의 범위를 계산하여 폰트 크기 스케일링을 위한 함수
  const calculateFontSize = (value: number, min: number, max: number) => {
    if (max === min) return minFontSize;
    const normalized = (value - min) / (max - min);
    return minFontSize + normalized * (maxFontSize - minFontSize);
  };

  // 데이터에서 최대값과 최소값 계산
  const maxValue = useMemo(
    () => Math.max(...data.map((item) => item.value)),
    [data]
  );
  const minValue = useMemo(
    () => Math.min(...data.map((item) => item.value)),
    [data]
  );

  // 키워드 위치 계산 (간단한 배치 알고리즘)
  const calculatePositions = useMemo(() => {
    if (!data || data.length === 0) return [];

    // 값 범위 계산
    const values = data.map((item) => item.value);
    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);

    // 간단한 랜덤 배치 (실제 워드 클라우드 알고리즘은 더 복잡함)
    const positionedData = data.map((item, index) => {
      const fontSize = calculateFontSize(item.value, minValue, maxValue);

      // 센터에서 시작하는 나선형 배치 시도 (매우 간단한 알고리즘)
      const angle = index * 0.3; // 나선 간격
      const radius = 10 + index * 4; // 나선 반경
      const x = width / 2 + Math.cos(angle) * radius;
      const y = height / 2 + Math.sin(angle) * radius;

      // 색상 계산
      const color = getSentimentColor(item.sentiment);

      return {
        ...item,
        fontSize,
        x: Math.max(0, Math.min(width - fontSize * 4, x)),
        y: Math.max(0, Math.min(height - fontSize, y)),
        color,
      };
    });

    return positionedData;
  }, [data, width, height, maxFontSize, minFontSize]);

  // 키워드가 없는 경우 표시할 메시지
  if (!data || data.length === 0) {
    return (
      <div
        style={{
          width,
          height,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          border: "1px dashed #ccc",
          borderRadius: "4px",
          color: "#999",
        }}
      >
        키워드 데이터가 없습니다.
      </div>
    );
  }

  return (
    <div style={{ width, height, position: "relative", overflow: "hidden" }}>
      {calculatePositions.map((item, index) => (
        <div
          key={index}
          style={{
            position: "absolute",
            left: item.x,
            top: item.y,
            fontSize: `${item.fontSize}px`,
            color: item.color,
            fontWeight:
              item.value > (maxValue + minValue) / 2 ? "bold" : "normal",
            cursor: "pointer",
            transition: "transform 0.2s",
            userSelect: "none",
            whiteSpace: "nowrap",
            transform: "translate(-50%, -50%)",
          }}
          title={`${item.text}: ${item.value}`}
        >
          {item.text}
        </div>
      ))}
    </div>
  );
};

export default KeywordCloud;
