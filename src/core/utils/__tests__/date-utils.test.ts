/**
 * 날짜 유틸리티 테스트
 */

import { formatDate, parseDate, isValidDate, getDateDifference } from '../date-utils';

describe('Date Utils', () => {
  describe('formatDate', () => {
    it('should format date correctly with default format', () => {
      const date = new Date('2023-01-15T12:30:45');
      expect(formatDate(date)).toBe('2023-01-15');
    });

    it('should format date correctly with custom format', () => {
      const date = new Date('2023-01-15T12:30:45');
      expect(formatDate(date, 'yyyy/MM/dd')).toBe('2023/01/15');
      expect(formatDate(date, 'MM/dd/yyyy')).toBe('01/15/2023');
      expect(formatDate(date, 'dd MMM yyyy')).toBe('15 Jan 2023');
    });

    it('should handle string date input', () => {
      expect(formatDate('2023-01-15')).toBe('2023-01-15');
    });

    it('should return empty string for invalid date', () => {
      expect(formatDate('invalid-date')).toBe('');
      expect(formatDate(null as any)).toBe('');
      expect(formatDate(undefined as any)).toBe('');
    });
  });

  describe('parseDate', () => {
    it('should parse date string correctly', () => {
      const result = parseDate('2023-01-15');
      expect(result).toBeInstanceOf(Date);
      expect(result.getFullYear()).toBe(2023);
      expect(result.getMonth()).toBe(0); // January is 0
      expect(result.getDate()).toBe(15);
    });

    it('should return null for invalid date string', () => {
      expect(parseDate('invalid-date')).toBeNull();
      expect(parseDate('')).toBeNull();
    });

    it('should return the same date for Date object input', () => {
      const date = new Date('2023-01-15');
      const result = parseDate(date);
      expect(result).toBeInstanceOf(Date);
      expect(result.getTime()).toBe(date.getTime());
    });
  });

  describe('isValidDate', () => {
    it('should return true for valid dates', () => {
      expect(isValidDate(new Date())).toBe(true);
      expect(isValidDate('2023-01-15')).toBe(true);
    });

    it('should return false for invalid dates', () => {
      expect(isValidDate('invalid-date')).toBe(false);
      expect(isValidDate('')).toBe(false);
      expect(isValidDate(null as any)).toBe(false);
      expect(isValidDate(undefined as any)).toBe(false);
      expect(isValidDate(new Date('invalid'))).toBe(false);
    });
  });

  describe('getDateDifference', () => {
    it('should calculate difference in days correctly', () => {
      const date1 = new Date('2023-01-15');
      const date2 = new Date('2023-01-20');
      expect(getDateDifference(date1, date2, 'days')).toBe(5);
      expect(getDateDifference(date2, date1, 'days')).toBe(-5);
    });

    it('should calculate difference in months correctly', () => {
      const date1 = new Date('2023-01-15');
      const date2 = new Date('2023-03-15');
      expect(getDateDifference(date1, date2, 'months')).toBe(2);
    });

    it('should calculate difference in years correctly', () => {
      const date1 = new Date('2021-01-15');
      const date2 = new Date('2023-01-15');
      expect(getDateDifference(date1, date2, 'years')).toBe(2);
    });

    it('should handle string date inputs', () => {
      expect(getDateDifference('2023-01-15', '2023-01-20', 'days')).toBe(5);
    });

    it('should return 0 for invalid dates', () => {
      expect(getDateDifference('invalid', '2023-01-20', 'days')).toBe(0);
      expect(getDateDifference('2023-01-15', 'invalid', 'days')).toBe(0);
    });
  });
});
