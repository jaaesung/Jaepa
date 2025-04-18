/**
 * API 클라이언트 테스트
 */

import axios from 'axios';
import apiClient from '../client';
import { API_SERVICES } from '../../../core/constants/api';

// axios 모의 설정
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API Client', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('get', () => {
    it('should make a GET request with correct parameters', async () => {
      const mockResponse = { data: { id: 1, name: 'Test' } };
      mockedAxios.get.mockResolvedValueOnce(mockResponse);

      const result = await apiClient.get(API_SERVICES.AUTH, 'user');

      expect(mockedAxios.get).toHaveBeenCalledWith(
        `${process.env.REACT_APP_API_URL}/${API_SERVICES.AUTH}/user`,
        expect.any(Object)
      );
      expect(result).toEqual(mockResponse.data);
    });

    it('should include query parameters in the request', async () => {
      const mockResponse = { data: [{ id: 1, name: 'Test' }] };
      mockedAxios.get.mockResolvedValueOnce(mockResponse);

      const params = { page: 1, limit: 10 };
      await apiClient.get(API_SERVICES.NEWS, 'articles', params);

      expect(mockedAxios.get).toHaveBeenCalledWith(
        `${process.env.REACT_APP_API_URL}/${API_SERVICES.NEWS}/articles`,
        expect.objectContaining({
          params,
        })
      );
    });

    it('should handle errors correctly', async () => {
      const errorMessage = 'Network Error';
      mockedAxios.get.mockRejectedValueOnce(new Error(errorMessage));

      await expect(apiClient.get(API_SERVICES.AUTH, 'user')).rejects.toThrow(errorMessage);
    });
  });

  describe('post', () => {
    it('should make a POST request with correct parameters', async () => {
      const mockResponse = { data: { id: 1, name: 'Test' } };
      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      const data = { username: 'test', password: 'password' };
      const result = await apiClient.post(API_SERVICES.AUTH, 'login', data);

      expect(mockedAxios.post).toHaveBeenCalledWith(
        `${process.env.REACT_APP_API_URL}/${API_SERVICES.AUTH}/login`,
        data,
        expect.any(Object)
      );
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle errors correctly', async () => {
      const errorMessage = 'Invalid credentials';
      mockedAxios.post.mockRejectedValueOnce(new Error(errorMessage));

      const data = { username: 'test', password: 'wrong' };
      await expect(apiClient.post(API_SERVICES.AUTH, 'login', data)).rejects.toThrow(errorMessage);
    });
  });

  describe('put', () => {
    it('should make a PUT request with correct parameters', async () => {
      const mockResponse = { data: { id: 1, name: 'Updated Test' } };
      mockedAxios.put.mockResolvedValueOnce(mockResponse);

      const data = { name: 'Updated Test' };
      const result = await apiClient.put(API_SERVICES.AUTH, 'user/1', data);

      expect(mockedAxios.put).toHaveBeenCalledWith(
        `${process.env.REACT_APP_API_URL}/${API_SERVICES.AUTH}/user/1`,
        data,
        expect.any(Object)
      );
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('delete', () => {
    it('should make a DELETE request with correct parameters', async () => {
      const mockResponse = { data: { success: true } };
      mockedAxios.delete.mockResolvedValueOnce(mockResponse);

      const result = await apiClient.delete(API_SERVICES.AUTH, 'user/1');

      expect(mockedAxios.delete).toHaveBeenCalledWith(
        `${process.env.REACT_APP_API_URL}/${API_SERVICES.AUTH}/user/1`,
        expect.any(Object)
      );
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('patch', () => {
    it('should make a PATCH request with correct parameters', async () => {
      const mockResponse = { data: { id: 1, name: 'Partially Updated' } };
      mockedAxios.patch.mockResolvedValueOnce(mockResponse);

      const data = { name: 'Partially Updated' };
      const result = await apiClient.patch(API_SERVICES.AUTH, 'user/1', data);

      expect(mockedAxios.patch).toHaveBeenCalledWith(
        `${process.env.REACT_APP_API_URL}/${API_SERVICES.AUTH}/user/1`,
        data,
        expect.any(Object)
      );
      expect(result).toEqual(mockResponse.data);
    });
  });
});
