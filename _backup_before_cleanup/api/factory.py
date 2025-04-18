"""
API 팩토리 모듈

FastAPI 애플리케이션을 생성하는 팩토리 함수를 제공합니다.
"""
import logging
from typing import Dict, Any, Optional, List, Callable
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from api.middleware import setup_middleware
from api.routes import auth, news, analysis

# 로깅 설정
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 생명 주기 관리자
    
    Args:
        app: FastAPI 애플리케이션
    """
    # 시작 이벤트 (이전의 startup)
    logger.info("API 초기화 중...")
    
    # 여기에 초기화 코드 추가
    
    logger.info("API 초기화 완료")
    
    yield  # 어플리케이션 실행 중
    
    # 종료 이벤트 (이전의 shutdown)
    logger.info("API 종료 중...")
    
    # 여기에 정리 코드 추가
    
    logger.info("API 종료 완료")


def create_app(config: Dict[str, Any]) -> FastAPI:
    """
    FastAPI 애플리케이션 생성
    
    Args:
        config: 설정 정보
        
    Returns:
        FastAPI: FastAPI 애플리케이션
    """
    # FastAPI 앱 생성
    app = FastAPI(
        title=config.get("title", "금융 분석 API"),
        description=config.get("description", "FinBERT 모델과 Polygon API를 사용한 금융 분석 API"),
        version=config.get("version", "1.0.0"),
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # 미들웨어 설정
    setup_middleware(app, config)
    
    # 정적 파일 마운트
    static_dir = config.get("static_dir", "static")
    if Path(static_dir).exists():
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # 템플릿 설정
    templates_dir = config.get("templates_dir", "templates")
    if Path(templates_dir).exists():
        templates = Jinja2Templates(directory=templates_dir)
        
        @app.get("/", response_class=HTMLResponse)
        async def root(request: Request):
            """루트 엔드포인트 - 대시보드 페이지 제공"""
            return templates.TemplateResponse("index.html", {"request": request})
    
    # API 기본 엔드포인트
    @app.get("/api")
    async def api_root():
        """기본 API 엔드포인트"""
        return {
            "message": "금융 분석 API에 오신 것을 환영합니다.",
            "version": config.get("version", "1.0.0"),
            "endpoints": [
                "/api/auth",
                "/api/news",
                "/api/analysis"
            ]
        }
    
    # 라우터 등록
    api_prefix = config.get("api_prefix", "/api")
    api_version = config.get("api_version", "v1")
    prefix = f"{api_prefix}/{api_version}"
    
    # 인증 라우터
    app.include_router(auth.router, prefix=prefix)
    
    # 뉴스 라우터
    app.include_router(news.router, prefix=prefix)
    
    # 분석 라우터
    app.include_router(analysis.router, prefix=prefix)
    
    logger.info(f"API 애플리케이션 생성 완료: {app.title} v{app.version}")
    return app
