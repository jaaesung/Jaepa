import React, { useEffect, useState } from 'react';
import { Checkbox, Divider, Typography, Space } from 'antd';
import { getNewsSources } from '../../services/api';

const { Title } = Typography;

interface NewsSource {
  id: string;
  name: string;
  description: string;
}

interface NewsSourceFilterProps {
  onChange: (selectedSources: string[]) => void;
  defaultSelected?: string[];
}

const NewsSourceFilter: React.FC<NewsSourceFilterProps> = ({ 
  onChange, 
  defaultSelected = ['traditional', 'enhanced', 'gdelt'] 
}) => {
  const [sources, setSources] = useState<NewsSource[]>([]);
  const [selectedSources, setSelectedSources] = useState<string[]>(defaultSelected);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchSources = async () => {
      try {
        setLoading(true);
        const sourcesData = await getNewsSources();
        setSources(sourcesData);
      } catch (error) {
        console.error('Failed to fetch news sources:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSources();
  }, []);

  const handleSourceChange = (sourceId: string, checked: boolean) => {
    let newSelectedSources: string[];
    
    if (checked) {
      newSelectedSources = [...selectedSources, sourceId];
    } else {
      newSelectedSources = selectedSources.filter(id => id !== sourceId);
    }
    
    setSelectedSources(newSelectedSources);
    onChange(newSelectedSources);
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      const allSourceIds = sources.map(source => source.id);
      setSelectedSources(allSourceIds);
      onChange(allSourceIds);
    } else {
      setSelectedSources([]);
      onChange([]);
    }
  };

  return (
    <div className="news-source-filter">
      <Title level={5}>뉴스 소스</Title>
      <Divider style={{ margin: '12px 0' }} />
      
      <div style={{ marginBottom: 8 }}>
        <Checkbox
          checked={selectedSources.length === sources.length && sources.length > 0}
          indeterminate={selectedSources.length > 0 && selectedSources.length < sources.length}
          onChange={(e) => handleSelectAll(e.target.checked)}
          disabled={loading}
        >
          전체 선택
        </Checkbox>
      </div>
      
      <Space direction="vertical" style={{ width: '100%' }}>
        {loading ? (
          <div>로딩 중...</div>
        ) : (
          sources.map(source => (
            <Checkbox
              key={source.id}
              checked={selectedSources.includes(source.id)}
              onChange={(e) => handleSourceChange(source.id, e.target.checked)}
            >
              <div>
                <div>{source.name}</div>
                <div style={{ fontSize: '12px', color: '#888' }}>{source.description}</div>
              </div>
            </Checkbox>
          ))
        )}
      </Space>
    </div>
  );
};

export default NewsSourceFilter;
