/**
 * 로컬 스토리지 서비스 테스트
 */

import localStorageService from '../local-storage';

describe('Local Storage Service', () => {
  beforeEach(() => {
    // 각 테스트 전에 로컬 스토리지 초기화
    window.localStorage.clear();
    jest.clearAllMocks();
  });

  describe('setItem', () => {
    it('should store string value correctly', () => {
      const key = 'testKey';
      const value = 'testValue';
      
      localStorageService.setItem(key, value);
      
      expect(window.localStorage.getItem(key)).toBe(value);
    });

    it('should store and stringify object value correctly', () => {
      const key = 'testObject';
      const value = { name: 'Test', id: 123 };
      
      localStorageService.setItem(key, value);
      
      expect(window.localStorage.getItem(key)).toBe(JSON.stringify(value));
    });

    it('should store and stringify array value correctly', () => {
      const key = 'testArray';
      const value = [1, 2, 3];
      
      localStorageService.setItem(key, value);
      
      expect(window.localStorage.getItem(key)).toBe(JSON.stringify(value));
    });

    it('should handle null and undefined values', () => {
      localStorageService.setItem('nullKey', null);
      localStorageService.setItem('undefinedKey', undefined);
      
      expect(window.localStorage.getItem('nullKey')).toBe('null');
      expect(window.localStorage.getItem('undefinedKey')).toBe('undefined');
    });
  });

  describe('getItem', () => {
    it('should retrieve string value correctly', () => {
      const key = 'testKey';
      const value = 'testValue';
      
      window.localStorage.setItem(key, value);
      
      expect(localStorageService.getItem(key)).toBe(value);
    });

    it('should retrieve and parse object value correctly', () => {
      const key = 'testObject';
      const value = { name: 'Test', id: 123 };
      
      window.localStorage.setItem(key, JSON.stringify(value));
      
      expect(localStorageService.getItem(key, true)).toEqual(value);
    });

    it('should retrieve and parse array value correctly', () => {
      const key = 'testArray';
      const value = [1, 2, 3];
      
      window.localStorage.setItem(key, JSON.stringify(value));
      
      expect(localStorageService.getItem(key, true)).toEqual(value);
    });

    it('should return null for non-existent key', () => {
      expect(localStorageService.getItem('nonExistentKey')).toBeNull();
      expect(localStorageService.getItem('nonExistentKey', true)).toBeNull();
    });

    it('should handle invalid JSON when parsing is requested', () => {
      const key = 'invalidJson';
      const value = '{invalid json}';
      
      window.localStorage.setItem(key, value);
      
      expect(localStorageService.getItem(key, true)).toBe(value);
    });
  });

  describe('removeItem', () => {
    it('should remove item correctly', () => {
      const key = 'testKey';
      const value = 'testValue';
      
      window.localStorage.setItem(key, value);
      localStorageService.removeItem(key);
      
      expect(window.localStorage.getItem(key)).toBeNull();
    });

    it('should not throw error when removing non-existent key', () => {
      expect(() => {
        localStorageService.removeItem('nonExistentKey');
      }).not.toThrow();
    });
  });

  describe('clear', () => {
    it('should clear all items', () => {
      window.localStorage.setItem('key1', 'value1');
      window.localStorage.setItem('key2', 'value2');
      
      localStorageService.clear();
      
      expect(window.localStorage.length).toBe(0);
    });
  });

  describe('key', () => {
    it('should return key at specified index', () => {
      window.localStorage.setItem('key1', 'value1');
      window.localStorage.setItem('key2', 'value2');
      
      expect(localStorageService.key(0)).toBe('key1');
      expect(localStorageService.key(1)).toBe('key2');
    });

    it('should return null for out of range index', () => {
      window.localStorage.setItem('key1', 'value1');
      
      expect(localStorageService.key(1)).toBeNull();
      expect(localStorageService.key(-1)).toBeNull();
    });
  });

  describe('length', () => {
    it('should return correct number of items', () => {
      expect(localStorageService.length).toBe(0);
      
      window.localStorage.setItem('key1', 'value1');
      expect(localStorageService.length).toBe(1);
      
      window.localStorage.setItem('key2', 'value2');
      expect(localStorageService.length).toBe(2);
      
      window.localStorage.removeItem('key1');
      expect(localStorageService.length).toBe(1);
      
      window.localStorage.clear();
      expect(localStorageService.length).toBe(0);
    });
  });
});
