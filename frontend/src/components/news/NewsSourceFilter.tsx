import React, { useEffect, useState } from 'react';
import { getNewsSources } from '../../services/api';

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
  defaultSelected = ['traditional', 'enhanced', 'gdelt'],
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
      <h5 style={{ fontSize: '16px', fontWeight: 'bold', margin: '0 0 12px 0' }}>뉴스 소스</h5>
      <hr style={{ margin: '12px 0', border: 'none', borderTop: '1px solid #f0f0f0' }} />

      <div style={{ marginBottom: 8 }}>
        <label
          style={{
            display: 'flex',
            alignItems: 'center',
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          <input
            type="checkbox"
            checked={selectedSources.length === sources.length && sources.length > 0}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleSelectAll(e.target.checked)}
            disabled={loading}
            style={{ marginRight: '8px' }}
          />
          전체 선택
        </label>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', width: '100%', gap: '8px' }}>
        {loading ? (
          <div>로딩 중...</div>
        ) : (
          sources.map(source => (
            <label
              key={source.id}
              style={{ display: 'flex', alignItems: 'flex-start', cursor: 'pointer' }}
            >
              <input
                type="checkbox"
                checked={selectedSources.includes(source.id)}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  handleSourceChange(source.id, e.target.checked)
                }
                style={{ marginRight: '8px', marginTop: '3px' }}
              />
              <div>
                <div>{source.name}</div>
                <div style={{ fontSize: '12px', color: '#888' }}>{source.description}</div>
              </div>
            </label>
          ))
        )}
      </div>
    </div>
  );
};

export default NewsSourceFilter;
