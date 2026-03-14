import type { Strategy } from '../../types';
import { loadStrategies, deleteStrategy } from '../../utils/storage';
import { useState, useEffect } from 'react';

interface StrategyListProps {
  onLoad: (strategy: Strategy) => void;
  onClose: () => void;
}

export default function StrategyList({ onLoad, onClose }: StrategyListProps) {
  const [strategies, setStrategies] = useState<Strategy[]>([]);

  useEffect(() => {
    setStrategies(loadStrategies());
  }, []);

  const handleDelete = (id: string) => {
    if (confirm('이 전략을 삭제하시겠습니까?')) {
      deleteStrategy(id);
      setStrategies(loadStrategies());
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-xl p-6 w-full max-w-md max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-white">저장된 전략</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-xl"
          >
            ×
          </button>
        </div>

        {strategies.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            저장된 전략이 없습니다.
          </p>
        ) : (
          <div className="flex flex-col gap-2">
            {strategies.map((s) => (
              <div
                key={s.id}
                className="flex items-center justify-between p-3 bg-gray-700 rounded-lg"
              >
                <div>
                  <p className="text-white font-medium text-sm">{s.name}</p>
                  <p className="text-gray-400 text-xs">
                    {s.phases.length}단계 ·{' '}
                    {new Date(s.createdAt).toLocaleDateString('ko-KR')}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => onLoad(s)}
                    className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    불러오기
                  </button>
                  <button
                    onClick={() => handleDelete(s.id)}
                    className="px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
                  >
                    삭제
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
