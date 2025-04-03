/**
 * RGB 색상을 HEX 형식으로 변환
 * @param {number} r - Red (0-255)
 * @param {number} g - Green (0-255)
 * @param {number} b - Blue (0-255)
 * @returns {string} HEX 색상 코드
 */
export const rgbToHex = (r, g, b) => {
  return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
};

/**
 * HEX 색상을 RGB 형식으로 변환
 * @param {string} hex - HEX 색상 코드
 * @returns {Object} RGB 색상 객체 {r, g, b}
 */
export const hexToRgb = (hex) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : null;
};

/**
 * 색상 밝기 계산 (0-255)
 * @param {string} color - HEX 색상 코드
 * @returns {number} 밝기 값
 */
export const calculateBrightness = (color) => {
  const rgb = hexToRgb(color);
  if (!rgb) return 0;
  return (rgb.r * 299 + rgb.g * 587 + rgb.b * 114) / 1000;
};

/**
 * 주어진 배경색에 적합한 텍스트 색상 반환 (검정 또는 흰색)
 * @param {string} bgColor - 배경 HEX 색상 코드
 * @returns {string} 텍스트 색상 코드 (#000000 또는 #FFFFFF)
 */
export const getContrastColor = (bgColor) => {
  const brightness = calculateBrightness(bgColor);
  return brightness > 128 ? '#000000' : '#FFFFFF';
};

/**
 * HSL의 Hue 값을 RGB 요소로 변환하는 보조 함수
 * @param {number} p
 * @param {number} q
 * @param {number} t
 * @returns {number} RGB 요소 값 (0-1)
 */
const hueToRgb = (p, q, t) => {
  if (t < 0) t += 1;
  if (t > 1) t -= 1;
  if (t < 1/6) return p + (q - p) * 6 * t;
  if (t < 1/2) return q;
  if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
  return p;
};

/**
 * 값의 범위에 따라 색상 그라데이션 생성
 * @param {number} value - 값
 * @param {number} min - 최소값
 * @param {number} max - 최대값
 * @param {Array} colors - 색상 배열 (최소값에서 최대값까지)
 * @returns {string} 색상 코드
 */
export const getGradientColor = (value, min, max, colors) => {
  if (value <= min) return colors[0];
  if (value >= max) return colors[colors.length - 1];
  
  const range = max - min;
  const position = (value - min) / range;
  const index = position * (colors.length - 1);
  
  const lowerIndex = Math.floor(index);
  const upperIndex = Math.ceil(index);
  
  if (lowerIndex === upperIndex) return colors[lowerIndex];
  
  const weight = index - lowerIndex;
  const lowerColor = hexToRgb(colors[lowerIndex]);
  const upperColor = hexToRgb(colors[upperIndex]);
  
  const r = Math.round(lowerColor.r * (1 - weight) + upperColor.r * weight);
  const g = Math.round(lowerColor.g * (1 - weight) + upperColor.g * weight);
  const b = Math.round(lowerColor.b * (1 - weight) + upperColor.b * weight);
  
  return rgbToHex(r, g, b);
};

/**
 * 차트용 색상 팔레트 생성
 * @param {number} count - 필요한 색상 수
 * @param {boolean} pastel - 파스텔 색상 여부
 * @returns {Array} 색상 코드 배열
 */
export const generateChartColors = (count, pastel = false) => {
  const baseColors = pastel
    ? [
        '#ffb3ba', // 연한 빨강
        '#ffdfba', // 연한 주황
        '#ffffba', // 연한 노랑
        '#baffc9', // 연한 녹색
        '#bae1ff', // 연한 파랑
        '#e2baff', // 연한 보라
        '#f4baff', // 연한 핑크
      ]
    : [
        '#1f77b4', // 파랑
        '#ff7f0e', // 주황
        '#2ca02c', // 녹색
        '#d62728', // 빨강
        '#9467bd', // 보라
        '#8c564b', // 갈색
        '#e377c2', // 핑크
        '#7f7f7f', // 회색
        '#bcbd22', // 연두
        '#17becf', // 청록
      ];
  
  if (count <= baseColors.length) {
    return baseColors.slice(0, count);
  }
  
  const result = [...baseColors];
  for (let i = baseColors.length; i < count; i++) {
    const hue = (i * 137.5) % 360; // 황금비(1.618)를 이용한 색상 분포
    const saturation = pastel ? 0.5 : 0.8;
    const lightness = pastel ? 0.8 : 0.6;
    
    // HSL to RGB 변환
    const h = hue / 360;
    const s = saturation;
    const l = lightness;
    const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
    const p = 2 * l - q;
    
    const rt = h + 1/3;
    const gt = h;
    const bt = h - 1/3;
    
    const r = Math.round(hueToRgb(p, q, rt < 0 ? rt + 1 : rt > 1 ? rt - 1 : rt) * 255);
    const g = Math.round(hueToRgb(p, q, gt < 0 ? gt + 1 : gt > 1 ? gt - 1 : gt) * 255);
    const b = Math.round(hueToRgb(p, q, bt < 0 ? bt + 1 : bt > 1 ? bt - 1 : bt) * 255);
    
    result.push(rgbToHex(r, g, b));
  }
  
  return result;
};

/**
 * 감성 점수에 따른 색상 코드 반환 (적색-황색-녹색 그라데이션)
 * @param {number} score - 감성 점수 (-1.0 ~ 1.0)
 * @returns {string} 색상 코드
 */
export const getSentimentColor = (score) => {
  const normalizedScore = (score + 1) / 2; // 0 ~ 1 범위로 정규화
  return getGradientColor(
    normalizedScore,
    0,
    1,
    ['#ff4d4f', '#faad14', '#52c41a'] // 적색, 황색, 녹색
  );
};

/**
 * 주식 변동에 따른 색상 코드 반환
 * @param {number} change - 변동률
 * @returns {string} 색상 코드
 */
export const getStockChangeColor = (change) => {
  if (change > 0) return '#f5222d'; // 상승 (적색)
  if (change < 0) return '#52c41a'; // 하락 (녹색)
  return '#bfbfbf'; // 변동 없음 (회색)
};