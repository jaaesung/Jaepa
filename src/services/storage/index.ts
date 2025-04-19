/**
 * 로컬 스토리지 서비스
 */

// 로컬 스토리지에 항목 저장
export const localStorageService = {
  /**
   * 로컬 스토리지에 항목 저장
   */
  setItem: (key: string, value: any): void => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('로컬 스토리지 저장 오류:', error);
    }
  },

  /**
   * 로컬 스토리지에서 항목 가져오기
   */
  getItem: <T = any>(key: string, defaultValue: T | null = null): T | null => {
    try {
      const item = localStorage.getItem(key);
      if (item === null) return defaultValue;
      return JSON.parse(item);
    } catch (error) {
      console.error('로컬 스토리지 조회 오류:', error);
      return defaultValue;
    }
  },

  /**
   * 로컬 스토리지에서 항목 삭제
   */
  removeItem: (key: string): void => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('로컬 스토리지 삭제 오류:', error);
    }
  },

  /**
   * 로컬 스토리지 초기화
   */
  clear: (): void => {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('로컬 스토리지 초기화 오류:', error);
    }
  }
};
