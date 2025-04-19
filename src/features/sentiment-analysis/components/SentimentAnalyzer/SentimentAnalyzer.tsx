/**
 * 감성 분석기 컴포넌트
 *
 * 텍스트 입력을 받아 감성 분석을 수행하는 컴포넌트를 제공합니다.
 */

import React, { useState, useEffect } from 'react';
import { Button, Card } from '../../../../components/ui';
import { useSentiment } from '../../hooks/useSentiment';
import { SentimentModel } from '../../types';
import SentimentResult from '../SentimentResult';
import './SentimentAnalyzer.css';

interface SentimentAnalyzerProps {
  initialText?: string;
  onAnalysisComplete?: (result: Record<string, any>) => void;
}

/**
 * 감성 분석기 컴포넌트
 */
const SentimentAnalyzer: React.FC<SentimentAnalyzerProps> = ({
  initialText = '',
  onAnalysisComplete,
}) => {
  const [text, setText] = useState(initialText);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const { analyzeText, results, isLoading, error, models, getModels, modelsLoading } =
    useSentiment();

  // 모델 목록 가져오기
  useEffect(() => {
    if (models.length === 0) {
      getModels();
    } else if (selectedModel === '' && models.length > 0) {
      // 기본 모델 선택
      const defaultModel = models.find((model: SentimentModel) => model.isDefault);
      setSelectedModel(defaultModel?.id || models[0].id);
    }
  }, [getModels, models, selectedModel]);

  // 텍스트 변경 핸들러
  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
  };

  // 모델 변경 핸들러
  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedModel(e.target.value);
  };

  // 분석 핸들러
  const handleAnalyze = async () => {
    if (!text.trim()) return;

    const success = await analyzeText({
      text,
      modelId: selectedModel,
      model: selectedModel, // 레거시 코드와의 호환성을 위해 추가
    });

    if (success && onAnalysisComplete) {
      onAnalysisComplete(results[text]);
    }
  };

  // 결과 가져오기
  const result = text ? results[text] : null;

  return (
    <Card className="sentiment-analyzer">
      <div className="sentiment-analyzer-header">
        <h2 className="sentiment-analyzer-title">감성 분석</h2>
        <p className="sentiment-analyzer-description">텍스트를 입력하여 감성 분석을 수행하세요.</p>
      </div>

      <div className="sentiment-analyzer-content">
        <div className="sentiment-analyzer-input">
          <textarea
            className="sentiment-text-input"
            value={text}
            onChange={handleTextChange}
            placeholder="분석할 텍스트를 입력하세요..."
            rows={5}
          />

          <div className="sentiment-analyzer-options">
            <div className="sentiment-model-selector">
              <label htmlFor="model-select">분석 모델:</label>
              <select
                id="model-select"
                value={selectedModel}
                onChange={handleModelChange}
                disabled={modelsLoading || isLoading}
              >
                {modelsLoading ? (
                  <option value="">모델 로딩 중...</option>
                ) : (
                  models.map((model: SentimentModel) => (
                    <option key={model.id} value={model.id}>
                      {model.name}
                    </option>
                  ))
                )}
              </select>
            </div>

            <Button
              onClick={handleAnalyze}
              isLoading={isLoading}
              disabled={!text.trim() || isLoading}
            >
              분석하기
            </Button>
          </div>

          {error && <div className="sentiment-analyzer-error">{error}</div>}
        </div>

        {result && (
          <div className="sentiment-analyzer-result">
            <SentimentResult result={result} />
          </div>
        )}
      </div>
    </Card>
  );
};

export default SentimentAnalyzer;
