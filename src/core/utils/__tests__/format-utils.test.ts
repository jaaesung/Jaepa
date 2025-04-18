/**
 * 포맷 유틸리티 테스트
 */

import { formatNumber, formatCurrency, formatPercentage, truncateText } from '../format-utils';

describe('Format Utils', () => {
  describe('formatNumber', () => {
    it('should format number correctly with default options', () => {
      expect(formatNumber(1234.56)).toBe('1,234.56');
      expect(formatNumber(1000)).toBe('1,000');
      expect(formatNumber(0)).toBe('0');
    });

    it('should format number with specified decimal places', () => {
      expect(formatNumber(1234.56789, { decimals: 2 })).toBe('1,234.57');
      expect(formatNumber(1234.5, { decimals: 3 })).toBe('1,234.500');
      expect(formatNumber(1234, { decimals: 0 })).toBe('1,234');
    });

    it('should handle thousand separator option', () => {
      expect(formatNumber(1234.56, { thousandSeparator: '.' })).toBe('1.234,56');
      expect(formatNumber(1234.56, { thousandSeparator: ' ' })).toBe('1 234,56');
      expect(formatNumber(1234.56, { thousandSeparator: '' })).toBe('1234,56');
    });

    it('should handle decimal separator option', () => {
      expect(formatNumber(1234.56, { decimalSeparator: ',' })).toBe('1.234,56');
      expect(formatNumber(1234.56, { decimalSeparator: ' ' })).toBe('1,234 56');
    });

    it('should handle combined options', () => {
      expect(
        formatNumber(1234.56789, {
          decimals: 3,
          thousandSeparator: '.',
          decimalSeparator: ',',
        })
      ).toBe('1.234,568');
    });

    it('should return empty string for invalid inputs', () => {
      expect(formatNumber(NaN)).toBe('');
      expect(formatNumber(null as any)).toBe('');
      expect(formatNumber(undefined as any)).toBe('');
    });
  });

  describe('formatCurrency', () => {
    it('should format currency correctly with default options', () => {
      expect(formatCurrency(1234.56)).toBe('$1,234.56');
      expect(formatCurrency(1000)).toBe('$1,000.00');
      expect(formatCurrency(0)).toBe('$0.00');
    });

    it('should format currency with specified currency symbol', () => {
      expect(formatCurrency(1234.56, { currencySymbol: '€' })).toBe('€1,234.56');
      expect(formatCurrency(1234.56, { currencySymbol: '₩' })).toBe('₩1,234.56');
    });

    it('should handle symbol position option', () => {
      expect(formatCurrency(1234.56, { symbolPosition: 'after' })).toBe('1,234.56$');
      expect(formatCurrency(1234.56, { currencySymbol: '€', symbolPosition: 'after' })).toBe(
        '1,234.56€'
      );
    });

    it('should handle combined options', () => {
      expect(
        formatCurrency(1234.56789, {
          decimals: 3,
          currencySymbol: '€',
          symbolPosition: 'after',
          thousandSeparator: '.',
          decimalSeparator: ',',
        })
      ).toBe('1.234,568€');
    });

    it('should return empty string for invalid inputs', () => {
      expect(formatCurrency(NaN)).toBe('');
      expect(formatCurrency(null as any)).toBe('');
      expect(formatCurrency(undefined as any)).toBe('');
    });
  });

  describe('formatPercentage', () => {
    it('should format percentage correctly with default options', () => {
      expect(formatPercentage(0.1234)).toBe('12.34%');
      expect(formatPercentage(1)).toBe('100.00%');
      expect(formatPercentage(0)).toBe('0.00%');
    });

    it('should format percentage with specified decimal places', () => {
      expect(formatPercentage(0.12345, { decimals: 3 })).toBe('12.345%');
      expect(formatPercentage(0.12, { decimals: 0 })).toBe('12%');
    });

    it('should handle multiplier option', () => {
      expect(formatPercentage(12.34, { multiplier: false })).toBe('12.34%');
      expect(formatPercentage(0.1234, { multiplier: true })).toBe('12.34%');
    });

    it('should handle combined options', () => {
      expect(
        formatPercentage(0.12345, {
          decimals: 3,
          multiplier: true,
          decimalSeparator: ',',
        })
      ).toBe('12,345%');
    });

    it('should return empty string for invalid inputs', () => {
      expect(formatPercentage(NaN)).toBe('');
      expect(formatPercentage(null as any)).toBe('');
      expect(formatPercentage(undefined as any)).toBe('');
    });
  });

  describe('truncateText', () => {
    it('should truncate text correctly with default options', () => {
      expect(truncateText('This is a long text that should be truncated', 20)).toBe(
        'This is a long text...'
      );
      expect(truncateText('Short text', 20)).toBe('Short text');
    });

    it('should handle custom suffix', () => {
      expect(truncateText('This is a long text that should be truncated', 20, ' [more]')).toBe(
        'This is a long text [more]'
      );
      expect(truncateText('This is a long text', 10, '..read more')).toBe('This is a..read more');
    });

    it('should handle word boundary option', () => {
      expect(truncateText('This is a long text that should be truncated', 20, '...', true)).toBe(
        'This is a long...'
      );
      expect(truncateText('ThisIsAVeryLongWordThatShouldBeTruncated', 10, '...', true)).toBe(
        'ThisIsAVer...'
      );
    });

    it('should return original text if shorter than max length', () => {
      expect(truncateText('Short text', 20)).toBe('Short text');
      expect(truncateText('', 20)).toBe('');
    });

    it('should handle invalid inputs', () => {
      expect(truncateText(null as any, 20)).toBe('');
      expect(truncateText(undefined as any, 20)).toBe('');
    });
  });
});
