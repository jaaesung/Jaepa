/**
 * 뉴스 카드 통합 테스트
 */

import React from 'react';
import { screen, fireEvent } from '@testing-library/react';
import { renderWithProviders } from '../../../../test/test-utils';
import { createTestData } from '../../../../test/test-utils';
import NewsCard from '../NewsCard/NewsCard';

describe('NewsCard Integration Test', () => {
  const mockArticle = createTestData.newsArticle({
    id: 'test-article-id',
    title: 'Test Article Title',
    content: 'This is a test article content that should be displayed in the news card.',
    source: 'Test Source',
    url: 'https://example.com/article',
    publishedAt: '2023-01-15T12:30:45Z',
    sentiment: 'positive',
    imageUrl: 'https://example.com/image.jpg',
  });

  const mockOnClick = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render news card correctly with all information', () => {
    renderWithProviders(<NewsCard article={mockArticle} onClick={mockOnClick} />);
    
    // 기본 정보 확인
    expect(screen.getByText(mockArticle.title)).toBeInTheDocument();
    expect(screen.getByText(mockArticle.source)).toBeInTheDocument();
    
    // 날짜 포맷 확인 (2023년 1월 15일 형식으로 표시)
    expect(screen.getByText(/2023년 1월 15일/i)).toBeInTheDocument();
    
    // 감성 분석 결과 확인
    expect(screen.getByText(/긍정적/i)).toBeInTheDocument();
    
    // 이미지 확인
    const image = screen.getByRole('img');
    expect(image).toHaveAttribute('src', mockArticle.imageUrl);
    expect(image).toHaveAttribute('alt', mockArticle.title);
  });

  it('should truncate long content', () => {
    const longContent = 'A'.repeat(300); // 300자 길이의 콘텐츠
    const articleWithLongContent = { ...mockArticle, content: longContent };
    
    renderWithProviders(<NewsCard article={articleWithLongContent} onClick={mockOnClick} />);
    
    // 콘텐츠가 잘렸는지 확인
    const displayedContent = screen.getByText(/A+/);
    expect(displayedContent.textContent?.length).toBeLessThan(longContent.length);
    expect(displayedContent.textContent?.endsWith('...')).toBe(true);
  });

  it('should call onClick handler when card is clicked', () => {
    renderWithProviders(<NewsCard article={mockArticle} onClick={mockOnClick} />);
    
    // 카드 클릭
    fireEvent.click(screen.getByRole('article'));
    
    // onClick 핸들러가 호출되었는지 확인
    expect(mockOnClick).toHaveBeenCalledTimes(1);
    expect(mockOnClick).toHaveBeenCalledWith(mockArticle);
  });

  it('should render with different sentiment indicators', () => {
    // 긍정적 감성
    const positiveArticle = { ...mockArticle, sentiment: 'positive' };
    const { rerender } = renderWithProviders(
      <NewsCard article={positiveArticle} onClick={mockOnClick} />
    );
    expect(screen.getByText(/긍정적/i)).toBeInTheDocument();
    expect(screen.getByTestId('sentiment-indicator')).toHaveClass('sentiment-positive');
    
    // 중립적 감성
    const neutralArticle = { ...mockArticle, sentiment: 'neutral' };
    rerender(<NewsCard article={neutralArticle} onClick={mockOnClick} />);
    expect(screen.getByText(/중립적/i)).toBeInTheDocument();
    expect(screen.getByTestId('sentiment-indicator')).toHaveClass('sentiment-neutral');
    
    // 부정적 감성
    const negativeArticle = { ...mockArticle, sentiment: 'negative' };
    rerender(<NewsCard article={negativeArticle} onClick={mockOnClick} />);
    expect(screen.getByText(/부정적/i)).toBeInTheDocument();
    expect(screen.getByTestId('sentiment-indicator')).toHaveClass('sentiment-negative');
  });

  it('should render with default image when imageUrl is not provided', () => {
    const articleWithoutImage = { ...mockArticle, imageUrl: undefined };
    
    renderWithProviders(<NewsCard article={articleWithoutImage} onClick={mockOnClick} />);
    
    // 기본 이미지 확인
    const image = screen.getByRole('img');
    expect(image).toHaveAttribute('src', 'default-news-image.jpg'); // 기본 이미지 경로 확인
    expect(image).toHaveAttribute('alt', mockArticle.title);
  });

  it('should render with compact layout when compact prop is true', () => {
    renderWithProviders(<NewsCard article={mockArticle} onClick={mockOnClick} compact />);
    
    // 컴팩트 레이아웃 클래스 확인
    expect(screen.getByRole('article')).toHaveClass('news-card--compact');
    
    // 컴팩트 모드에서는 콘텐츠가 표시되지 않음
    expect(screen.queryByText(mockArticle.content)).not.toBeInTheDocument();
  });

  it('should apply custom className when provided', () => {
    renderWithProviders(
      <NewsCard article={mockArticle} onClick={mockOnClick} className="custom-class" />
    );
    
    // 사용자 정의 클래스 확인
    expect(screen.getByRole('article')).toHaveClass('custom-class');
  });
});
