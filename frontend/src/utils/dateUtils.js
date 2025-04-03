/**
 * 날짜를 yyyy-mm-dd 형식으로 포맷팅
 * @param {Date} date - 날짜 객체
 * @returns {string} 포맷팅된 날짜 문자열
 */
export const formatDate = (date) => {
  const d = new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

/**
 * yyyy-mm-dd 형식의 문자열을 Date 객체로 변환
 * @param {string} dateStr - 날짜 문자열
 * @returns {Date} 날짜 객체
 */
export const parseDate = (dateStr) => {
  const [year, month, day] = dateStr.split('-').map(Number);
  return new Date(year, month - 1, day);
};

/**
 * 현재 날짜로부터 n일 전의 날짜를 반환
 * @param {number} days - 이전 일수
 * @returns {Date} 이전 날짜 객체
 */
export const getDaysAgo = (days) => {
  const date = new Date();
  date.setDate(date.getDate() - days);
  return date;
};

/**
 * 상대적 시간 표시 (예: '3시간 전', '2일 전')
 * @param {Date|string} date - 날짜 객체 또는 문자열
 * @returns {string} 상대적 시간 문자열
 */
export const getRelativeTime = (date) => {
  const d = date instanceof Date ? date : new Date(date);
  const now = new Date();
  const diff = Math.floor((now - d) / 1000); // 초 단위 차이
  
  if (diff < 60) return '방금 전';
  if (diff < 3600) return `${Math.floor(diff / 60)}분 전`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}시간 전`;
  if (diff < 2592000) return `${Math.floor(diff / 86400)}일 전`;
  if (diff < 31536000) return `${Math.floor(diff / 2592000)}개월 전`;
  return `${Math.floor(diff / 31536000)}년 전`;
};

/**
 * 날짜 범위 생성 (시작일부터 종료일까지의 모든 날짜)
 * @param {Date} startDate - 시작 날짜
 * @param {Date} endDate - 종료 날짜
 * @returns {Array<Date>} 날짜 범위 배열
 */
export const getDateRange = (startDate, endDate) => {
  const dates = [];
  const currentDate = new Date(startDate);
  
  while (currentDate <= endDate) {
    dates.push(new Date(currentDate));
    currentDate.setDate(currentDate.getDate() + 1);
  }
  
  return dates;
};

/**
 * 날짜를 사용자 친화적인 형식으로 포맷팅 (예: '2023년 1월 1일')
 * @param {Date|string} date - 날짜 객체 또는 문자열
 * @returns {string} 포맷팅된 날짜 문자열
 */
export const formatDateFriendly = (date) => {
  const d = date instanceof Date ? date : new Date(date);
  return d.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

/**
 * 날짜와 시간을 포맷팅 (예: '2023-01-01 14:30:45')
 * @param {Date|string} date - 날짜 객체 또는 문자열
 * @returns {string} 포맷팅된 날짜 및 시간 문자열
 */
export const formatDateTime = (date) => {
  const d = date instanceof Date ? date : new Date(date);
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');
  
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
};