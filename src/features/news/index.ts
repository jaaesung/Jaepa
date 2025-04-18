/**
 * 뉴스 기능 모듈
 *
 * 뉴스 관련 기능을 제공합니다.
 */

// 컴포넌트 내보내기
import { NewsCard, NewsList, NewsDetail, NewsFilter } from "./components";

// 훅 내보내기
import useNews from "./hooks/useNews";

// 서비스 내보내기
import newsService from "./services/newsService";

// 상태 관리 내보내기
import newsReducer, * as newsActions from "./store/newsSlice";

// 타입 내보내기
import * as newsTypes from "./types";

export {
  // 컴포넌트
  NewsCard,
  NewsList,
  NewsDetail,
  NewsFilter,

  // 훅
  useNews,

  // 서비스
  newsService,

  // 상태 관리
  newsReducer,
  newsActions,

  // 타입
  newsTypes,
};
