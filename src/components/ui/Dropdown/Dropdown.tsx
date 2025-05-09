/**
 * 드롭다운 컴포넌트
 *
 * 사용자가 여러 옵션 중 하나를 선택할 수 있는 드롭다운 컴포넌트를 제공합니다.
 */

import React, { useState, useRef, useEffect } from 'react';
import './Dropdown.css';

export interface DropdownOption {
  /**
   * 옵션 값
   */
  value: string;

  /**
   * 옵션 라벨
   */
  label: string;

  /**
   * 옵션 비활성화 여부
   */
  disabled?: boolean;

  /**
   * 옵션 아이콘
   */
  icon?: React.ReactNode;
}

export interface DropdownProps {
  /**
   * 옵션 목록
   */
  options: DropdownOption[];

  /**
   * 선택된 값
   */
  value?: string;

  /**
   * 값 변경 핸들러
   */
  onChange?: (value: string) => void;

  /**
   * 플레이스홀더
   */
  placeholder?: string;

  /**
   * 라벨
   */
  label?: string;

  /**
   * 비활성화 여부
   */
  disabled?: boolean;

  /**
   * 에러 메시지
   */
  error?: string;

  /**
   * 전체 너비 적용 여부
   */
  fullWidth?: boolean;

  /**
   * 추가 클래스명
   */
  className?: string;

  /**
   * 필수 여부
   */
  required?: boolean;

  /**
   * 검색 가능 여부
   */
  searchable?: boolean;

  /**
   * 검색 플레이스홀더
   */
  searchPlaceholder?: string;

  /**
   * 스크린 리더에서 읽을 아리아 레이블
   */
  ariaLabel?: string;

  /**
   * 스크린 리더에서 읽을 아리아 설명
   */
  ariaDescription?: string;
}

/**
 * 드롭다운 컴포넌트
 */
