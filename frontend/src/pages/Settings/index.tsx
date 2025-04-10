import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../types';
import { setTheme } from '../../store/slices/uiSlice';
import './Settings.css';

interface SettingsSection {
  id: string;
  label: string;
  icon: string;
}

interface StockPreference {
  symbol: string;
  name: string;
  selected: boolean;
}

interface NotificationSetting {
  type: string;
  label: string;
  enabled: boolean;
}

const Settings: React.FC = () => {
  const dispatch = useDispatch();
  const { theme } = useSelector((state: RootState) => state.ui);
  const { user } = useSelector((state: RootState) => state.auth);
  
  const [activeSection, setActiveSection] = useState<string>('general');
  const [notificationSettings, setNotificationSettings] = useState<NotificationSetting[]>([
    { type: 'news', label: '뉴스 알림', enabled: true },
    { type: 'price', label: '가격 변동 알림', enabled: true },
    { type: 'analysis', label: '분석 리포트 알림', enabled: false },
    { type: 'sentiment', label: '감성 분석 알림', enabled: true },
    { type: 'earnings', label: '실적 발표 알림', enabled: true },
  ]);
  const [stockPreferences, setStockPreferences] = useState<StockPreference[]>([
    { symbol: 'AAPL', name: 'Apple Inc.', selected: true },
    { symbol: 'MSFT', name: 'Microsoft Corporation', selected: true },
    { symbol: 'GOOG', name: 'Alphabet Inc.', selected: true },
    { symbol: 'AMZN', name: 'Amazon.com, Inc.', selected: false },
    { symbol: 'TSLA', name: 'Tesla, Inc.', selected: false },
    { symbol: 'META', name: 'Meta Platforms, Inc.', selected: false },
    { symbol: 'NVDA', name: 'NVIDIA Corporation', selected: true },
    { symbol: 'NFLX', name: 'Netflix, Inc.', selected: false },
    { symbol: 'BABA', name: 'Alibaba Group Holding Limited', selected: false },
    { symbol: '005930', name: 'Samsung Electronics Co., Ltd.', selected: true },
  ]);
  
  const sections: SettingsSection[] = [
    { id: 'general', label: '일반 설정', icon: '⚙️' },
    { id: 'stocks', label: '관심 종목', icon: '📈' },
    { id: 'notifications', label: '알림 설정', icon: '🔔' },
    { id: 'data', label: '데이터 설정', icon: '📊' },
    { id: 'account', label: '계정 관리', icon: '👤' },
  ];
  
  const handleThemeChange = (newTheme: 'light' | 'dark') => {
    dispatch(setTheme(newTheme));
  };
  
  const handleToggleNotification = (type: string) => {
    setNotificationSettings(prev => 
      prev.map(item => 
        item.type === type ? { ...item, enabled: !item.enabled } : item
      )
    );
  };
  
  const handleToggleStock = (symbol: string) => {
    setStockPreferences(prev => 
      prev.map(item => 
        item.symbol === symbol ? { ...item, selected: !item.selected } : item
      )
    );
  };
  
  const renderGeneralSettings = () => (
    <div className="settings-content">
      <h2>일반 설정</h2>
      
      <div className="settings-group">
        <h3>테마</h3>
        <div className="theme-selector">
          <div
            className={`theme-option ${theme === 'light' ? 'active' : ''}`}
            onClick={() => handleThemeChange('light')}
          >
            <div className="theme-preview light-theme">
              <div className="theme-header"></div>
              <div className="theme-body"></div>
            </div>
            <span>라이트 모드</span>
          </div>
          
          <div 
            className={`theme-option ${theme === 'dark' ? 'active' : ''}`}
            onClick={() => handleThemeChange('dark')}
          >
            <div className="theme-preview dark-theme">
              <div className="theme-header"></div>
              <div className="theme-body"></div>
            </div>
            <span>다크 모드</span>
          </div>
        </div>
      </div>
      
      <div className="settings-group">
        <h3>언어 설정</h3>
        <select className="select-input" defaultValue="ko">
          <option value="ko">한국어</option>
          <option value="en">English</option>
          <option value="zh">中文</option>
          <option value="ja">日本語</option>
        </select>
      </div>
      
      <div className="settings-group">
        <h3>시간대 설정</h3>
        <select className="select-input" defaultValue="Asia/Seoul">
          <option value="Asia/Seoul">서울 (UTC+9)</option>
          <option value="America/New_York">뉴욕 (UTC-5/4)</option>
          <option value="Europe/London">런던 (UTC+0/1)</option>
          <option value="Asia/Tokyo">도쿄 (UTC+9)</option>
          <option value="Asia/Shanghai">상하이 (UTC+8)</option>
        </select>
      </div>
    </div>
  );
  
  const renderStocksSettings = () => (
    <div className="settings-content">
      <h2>관심 종목 설정</h2>
      <p className="settings-description">대시보드와 알림에 표시될 주식 종목을 선택해주세요.</p>
      
      <div className="stock-preferences">
        {stockPreferences.map(stock => (
          <div key={stock.symbol} className="stock-preference-item">
            <label className="checkbox-container">
              <input
                type="checkbox"
                checked={stock.selected}
                onChange={() => handleToggleStock(stock.symbol)}
              />
              <span className="checkmark"></span>
              <span className="stock-symbol">{stock.symbol}</span>
              <span className="stock-name">{stock.name}</span>
            </label>
          </div>
        ))}
      </div>
      
      <button className="add-stock-button">
        <span>종목 추가</span>
        <span className="icon">+</span>
      </button>
    </div>
  );
  
  const renderNotificationsSettings = () => (
    <div className="settings-content">
      <h2>알림 설정</h2>
      <p className="settings-description">받고 싶은 알림 유형을 선택해주세요.</p>
      
      <div className="notification-settings">
        {notificationSettings.map(notification => (
          <div key={notification.type} className="notification-setting-item">
            <label className="toggle-container">
              <span className="notification-label">{notification.label}</span>
              <div className="toggle-switch">
                <input
                  type="checkbox"
                  checked={notification.enabled}
                  onChange={() => handleToggleNotification(notification.type)}
                />
                <span className="toggle-slider"></span>
              </div>
            </label>
          </div>
        ))}
      </div>
      
      <div className="settings-group">
        <h3>알림 빈도</h3>
        <select className="select-input" defaultValue="realtime">
          <option value="realtime">실시간</option>
          <option value="hourly">시간별</option>
          <option value="daily">일별 요약</option>
          <option value="weekly">주간 요약</option>
        </select>
      </div>
      
      <div className="settings-group">
        <h3>방해 금지 시간</h3>
        <div className="time-range-picker">
          <div className="time-input">
            <label>시작</label>
            <input type="time" defaultValue="22:00" />
          </div>
          <div className="time-input">
            <label>종료</label>
            <input type="time" defaultValue="08:00" />
          </div>
        </div>
      </div>
    </div>
  );
  
  const renderDataSettings = () => (
    <div className="settings-content">
      <h2>데이터 설정</h2>
      
      <div className="settings-group">
        <h3>기본 차트 기간</h3>
        <select className="select-input" defaultValue="1m">
          <option value="1d">1일</option>
          <option value="1w">1주</option>
          <option value="1m">1개월</option>
          <option value="3m">3개월</option>
          <option value="6m">6개월</option>
          <option value="1y">1년</option>
          <option value="5y">5년</option>
        </select>
      </div>
      
      <div className="settings-group">
        <h3>차트 스타일</h3>
        <select className="select-input" defaultValue="candle">
          <option value="line">선 차트</option>
          <option value="candle">캔들스틱 차트</option>
          <option value="ohlc">OHLC 차트</option>
          <option value="area">영역 차트</option>
        </select>
      </div>
      
      <div className="settings-group">
        <h3>기술적 지표</h3>
        <div className="checkbox-list">
          <label className="checkbox-container">
            <input type="checkbox" checked />
            <span className="checkmark"></span>
            <span>이동평균선 (MA)</span>
          </label>
          <label className="checkbox-container">
            <input type="checkbox" checked />
            <span className="checkmark"></span>
            <span>상대강도지수 (RSI)</span>
          </label>
          <label className="checkbox-container">
            <input type="checkbox" />
            <span className="checkmark"></span>
            <span>볼린저 밴드</span>
          </label>
          <label className="checkbox-container">
            <input type="checkbox" />
            <span className="checkmark"></span>
            <span>MACD</span>
          </label>
        </div>
      </div>
      
      <div className="settings-group">
        <h3>데이터 새로고침 빈도</h3>
        <select className="select-input" defaultValue="1m">
          <option value="10s">10초</option>
          <option value="30s">30초</option>
          <option value="1m">1분</option>
          <option value="5m">5분</option>
          <option value="15m">15분</option>
          <option value="30m">30분</option>
        </select>
      </div>
    </div>
  );
  
  const renderAccountSettings = () => (
    <div className="settings-content">
      <h2>계정 관리</h2>
      
      <div className="settings-group">
        <h3>프로필 정보</h3>
        <div className="profile-info">
          <div className="profile-avatar">
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div className="profile-details">
            <div className="form-group">
              <label>이름</label>
              <input type="text" defaultValue={user?.username || ''} className="text-input" />
            </div>
            <div className="form-group">
              <label>이메일</label>
              <input type="email" defaultValue={user?.email || ''} className="text-input" readOnly />
            </div>
          </div>
        </div>
      </div>
      
      <div className="settings-group">
        <h3>비밀번호 변경</h3>
        <div className="form-group">
          <label>현재 비밀번호</label>
          <input type="password" className="text-input" />
        </div>
        <div className="form-group">
          <label>새 비밀번호</label>
          <input type="password" className="text-input" />
        </div>
        <div className="form-group">
          <label>비밀번호 확인</label>
          <input type="password" className="text-input" />
        </div>
        <button className="action-button">비밀번호 변경</button>
      </div>
      
      <div className="settings-group danger-zone">
        <h3>계정 삭제</h3>
        <p className="warning-text">
          계정을 삭제하면 모든 데이터가 영구적으로 제거됩니다. 이 작업은 되돌릴 수 없습니다.
        </p>
        <button className="danger-button">계정 삭제</button>
      </div>
    </div>
  );
  
  const renderActiveSection = () => {
    switch (activeSection) {
      case 'general':
        return renderGeneralSettings();
      case 'stocks':
        return renderStocksSettings();
      case 'notifications':
        return renderNotificationsSettings();
      case 'data':
        return renderDataSettings();
      case 'account':
        return renderAccountSettings();
      default:
        return renderGeneralSettings();
    }
  };
  
  return (
    <div className="settings-container">
      <h1 className="settings-title">설정</h1>
      
      <div className="settings-layout">
        <div className="settings-sidebar">
          {sections.map(section => (
            <div
              key={section.id}
              className={`settings-nav-item ${activeSection === section.id ? 'active' : ''}`}
              onClick={() => setActiveSection(section.id)}
            >
              <span className="settings-nav-icon">{section.icon}</span>
              <span className="settings-nav-label">{section.label}</span>
            </div>
          ))}
        </div>
        
        <div className="settings-main">
          {renderActiveSection()}
          
          <div className="settings-actions">
            <button className="cancel-button">취소</button>
            <button className="save-button">저장</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;