import { useState, useEffect } from 'react';
import { getTeamStrategies, getPublicStrategies } from '../../services/strategyService';
import type { StrategyMeta } from '../../types';
import LikeButton from '../Social/LikeButton';

interface StrategyFeedProps {
  teamId?: string;
  mode: 'team' | 'public';
  onLoad: (strategy: StrategyMeta) => void;
  onClose: () => void;
}

export default function StrategyFeed({ teamId, mode, onLoad, onClose }: StrategyFeedProps) {
  const [strategies, setStrategies] = useState<StrategyMeta[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      const data = mode === 'team' && teamId
        ? await getTeamStrategies(teamId)
        : await getPublicStrategies();
      setStrategies(data);
      setLoading(false);
    };
    fetch();
  }, [teamId, mode]);

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-xl p-6 w-full max-w-lg max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-white">
            {mode === 'team' ? '팀 전술' : '공개 전술'}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-xl">×</button>
        </div>

        {loading ? (
          <p className="text-gray-500 text-center py-8">로딩 중...</p>
        ) : strategies.length === 0 ? (
          <p className="text-gray-500 text-center py-8 text-sm">전술이 없습니다.</p>
        ) : (
          <div className="flex flex-col gap-3">
            {strategies.map((s) => (
              <div key={s.id} className="p-4 bg-gray-700 rounded-xl">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-white font-medium">{s.name}</p>
                    {s.description && (
                      <p className="text-gray-400 text-xs mt-1">{s.description}</p>
                    )}
                    <p className="text-gray-500 text-xs mt-1">
                      {s.authorName} · {s.teamName} · {s.phases.length}단계 ·{' '}
                      {new Date(s.updatedAt).toLocaleDateString('ko-KR')}
                    </p>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    s.visibility === 'public' ? 'bg-green-600/20 text-green-400' :
                    s.visibility === 'team' ? 'bg-blue-600/20 text-blue-400' :
                    'bg-gray-600/20 text-gray-400'
                  }`}>
                    {s.visibility === 'public' ? '공개' : s.visibility === 'team' ? '팀' : '비공개'}
                  </span>
                </div>
                <div className="flex items-center gap-2 mt-3">
                  <button
                    onClick={() => onLoad(s)}
                    className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    불러오기
                  </button>
                  <LikeButton strategyId={s.id} initialCount={s.likesCount} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
