/**
 * 로컬 스토리지 서비스
 * 
 * 브라우저의 로컬 스토리지에 데이터를 저장하고 가져오는 기능을 제공합니다.
 */

/**
 * 로컬 스토리지에 데이터 저장
 * @param key 저장할 키
 * @param value 저장할 값
 */
const set = <T>(key: string, value: T): void => {
  try {
    const serializedValue = JSON.stringify(value);
    localStorage.setItem(key, serializedValue);
  } catch (error) {
    console.error('로컬 스토리지에 데이터를 저장하는 중 오류 발생:', error);
  }
};

/**
 * 로컬 스토리지에서 데이터 가져오기
 * @param key 가져올 키
 * @param defaultValue 기본값 (선택 사항)
 * @returns 저장된 값 또는 기본값
 */
const get = <T = any>(key: string, defaultValue: T | null = null): T | null => {
  try {
    const serializedValue = localStorage.getItem(key);
    if (serializedValue === null) {
      return defaultValue;
    }
    return JSON.parse(serializedValue) as T;
  } catch (error) {
    console.error('로컬 스토리지에서 데이터를 가져오는 중 오류 발생:', error);
    return defaultValue;
  }
};

/**
 * 로컬 스토리지에서 데이터 삭제
 * @param key 삭제할 키
 */
const remove = (key: string): void => {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error('로컬 스토리지에서 데이터를 삭제하는 중 오류 발생:', error);
  }
};

/**
 * 로컬 스토리지 비우기
 */
const clear = (): void => {
  try {
    localStorage.clear();
  } catch (error) {
    console.error('로컬 스토리지를 비우는 중 오류 발생:', error);
  }
};

// 기존 메서드와의 호환성을 위한 별칭
const setItem = set;
const getItem = get;
const removeItem = remove;

const localStorageService = {
  set,
  get,
  remove,
  clear,
  // 기존 메서드와의 호환성을 위한 별칭
  setItem,
  getItem,
  removeItem,
};

export default localStorageService;
