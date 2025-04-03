/**
 * 프론트엔드 API 서비스 테스트 모듈
 * 
 * 이 모듈은 프론트엔드의 API 서비스를 테스트합니다.
 * 테스트를 실행하려면 Jest가 필요합니다.
 */
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';

// API 서비스 모듈 경로, 실제 환경에 맞게 조정 필요
import api from '../../frontend/src/services/api';

// Jest 목(mock) 설정
jest.mock('axios');

describe('API 서비스 테스트', () => {
  let mockAxios;

  beforeEach(() => {
    // axios 목 어댑터 설정
    mockAxios = new MockAdapter(axios);
    
    // localStorage 목 설정
    const localStorageMock = {
      getItem: jest.fn(),
      setItem: jest.fn(),
      removeItem: jest.fn()
    };
    Object.defineProperty(window, 'localStorage', { value: localStorageMock });
    
    // 환경 변수 목 설정 (API_BASE_URL이 process.env에서 제대로 로드되지 않을 경우)
    process.env.REACT_APP_API_URL = 'http://localhost:8000/api';
  });

  afterEach(() => {
    mockAxios.reset();
    jest.clearAllMocks();
  });

  test('API 요청 시 Authorization 헤더에 토큰이 포함되어야 함', () => {
    // 목 토큰 설정
    const mockToken = 'mock_jwt_token';
    localStorage.getItem.mockReturnValue(mockToken);
    
    // API 응답 목 설정
    mockAxios.onGet('http://localhost:8000/api/user/profile').reply(200, {
      id: 1,
      username: 'testuser',
      email: 'test@example.com'
    });
    
    // API 호출
    api.get('/user/profile')
      .then(response => {
        // 응답 검증
        expect(response.status).toBe(200);
        expect(response.data).toHaveProperty('username', 'testuser');
        
        // 요청 헤더 검증
        const request = mockAxios.history.get[0];
        expect(request.headers).toHaveProperty('Authorization', `Bearer ${mockToken}`);
      });
  });

  test('토큰이 없을 경우 Authorization 헤더가 없어야 함', () => {
    // 토큰 없음 설정
    localStorage.getItem.mockReturnValue(null);
    
    // API 응답 목 설정
    mockAxios.onGet('http://localhost:8000/api/public/data').reply(200, {
      message: 'Public data'
    });
    
    // API 호출
    api.get('/public/data')
      .then(response => {
        // 응답 검증
        expect(response.status).toBe(200);
        
        // 요청 헤더 검증 (Authorization 헤더가 없거나 undefined 여야 함)
        const request = mockAxios.history.get[0];
        expect(request.headers).not.toHaveProperty('Authorization');
      });
  });

  test('401 오류 시 리프레시 토큰으로 재시도해야 함', async () => {
    // 목 토큰 설정
    const mockToken = 'mock_jwt_token';
    const mockRefreshToken = 'mock_refresh_token';
    localStorage.getItem.mockImplementation((key) => {
      if (key === 'token') return mockToken;
      if (key === 'refreshToken') return mockRefreshToken;
      return null;
    });
    
    // 첫 요청에서 401 오류 응답 설정
    mockAxios.onGet('http://localhost:8000/api/user/data').replyOnce(401, {
      message: 'Unauthorized'
    });
    
    // 리프레시 토큰 요청에 대한 응답 설정
    mockAxios.onPost('http://localhost:8000/api/auth/refresh-token').replyOnce(200, {
      token: 'new_jwt_token'
    });
    
    // 재시도 요청에 대한 응답 설정
    mockAxios.onGet('http://localhost:8000/api/user/data').replyOnce(200, {
      message: 'User data'
    });
    
    // API 호출
    const response = await api.get('/user/data');
    
    // 응답 검증
    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('message', 'User data');
    
    // localStorage에 새 토큰이 저장되었는지 검증
    expect(localStorage.setItem).toHaveBeenCalledWith('token', 'new_jwt_token');
    
    // 리프레시 토큰 API가 호출되었는지 검증
    const refreshRequest = mockAxios.history.post.find(
      req => req.url === 'http://localhost:8000/api/auth/refresh-token'
    );
    expect(refreshRequest).toBeDefined();
    expect(JSON.parse(refreshRequest.data)).toHaveProperty('refresh_token', mockRefreshToken);
  });

  test('리프레시 토큰 오류 시 로그아웃 처리해야 함', async () => {
    // 목 토큰 설정
    const mockToken = 'mock_jwt_token';
    const mockRefreshToken = 'mock_refresh_token';
    localStorage.getItem.mockImplementation((key) => {
      if (key === 'token') return mockToken;
      if (key === 'refreshToken') return mockRefreshToken;
      return null;
    });
    
    // 첫 요청에서 401 오류 응답 설정
    mockAxios.onGet('http://localhost:8000/api/user/data').replyOnce(401, {
      message: 'Unauthorized'
    });
    
    // 리프레시 토큰 요청에 대한 오류 응답 설정
    mockAxios.onPost('http://localhost:8000/api/auth/refresh-token').replyOnce(401, {
      message: 'Invalid refresh token'
    });
    
    // API 호출 (오류가 발생해야 함)
    try {
      await api.get('/user/data');
      // 이 라인은 실행되지 않아야 함
      expect(true).toBe(false);
    } catch (error) {
      // 오류 검증
      expect(error.response.status).toBe(401);
      
      // localStorage에서 토큰이 제거되었는지 검증
      expect(localStorage.removeItem).toHaveBeenCalledWith('token');
      expect(localStorage.removeItem).toHaveBeenCalledWith('refreshToken');
    }
  });
});

