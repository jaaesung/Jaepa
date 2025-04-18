/**
 * 로컬 스토리지 서비스 모듈
 * 
 * 브라우저의 localStorage를 사용하여 데이터를 영구적으로 저장하는 기능을 제공합니다.
 */

/**
 * 로컬 스토리지 서비스 클래스
 */
class LocalStorageService {
  /**
   * 데이터 저장
   * 
   * @param key 저장할 키
   * @param value 저장할 값
   */
  set<T>(key: string, value: T): void {
    try {
      const serializedValue = JSON.stringify(value);
      localStorage.setItem(key, serializedValue);
    } catch (error) {
      console.error('LocalStorage 저장 오류:', error);
    }
  }

  /**
   * 데이터 조회
   * 
   * @param key 조회할 키
   * @returns 저장된 값 또는 null
   */
  get<T>(key: string): T | null {
    try {
      const serializedValue = localStorage.getItem(key);
      if (serializedValue === null) {
        return null;
      }
      return JSON.parse(serializedValue) as T;
    } catch (error) {
      console.error('LocalStorage 조회 오류:', error);
      return null;
    }
  }

  /**
   * 데이터 삭제
   * 
   * @param key 삭제할 키
   */
  remove(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('LocalStorage 삭제 오류:', error);
    }
  }

  /**
   * 모든 데이터 삭제
   */
  clear(): void {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('LocalStorage 초기화 오류:', error);
    }
  }

  /**
   * 키 존재 여부 확인
   * 
   * @param key 확인할 키
   * @returns 키 존재 여부
   */
  has(key: string): boolean {
    try {
      return localStorage.getItem(key) !== null;
    } catch (error) {
      console.error('LocalStorage 확인 오류:', error);
      return false;
    }
  }
}

export const localStorageService = new LocalStorageService();
export default localStorageService;
