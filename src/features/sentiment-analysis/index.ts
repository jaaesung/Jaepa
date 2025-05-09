/**
 * 감성 분석 기능 모듈
 * 
 * 감성 분석 관련 기능을 제공합니다.
 */

// 컴포넌트 내보내기
import { SentimentAnalyzer, SentimentResult, SentimentTrendChart } from './components';

// 훅 내보내기
import useSentiment from './hooks/useSentiment';

// 서비스 내보내기
import sentimentService from './services/sentimentService';

// 상태 관리 내보내기
import sentimentReducer, * as sentimentActions from './store/sentimentSlice';

// 타입 내보내기
import * as sentimentTypes from './types';

export {
  // 컴포넌트
  SentimentAnalyzer,
  SentimentResult,
  SentimentTrendChart,
  
  // 훅
  useSentiment,
  
  // 서비스
  sentimentService,
  
  // 상태 관리
  sentimentReducer,
  sentimentActions,
  
  // 타입
  sentimentTypes,
};