const Dropdown: React.FC<DropdownProps> = ({
  options,
  value,
  onChange,
  placeholder = '선택하세요',
  label,
  disabled = false,
  error,
  fullWidth = false,
  className = '',
  required = false,
  searchable = false,
  searchPlaceholder = '검색...',
  ariaLabel,
  ariaDescription,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const optionsRef = useRef<HTMLLIElement[]>([]);

  // 선택된 옵션 찾기
  const selectedOption = options.find(option => option.value === value);

  // 드롭다운 토글
  const toggleDropdown = () => {
    if (!disabled) {
      setIsOpen(!isOpen);
      if (!isOpen) {
        setHighlightedIndex(-1);
      }
    }
  };

  // 키보드 이벤트 핸들러
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (disabled) return;

    switch (e.key) {
      case 'Enter':
      case ' ':
        e.preventDefault();
        if (isOpen && highlightedIndex >= 0 && highlightedIndex < filteredOptions.length) {
          handleOptionSelect(filteredOptions[highlightedIndex]);
        } else {
          toggleDropdown();
        }
        break;
      case 'Escape':
        e.preventDefault();
        setIsOpen(false);
        break;
      case 'ArrowDown':
        e.preventDefault();
        if (!isOpen) {
          setIsOpen(true);
          setHighlightedIndex(0);
        } else {
          setHighlightedIndex(prev => (prev < filteredOptions.length - 1 ? prev + 1 : 0));
        }
        break;
      case 'ArrowUp':
        e.preventDefault();
        if (!isOpen) {
          setIsOpen(true);
          setHighlightedIndex(filteredOptions.length - 1);
        } else {
          setHighlightedIndex(prev => (prev > 0 ? prev - 1 : filteredOptions.length - 1));
        }
        break;
      case 'Tab':
        if (isOpen) {
          e.preventDefault();
          setIsOpen(false);
        }
        break;
      default:
        break;
    }
  };

  // 옵션 선택 핸들러
  const handleOptionSelect = (option: DropdownOption) => {
    if (option.disabled) return;

    if (onChange) {
      onChange(option.value);
    }

    setIsOpen(false);
    setSearchTerm('');
  };

  // 검색어 변경 핸들러
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  // 검색 결과 필터링
  const filteredOptions =
    searchable && searchTerm
      ? options.filter(option => option.label.toLowerCase().includes(searchTerm.toLowerCase()))
      : options;

  // 외부 클릭 감지
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // 드롭다운 열릴 때 검색 입력에 포커스
  useEffect(() => {
    if (isOpen && searchable && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isOpen, searchable]);

  // 하이라이트된 옵션으로 스크롤
  useEffect(() => {
    if (isOpen && highlightedIndex >= 0 && optionsRef.current[highlightedIndex]) {
      optionsRef.current[highlightedIndex].scrollIntoView({ block: 'nearest' });
    }
  }, [isOpen, highlightedIndex]);

  // 드롭다운 클래스 생성
  const dropdownClasses = [
    'dropdown',
    disabled ? 'dropdown--disabled' : '',
    error ? 'dropdown--error' : '',
    fullWidth ? 'dropdown--full-width' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={dropdownClasses} ref={dropdownRef}>
      {label && (
        <label
          className="dropdown-label"
          id={`dropdown-label-${label.replace(/\s+/g, '-').toLowerCase()}`}
        >
          {label}
          {required && <span className="dropdown-required">*</span>}
        </label>
      )}

      <div
        className="dropdown-select"
        onClick={toggleDropdown}
        tabIndex={disabled ? -1 : 0}
        role="combobox"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-labelledby={
          label ? `dropdown-label-${label.replace(/\s+/g, '-').toLowerCase()}` : undefined
        }
        aria-label={!label && ariaLabel ? ariaLabel : undefined}
        aria-describedby={ariaDescription ? `dropdown-description` : undefined}
        aria-disabled={disabled}
        aria-controls={isOpen ? 'dropdown-options' : undefined}
        aria-activedescendant={
          isOpen && highlightedIndex >= 0 ? `dropdown-option-${highlightedIndex}` : undefined
        }
        onKeyDown={handleKeyDown}
      >
        <div className="dropdown-value">
          {selectedOption ? (
            <div className="dropdown-selected">
              {selectedOption.icon && (
                <span className="dropdown-option-icon">{selectedOption.icon}</span>
              )}
              <span className="dropdown-option-label">{selectedOption.label}</span>
            </div>
          ) : (
            <span className="dropdown-placeholder">{placeholder}</span>
          )}
        </div>
        <div className="dropdown-arrow">
          <svg
            width="10"
            height="6"
            viewBox="0 0 10 6"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M1 1L5 5L9 1"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
      </div>

      {isOpen && (
        <div className="dropdown-menu">
          {searchable && (
            <div className="dropdown-search">
              <input
                type="text"
                className="dropdown-search-input"
                placeholder={searchPlaceholder}
                value={searchTerm}
                onChange={handleSearchChange}
                ref={searchInputRef}
                onClick={e => e.stopPropagation()}
              />
            </div>
          )}

          <ul
            className="dropdown-options"
            role="listbox"
            id="dropdown-options"
            aria-labelledby={
              label ? `dropdown-label-${label.replace(/\s+/g, '-').toLowerCase()}` : undefined
            }
          >
            {filteredOptions.length > 0 ? (
              filteredOptions.map((option, index) => (
                <li
                  key={option.value}
                  ref={el => {
                    if (el) optionsRef.current[index] = el;
                  }}
                  className={`dropdown-option ${
                    option.disabled ? 'dropdown-option--disabled' : ''
                  } ${option.value === value ? 'dropdown-option--selected' : ''} ${
                    index === highlightedIndex ? 'dropdown-option--highlighted' : ''
                  }`}
                  onClick={() => handleOptionSelect(option)}
                  onMouseEnter={() => setHighlightedIndex(index)}
                  onMouseLeave={() => setHighlightedIndex(-1)}
                  role="option"
                  id={`dropdown-option-${index}`}
                  aria-selected={option.value === value}
                  aria-disabled={option.disabled}
                  tabIndex={-1}
                >
                  {option.icon && <span className="dropdown-option-icon">{option.icon}</span>}
                  <span className="dropdown-option-label">{option.label}</span>
                </li>
              ))
            ) : (
              <li className="dropdown-no-options">결과 없음</li>
            )}
          </ul>
        </div>
      )}

      {ariaDescription && (
        <div id="dropdown-description" className="sr-only">
          {ariaDescription}
        </div>
      )}

      {error && (
        <div className="dropdown-error" aria-live="assertive">
          {error}
        </div>
      )}
    </div>
  );
};

export default Dropdown;
