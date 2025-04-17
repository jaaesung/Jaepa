"""
API 패키지

FastAPI 기반 API 애플리케이션을 제공합니다.
"""
import logging
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from api.middleware import setup_middleware
from api.responses import create_error_response, ResponseStatus
from api.exceptions import ApiException, ErrorCode, InternalServerException
from api.routes import auth, news, analysis

# 로깅 설정
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 생명 주기 관리
    
    Args:
        app: FastAPI 애플리케이션
    """
    # 시작 이벤트 (이전의 startup)
    logger.info("API 초기화 중...")
    
    # 전역 객체 초기화
    try:
        from analysis.finbert_sentiment import FinBERTSentiment
        from data.stock_data_store import StockDataStore
        from analysis.sentiment_price_analyzer import SentimentPriceAnalyzer
        
        # FinBERT 감성 분석기 초기화
        app.state.finbert = FinBERTSentiment()
        
        # 주식 데이터 저장소 초기화
        app.state.stock_data_store = StockDataStore()
        
        # 감성-가격 분석기 초기화
        app.state.sentiment_price_analyzer = SentimentPriceAnalyzer()
        
        logger.info("API 초기화 완료")
    except Exception as e:
        logger.error(f"API 초기화 실패: {str(e)}")
        raise
    
    yield  # 애플리케이션 실행 중
    
    # 종료 이벤트 (이전의 shutdown)
    logger.info("API 종료 중...")
    
    # 리소스 정리
    try:
        if hasattr(app.state, "stock_data_store"):
            app.state.stock_data_store.close()
        
        if hasattr(app.state, "sentiment_price_analyzer"):
            app.state.sentiment_price_analyzer.close()
        
        logger.info("API 종료 완료")
    except Exception as e:
        logger.error(f"API 종료 실패: {str(e)}")


def create_app(config: Optional[Dict[str, Any]] = None) -> FastAPI:
    """
    FastAPI 애플리케이션 생성
    
    Args:
        config: 설정 정보
        
    Returns:
        FastAPI: FastAPI 애플리케이션
    """
    # 기본 설정
    config = config or {}
    
    # FastAPI 앱 생성
    app = FastAPI(
        title=config.get("title", "금융 분석 API"),
        description=config.get("description", "FinBERT 모델과 Polygon API를 사용한 금융 분석 API"),
        version=config.get("version", "1.0.0"),
        lifespan=lifespan,
        docs_url=config.get("docs_url", "/api/docs"),
        redoc_url=config.get("redoc_url", "/api/redoc"),
        openapi_url=config.get("openapi_url", "/api/openapi.json")
    )
    
    # 미들웨어 설정
    setup_middleware(app, config)
    
    # 예외 핸들러 등록
    @app.exception_handler(ApiException)
    async def api_exception_handler(request: Request, exc: ApiException):
        """
        API 예외 핸들러
        
        Args:
            request: HTTP 요청
            exc: API 예외
            
        Returns:
            JSONResponse: JSON 응답
        """
        # 오류 로깅
        logger.error(
            f"API 예외 발생: {exc.error_code} - {exc.detail} "
            f"(상태 코드: {exc.status_code})"
        )
        
        # 오류 응답 생성
        error_detail = {
            "code": exc.error_code,
            "message": exc.detail["message"] if isinstance(exc.detail, dict) else str(exc.detail)
        }
        
        if hasattr(exc, "field") and exc.field:
            error_detail["field"] = exc.field
            
        if hasattr(exc, "details") and exc.details:
            error_detail["details"] = exc.details
        
        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                message=error_detail["message"],
                errors=[error_detail],
                meta_info={"request_id": getattr(request.state, "request_id", "unknown")}
            ),
            headers=exc.headers
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        HTTP 예외 핸들러
        
        Args:
            request: HTTP 요청
            exc: HTTP 예외
            
        Returns:
            JSONResponse: JSON 응답
        """
        # 오류 로깅
        logger.error(
            f"HTTP 예외 발생: {exc.detail} "
            f"(상태 코드: {exc.status_code})"
        )
        
        # 오류 응답 생성
        error_detail = {
            "code": f"HTTP_{exc.status_code}",
            "message": str(exc.detail)
        }
        
        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                message=str(exc.detail),
                errors=[error_detail],
                meta_info={"request_id": getattr(request.state, "request_id", "unknown")}
            ),
            headers=exc.headers
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        일반 예외 핸들러
        
        Args:
            request: HTTP 요청
            exc: 예외
            
        Returns:
            JSONResponse: JSON 응답
        """
        # 오류 로깅
        logger.exception(
            f"예상치 못한 예외 발생: {str(exc)} "
            f"(요청: {request.method} {request.url.path})"
        )
        
        # 디버그 모드 확인
        debug_mode = config.get("debug", False)
        
        # 오류 메시지 설정
        if debug_mode:
            error_message = str(exc)
            error_details = {
                "traceback": str(exc.__traceback__),
                "type": exc.__class__.__name__
            }
        else:
            error_message = "서버 내부 오류가 발생했습니다."
            error_details = None
        
        # 오류 응답 생성
        error_detail = {
            "code": ErrorCode.INTERNAL_SERVER_ERROR,
            "message": error_message
        }
        
        if error_details:
            error_detail["details"] = error_details
        
        return JSONResponse(
            status_code=500,
            content=create_error_response(
                message=error_message,
                errors=[error_detail],
                meta_info={"request_id": getattr(request.state, "request_id", "unknown")}
            )
        )
    
    # 라우터 등록
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(news.router, prefix="/api/v1")
    app.include_router(analysis.router, prefix="/api/v1")
    
    # 정적 파일 마운트
    if config.get("static_dir"):
        app.mount("/static", StaticFiles(directory=config["static_dir"]), name="static")
    
    # 템플릿 설정
    if config.get("templates_dir"):
        app.state.templates = Jinja2Templates(directory=config["templates_dir"])
    
    # 루트 엔드포인트
    @app.get("/")
    async def root():
        """
        루트 엔드포인트
        
        Returns:
            Dict[str, Any]: 기본 응답
        """
        return create_response(
            message="금융 분석 API에 오신 것을 환영합니다.",
            meta_info={"version": app.version}
        )
    
    @app.get("/api")
    async def api_root():
        """
        API 루트 엔드포인트
        
        Returns:
            Dict[str, Any]: API 정보
        """
        return create_response(
            data={
                "version": app.version,
                "endpoints": [
                    "/api/v1/auth/token",
                    "/api/v1/auth/register",
                    "/api/v1/auth/me",
                    "/api/v1/news",
                    "/api/v1/news/{news_id}",
                    "/api/v1/news/search",
                    "/api/v1/news/symbol/{symbol}",
                    "/api/v1/analysis/text",
                    "/api/v1/analysis/news",
                    "/api/v1/analysis/correlation",
                    "/api/v1/analysis/summary"
                ]
            },
            message="금융 분석 API에 오신 것을 환영합니다."
        )
    
    # 상태 확인 엔드포인트
    @app.get("/health")
    async def health_check():
        """
        상태 확인 엔드포인트
        
        Returns:
            Dict[str, Any]: 상태 정보
        """
        return create_response(
            data={"status": "ok"},
            message="서비스가 정상적으로 실행 중입니다."
        )
    
    # OpenAPI 스키마 커스터마이징
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes
        )
        
        # 서버 정보 추가
        openapi_schema["servers"] = [
            {"url": "/", "description": "현재 서버"}
        ]
        
        # 태그 정보 추가
        openapi_schema["tags"] = [
            {
                "name": "인증",
                "description": "사용자 인증 및 계정 관리 관련 엔드포인트"
            },
            {
                "name": "뉴스",
                "description": "뉴스 조회 및 검색 관련 엔드포인트"
            },
            {
                "name": "분석",
                "description": "감성 분석 및 상관관계 분석 관련 엔드포인트"
            }
        ]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi
    
    return app
