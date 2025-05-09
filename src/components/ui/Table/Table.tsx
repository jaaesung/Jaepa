/**
 * 테이블 컴포넌트
 *
 * 데이터를 표 형식으로 표시하는 테이블 컴포넌트를 제공합니다.
 */

import React from 'react';
import './Table.css';

export interface TableColumn<T> {
  /**
   * 컬럼 ID
   */
  id: string;

  /**
   * 컬럼 헤더
   */
  header: React.ReactNode;

  /**
   * 셀 렌더러
   */
  cell: (row: T, rowIndex: number) => React.ReactNode;

  /**
   * 컬럼 너비
   */
  width?: string;

  /**
   * 정렬
   */
  align?: 'left' | 'center' | 'right';

  /**
   * 정렬 가능 여부
   */
  sortable?: boolean;
}

export interface TableProps<T> {
  /**
   * 컬럼 정의
   */
  columns: TableColumn<T>[];

  /**
   * 데이터
   */
  data: T[];

  /**
   * 로딩 상태
   */
  isLoading?: boolean;

  /**
   * 에러 메시지
   */
  error?: string;

  /**
   * 빈 데이터 메시지
   */
  emptyMessage?: string;

  /**
   * 추가 클래스명
   */
  className?: string;

  /**
   * 행 클릭 핸들러
   */
  onRowClick?: (row: T, index: number) => void;

  /**
   * 정렬 컬럼
   */
  sortColumn?: string;

  /**
   * 정렬 방향
   */
  sortDirection?: 'asc' | 'desc';

  /**
   * 정렬 변경 핸들러
   */
  onSort?: (columnId: string, direction: 'asc' | 'desc') => void;

  /**
   * 스트라이프 적용 여부
   */
  striped?: boolean;

  /**
   * 테두리 적용 여부
   */
  bordered?: boolean;

  /**
   * 행 호버 효과 적용 여부
   */
  hoverable?: boolean;

  /**
   * 컴팩트 모드 적용 여부
   */
  compact?: boolean;

  /**
   * 테이블 요약 (스크린 리더용)
   */
  caption?: string;

  /**
   * 테이블 아리아 레이블 (스크린 리더용)
   */
  ariaLabel?: string;
}

/**
 * 테이블 컴포넌트
 */
function Table<T extends Record<string, any>>({
  columns,
  data,
  isLoading = false,
  error,
  emptyMessage = '데이터가 없습니다.',
  className = '',
  onRowClick,
  sortColumn,
  sortDirection,
  onSort,
  striped = false,
  bordered = false,
  hoverable = true,
  compact = false,
  caption,
  ariaLabel,
}: TableProps<T>) {
  // 정렬 토글 핸들러
  const handleSort = (columnId: string) => {
    if (!onSort) return;

    const newDirection = sortColumn === columnId && sortDirection === 'asc' ? 'desc' : 'asc';

    onSort(columnId, newDirection);
  };

  // 테이블 클래스 생성
  const tableClasses = [
    'table',
    striped ? 'table--striped' : '',
    bordered ? 'table--bordered' : '',
    hoverable ? 'table--hoverable' : '',
    compact ? 'table--compact' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  // 로딩 상태 렌더링
  if (isLoading) {
    return (
      <div className="table-container">
        <div className="table-loading">
          <div className="table-loading-spinner"></div>
          <p>데이터를 불러오는 중입니다...</p>
        </div>
      </div>
    );
  }

  // 에러 상태 렌더링
  if (error) {
    return (
      <div className="table-container">
        <div className="table-error">
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="table-container" role="region" aria-label={ariaLabel || '테이블 데이터'}>
      <table className={tableClasses}>
        {caption && <caption>{caption}</caption>}
        <thead className="table-header">
          <tr>
            {columns.map(column => (
              <th
                key={column.id}
                className={`table-header-cell ${column.align ? `table-cell--${column.align}` : ''}`}
                style={{ width: column.width }}
                onClick={column.sortable ? () => handleSort(column.id) : undefined}
                aria-sort={
                  sortColumn === column.id
                    ? sortDirection === 'asc'
                      ? 'ascending'
                      : 'descending'
                    : undefined
                }
              >
                <div className="table-header-content">
                  <span>{column.header}</span>

                  {column.sortable && (
                    <span className="table-sort-icon">
                      {sortColumn === column.id ? (
                        sortDirection === 'asc' ? (
                          <svg
                            width="10"
                            height="10"
                            viewBox="0 0 10 10"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                          >
                            <path d="M5 2L9 6H1L5 2Z" fill="currentColor" />
                          </svg>
                        ) : (
                          <svg
                            width="10"
                            height="10"
                            viewBox="0 0 10 10"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                          >
                            <path d="M5 8L1 4H9L5 8Z" fill="currentColor" />
                          </svg>
                        )
                      ) : (
                        <svg
                          width="10"
                          height="10"
                          viewBox="0 0 10 10"
                          fill="none"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <path d="M5 2L9 6H1L5 2Z" fill="currentColor" opacity="0.3" />
                          <path d="M5 8L1 4H9L5 8Z" fill="currentColor" opacity="0.3" />
                        </svg>
                      )}
                    </span>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>

        <tbody className="table-body">
          {data.length > 0 ? (
            data.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className={`table-row ${onRowClick ? 'table-row--clickable' : ''}`}
                onClick={onRowClick ? () => onRowClick(row, rowIndex) : undefined}
                role="row"
                aria-rowindex={rowIndex + 1}
              >
                {columns.map(column => (
                  <td
                    key={`${rowIndex}-${column.id}`}
                    className={`table-cell ${column.align ? `table-cell--${column.align}` : ''}`}
                  >
                    {column.cell(row, rowIndex)}
                  </td>
                ))}
              </tr>
            ))
          ) : (
            <tr className="table-empty-row">
              <td colSpan={columns.length} className="table-empty-cell">
                {emptyMessage}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

export default React.memo(Table);
