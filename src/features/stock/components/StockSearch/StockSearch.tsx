/**
 * 주식 검색 컴포넌트
 *
 * 주식 검색 기능을 제공하는 컴포넌트입니다.
 */

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStock } from '../../hooks/useStock';
import { useDebounce } from '../../../../core/hooks';
import './StockSearch.css';

interface StockSearchProps {
  onSelect?: (symbol: string) => void;
  placeholder?: string;
  autoFocus?: boolean;
}

/**
 * 주식 검색 컴포넌트
 */
const StockSearch: React.FC<StockSearchProps> = ({
  onSelect,
  placeholder = '주식 심볼 또는 회사명 검색...',
  autoFocus = false,
}) => {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const debouncedQuery = useDebounce(query, 300);
  const { searchStock, searchResults, searchLoading, clearStockSearchResults } = useStock();
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  // 검색어 변경 시 검색 실행
  useEffect(() => {
    if (debouncedQuery.trim().length >= 2) {
      searchStock(debouncedQuery);
      setIsOpen(true);
    } else {
      clearStockSearchResults();
      setIsOpen(false);
    }
  }, [debouncedQuery, searchStock, clearStockSearchResults]);

  // 검색어 변경 핸들러
  const handleQueryChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  // 검색 결과 선택 핸들러
  const handleSelect = (symbol: string) => {
    setQuery('');
    setIsOpen(false);
    clearStockSearchResults();

    if (onSelect) {
      onSelect(symbol);
    } else {
      navigate(`/stock-analysis/${symbol}`);
    }
  };

  // 검색 폼 제출 핸들러
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (searchResults.length > 0) {
      handleSelect(searchResults[0].symbol);
    }
  };

  // 외부 클릭 감지 핸들러
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        resultsRef.current &&
        !resultsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="stock-search">
      <form className="stock-search-form" onSubmit={handleSubmit}>
        <input
          ref={inputRef}
          type="text"
          className="stock-search-input"
          placeholder={placeholder}
          value={query}
          onChange={handleQueryChange}
          onFocus={() => query.trim().length >= 2 && setIsOpen(true)}
          autoFocus={autoFocus}
        />
        <button type="submit" className="stock-search-button">
          <span className="stock-search-icon">🔍</span>
        </button>
      </form>

      {isOpen && (
        <div ref={resultsRef} className="stock-search-results">
          {searchLoading ? (
            <div className="stock-search-loading">
              <div className="spinner-small"></div>
              <p>검색 중...</p>
            </div>
          ) : searchResults.length === 0 ? (
            <div className="stock-search-empty">
              <p>검색 결과가 없습니다.</p>
            </div>
          ) : (
            <ul className="stock-search-list">
              {searchResults.map((result: { symbol: string; name: string; exchange: string }) => (
                <li key={result.symbol} className="stock-search-item">
                  <button
                    className="stock-search-item-button"
                    onClick={() => handleSelect(result.symbol)}
                  >
                    <div className="stock-search-item-symbol">{result.symbol}</div>
                    <div className="stock-search-item-name">{result.name}</div>
                    <div className="stock-search-item-exchange">{result.exchange}</div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default StockSearch;
