/**
 * 주식 기능 모듈
 * 
 * 주식 관련 기능을 제공합니다.
 */

// 컴포넌트 내보내기
import { StockChart, StockInfo, StockSearch } from './components';

// 훅 내보내기
import useStock from './hooks/useStock';

// 서비스 내보내기
import stockService from './services/stockService';

// 상태 관리 내보내기
import stockReducer, * as stockActions from './store/stockSlice';

// 타입 내보내기
import * as stockTypes from './types';

export {
  // 컴포넌트
  StockChart,
  StockInfo,
  StockSearch,
  
  // 훅
  useStock,
  
  // 서비스
  stockService,
  
  // 상태 관리
  stockReducer,
  stockActions,
  
  // 타입
  stockTypes,
};
