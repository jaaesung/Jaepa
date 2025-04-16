"""
감성 분석 API 라우트 모듈

뉴스 감성 분석 및 주가 상관관계 분석 관련 API 엔드포인트를 정의합니다.
"""
import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# 프로젝트 루트 디렉토리를 sys.path에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.app.auth.auth_middleware import get_current_user
from crawling.gdelt_client import GDELTClient
from analysis.sentiment_stock_analyzer import SentimentStockAnalyzer
from analysis.sentiment_stock_visualizer import SentimentStockVisualizer

router = APIRouter(
    prefix="/api/sentiment",
    tags=["sentiment"],
    responses={404: {"description": "Not found"}},
)

# 클라이언트 초기화
gdelt_client = GDELTClient()
analyzer = SentimentStockAnalyzer()
visualizer = SentimentStockVisualizer()

# 모델 정의
class DateRangeParams(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    days: Optional[int] = None

class CorrelationParams(BaseModel):
    symbol: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    period_days: Optional[int] = 90
    force_update: Optional[bool] = False

class PatternParams(BaseModel):
    symbol: str
    lookback_days: Optional[int] = 365
    min_pattern_strength: Optional[float] = 0.3

class DashboardParams(BaseModel):
    symbol: str
    period_days: Optional[int] = 90

# API 엔드포인트
@router.get("/trends/{symbol}")
async def get_sentiment_trends(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days: Optional[int] = 30,
    interval: str = Query("day", description="시간 간격 ('hour', 'day', 'week', 'month')"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    특정 주식 심볼에 대한 감성 트렌드 조회
    """
    try:
        # 날짜 범위 설정
        end_date_obj = datetime.now() if not end_date else datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if start_date:
            start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        elif days:
            start_date_obj = end_date_obj - timedelta(days=days)
        else:
            start_date_obj = end_date_obj - timedelta(days=30)
        
        # 감성 트렌드 가져오기
        trends = gdelt_client.get_news_sentiment_trends(
            symbol=symbol,
            start_date=start_date_obj,
            end_date=end_date_obj,
            interval=interval
        )
        
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"감성 트렌드 조회 중 오류 발생: {str(e)}")

@router.get("/volume/{symbol}")
async def get_news_volume(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days: Optional[int] = 30,
    interval: str = Query("day", description="시간 간격 ('day', 'week', 'month')"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    특정 주식 심볼에 대한 뉴스 볼륨 조회
    """
    try:
        # 날짜 범위 설정
        end_date_obj = datetime.now() if not end_date else datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if start_date:
            start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        elif days:
            start_date_obj = end_date_obj - timedelta(days=days)
        else:
            start_date_obj = end_date_obj - timedelta(days=30)
        
        # 뉴스 볼륨 가져오기
        volume = gdelt_client.get_news_volume_by_symbol(
            symbol=symbol,
            start_date=start_date_obj,
            end_date=end_date_obj,
            interval=interval
        )
        
        return volume
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"뉴스 볼륨 조회 중 오류 발생: {str(e)}")

@router.get("/entities/{symbol}")
async def get_related_entities(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days: Optional[int] = 30,
    min_count: int = Query(2, description="최소 언급 횟수"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    특정 주식 심볼에 대한 관련 엔티티(인물, 조직, 장소 등) 조회
    """
    try:
        # 날짜 범위 설정
        end_date_obj = datetime.now() if not end_date else datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if start_date:
            start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        elif days:
            start_date_obj = end_date_obj - timedelta(days=days)
        else:
            start_date_obj = end_date_obj - timedelta(days=30)
        
        # 관련 엔티티 가져오기
        entities = gdelt_client.get_related_entities(
            symbol=symbol,
            start_date=start_date_obj,
            end_date=end_date_obj,
            min_count=min_count
        )
        
        return entities
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"관련 엔티티 조회 중 오류 발생: {str(e)}")

@router.post("/correlation")
async def analyze_correlation(
    params: CorrelationParams,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    감성과 주가 변동의 상관관계 분석
    """
    try:
        # 날짜 범위 설정
        if params.start_date and params.end_date:
            start_date_obj = datetime.fromisoformat(params.start_date.replace('Z', '+00:00'))
            end_date_obj = datetime.fromisoformat(params.end_date.replace('Z', '+00:00'))
        else:
            end_date_obj = datetime.now()
            start_date_obj = end_date_obj - timedelta(days=params.period_days)
        
        # 상관관계 분석
        correlation = analyzer.analyze_correlation(
            symbol=params.symbol,
            start_date=start_date_obj,
            end_date=end_date_obj,
            force_update=params.force_update
        )
        
        return correlation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상관관계 분석 중 오류 발생: {str(e)}")

@router.post("/patterns")
async def identify_patterns(
    params: PatternParams,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    주요 감성 패턴 식별
    """
    try:
        # 패턴 식별
        patterns = analyzer.identify_sentiment_patterns(
            symbol=params.symbol,
            lookback_days=params.lookback_days,
            min_pattern_strength=params.min_pattern_strength
        )
        
        return patterns
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"패턴 식별 중 오류 발생: {str(e)}")

@router.get("/charts/sentiment-vs-price/{symbol}")
async def get_sentiment_vs_price_chart(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days: Optional[int] = 90,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    감성과 주가 변동 비교 차트
    """
    try:
        # 날짜 범위 설정
        end_date_obj = datetime.now() if not end_date else datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if start_date:
            start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        elif days:
            start_date_obj = end_date_obj - timedelta(days=days)
        else:
            start_date_obj = end_date_obj - timedelta(days=90)
        
        # 차트 생성
        chart = visualizer.plot_sentiment_vs_price(
            symbol=symbol,
            start_date=start_date_obj,
            end_date=end_date_obj,
            return_base64=True
        )
        
        return {"image": chart}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"차트 생성 중 오류 발생: {str(e)}")

@router.get("/charts/sentiment-trends/{symbol}")
async def get_sentiment_trends_chart(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days: Optional[int] = 90,
    interval: str = Query("day", description="시간 간격 ('day', 'week', 'month')"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    감성 트렌드 시각화
    """
    try:
        # 날짜 범위 설정
        end_date_obj = datetime.now() if not end_date else datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if start_date:
            start_date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        elif days:
            start_date_obj = end_date_obj - timedelta(days=days)
        else:
            start_date_obj = end_date_obj - timedelta(days=90)
        
        # 차트 생성
        chart = visualizer.plot_sentiment_trends(
            symbol=symbol,
            start_date=start_date_obj,
            end_date=end_date_obj,
            interval=interval,
            return_base64=True
        )
        
        return {"image": chart}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"차트 생성 중 오류 발생: {str(e)}")

@router.get("/charts/pattern-impact/{symbol}")
async def get_pattern_impact_chart(
    symbol: str,
    pattern_type: Optional[str] = None,
    lookback_days: int = Query(365, description="분석 기간 (일)"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    특정 패턴의 주가 영향 시각화
    """
    try:
        # 차트 생성
        chart = visualizer.plot_pattern_impact(
            symbol=symbol,
            pattern_type=pattern_type,
            lookback_days=lookback_days,
            return_base64=True
        )
        
        return {"image": chart}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"차트 생성 중 오류 발생: {str(e)}")

@router.post("/dashboard")
async def generate_dashboard(
    params: DashboardParams,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    대시보드용 데이터 생성
    """
    try:
        # 대시보드 데이터 생성
        dashboard_data = visualizer.generate_dashboard_data(
            symbol=params.symbol,
            period_days=params.period_days
        )
        
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대시보드 데이터 생성 중 오류 발생: {str(e)}")

@router.get("/insights/{symbol}")
async def get_insights(
    symbol: str,
    period_days: int = Query(90, description="분석 기간 (일)"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    분석 인사이트 보고서 생성
    """
    try:
        # 인사이트 보고서 생성
        insights = analyzer.generate_insight_report(
            symbol=symbol,
            period_days=period_days
        )
        
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인사이트 보고서 생성 중 오류 발생: {str(e)}")

# 서버 종료 시 연결 종료
@router.on_event("shutdown")
def shutdown_event():
    analyzer.close()
