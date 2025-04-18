/**
 * 감성 분석 결과 컴포넌트
 * 
 * 감성 분석 결과를 시각적으로 표시하는 컴포넌트를 제공합니다.
 */

import React from 'react';
import { SentimentResult as SentimentResultType } from '../../types';
import './SentimentResult.css';

interface SentimentResultProps {
  result: SentimentResultType;
}

/**
 * 감성 분석 결과 컴포넌트
 */
const SentimentResult: React.FC<SentimentResultProps> = ({ result }) => {
  // 감성 레이블에 따른 클래스 이름
  const getLabelClassName = (label: string) => {
    switch (label) {
      case 'positive':
        return 'sentiment-label-positive';
      case 'negative':
        return 'sentiment-label-negative';
      case 'neutral':
      default:
        return 'sentiment-label-neutral';
    }
  };

  // 감성 레이블에 따른 한글 텍스트
  const getLabelText = (label: string) => {
    switch (label) {
      case 'positive':
        return '긍정적';
      case 'negative':
        return '부정적';
      case 'neutral':
      default:
        return '중립적';
    }
  };

  // 감성 점수를 퍼센트로 변환
  const getScorePercent = (score: number) => {
    return Math.round(score * 100);
  };

  return (
    <div className="sentiment-result">
      <div className="sentiment-result-header">
        <h3 className="sentiment-result-title">분석 결과</h3>
        <div className={`sentiment-result-label ${getLabelClassName(result.label)}`}>
          {getLabelText(result.label)}
        </div>
      </div>

      <div className="sentiment-result-scores">
        <div className="sentiment-score-item">
          <div className="sentiment-score-label">긍정적</div>
          <div className="sentiment-score-bar-container">
            <div
              className="sentiment-score-bar sentiment-score-positive"
              style={{ width: `${getScorePercent(result.scores.positive)}%` }}
            ></div>
          </div>
          <div className="sentiment-score-value">{getScorePercent(result.scores.positive)}%</div>
        </div>

        <div className="sentiment-score-item">
          <div className="sentiment-score-label">중립적</div>
          <div className="sentiment-score-bar-container">
            <div
              className="sentiment-score-bar sentiment-score-neutral"
              style={{ width: `${getScorePercent(result.scores.neutral)}%` }}
            ></div>
          </div>
          <div className="sentiment-score-value">{getScorePercent(result.scores.neutral)}%</div>
        </div>

        <div className="sentiment-score-item">
          <div className="sentiment-score-label">부정적</div>
          <div className="sentiment-score-bar-container">
            <div
              className="sentiment-score-bar sentiment-score-negative"
              style={{ width: `${getScorePercent(result.scores.negative)}%` }}
            ></div>
          </div>
          <div className="sentiment-score-value">{getScorePercent(result.scores.negative)}%</div>
        </div>
      </div>

      <div className="sentiment-result-meta">
        <div className="sentiment-result-meta-item">
          <span className="sentiment-result-meta-label">모델:</span>
          <span className="sentiment-result-meta-value">{result.model}</span>
        </div>
        <div className="sentiment-result-meta-item">
          <span className="sentiment-result-meta-label">언어:</span>
          <span className="sentiment-result-meta-value">{result.language}</span>
        </div>
        <div className="sentiment-result-meta-item">
          <span className="sentiment-result-meta-label">분석 시간:</span>
          <span className="sentiment-result-meta-value">
            {new Date(result.timestamp).toLocaleString()}
          </span>
        </div>
      </div>
    </div>
  );
};

export default SentimentResult;