/**
 * API 엔드포인트별 테스트
 */
describe('API 엔드포인트 테스트', () => {
  let mockAxios;

  beforeEach(() => {
    mockAxios = new MockAdapter(axios);
    const mockToken = 'mock_jwt_token';
    localStorage.getItem = jest.fn(key => key === 'token' ? mockToken : null);
  });

  afterEach(() => {
    mockAxios.reset();
    jest.clearAllMocks();
  });

  test('로그인 API', async () => {
    // 로그인 요청 데이터
    const loginData = {
      username: 'testuser',
      password: 'password123'
    };
    
    // API 응답 목 설정
    mockAxios.onPost('http://localhost:8000/api/auth/login').reply(200, {
      token: 'new_jwt_token',
      refresh_token: 'new_refresh_token',
      user: {
        id: 1,
        username: 'testuser'
      }
    });
    
    // API 호출
    const response = await api.post('/auth/login', loginData);
    
    // 응답 검증
    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('token');
    expect(response.data).toHaveProperty('refresh_token');
    expect(response.data).toHaveProperty('user');
    
    // 요청 데이터 검증
    const request = mockAxios.history.post[0];
    expect(JSON.parse(request.data)).toEqual(loginData);
  });

  test('주식 데이터 조회 API', async () => {
    // API 응답 목 설정
    mockAxios.onGet('http://localhost:8000/api/stocks/AAPL?period=1mo').reply(200, {
      symbol: 'AAPL',
      data: [
        {
          date: '2023-04-01',
          open: 150.0,
          close: 155.0,
          high: 157.0,
          low: 149.0,
          volume: 1000000
        },
        {
          date: '2023-04-02',
          open: 155.0,
          close: 158.0,
          high: 160.0,
          low: 154.0,
          volume: 1200000
        }
      ]
    });
    
    // API 호출
    const response = await api.get('/stocks/AAPL', { params: { period: '1mo' } });
    
    // 응답 검증
    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('symbol', 'AAPL');
    expect(response.data).toHaveProperty('data');
    expect(response.data.data).toHaveLength(2);
    expect(response.data.data[0]).toHaveProperty('date');
    expect(response.data.data[0]).toHaveProperty('close');
    
    // 요청 파라미터 검증
    const request = mockAxios.history.get[0];
    expect(request.params).toHaveProperty('period', '1mo');
  });

  test('뉴스 검색 API', async () => {
    // API 응답 목 설정
    mockAxios.onGet('http://localhost:8000/api/news/search?keyword=crypto&days=7').reply(200, {
      articles: [
        {
          title: 'Crypto Market Analysis',
          url: 'https://example.com/article1',
          source: 'reuters',
          published_date: '2023-04-01T00:00:00'
        },
        {
          title: 'Bitcoin Price Surge',
          url: 'https://example.com/article2',
          source: 'bloomberg',
          published_date: '2023-04-02T00:00:00'
        }
      ],
      total: 2
    });
    
    // API 호출
    const response = await api.get('/news/search', {
      params: { keyword: 'crypto', days: 7 }
    });
    
    // 응답 검증
    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('articles');
    expect(response.data.articles).toHaveLength(2);
    expect(response.data).toHaveProperty('total', 2);
    
    // 요청 파라미터 검증
    const request = mockAxios.history.get[0];
    expect(request.params).toHaveProperty('keyword', 'crypto');
    expect(request.params).toHaveProperty('days', 7);
  });
});
