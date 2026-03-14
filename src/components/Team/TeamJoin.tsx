import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { joinTeamByCode } from '../../services/teamService';
import type { Team } from '../../types';

interface TeamJoinProps {
  onJoined: (team: Team) => void;
  onClose: () => void;
}

export default function TeamJoin({ onJoined, onClose }: TeamJoinProps) {
  const { profile } = useAuth();
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [joining, setJoining] = useState(false);

  const handleJoin = async () => {
    if (!code.trim() || !profile) return;
    setJoining(true);
    setError('');
    const team = await joinTeamByCode(code.trim().toUpperCase(), profile.uid);
    setJoining(false);
    if (team) {
      onJoined(team);
    } else {
      setError('유효하지 않은 초대코드입니다.');
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-xl p-6 w-full max-w-sm">
        <h2 className="text-lg font-bold text-white mb-4">팀 가입</h2>
        <input
          className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 mb-2 outline-none focus:border-blue-500 uppercase tracking-widest text-center text-lg"
          placeholder="초대코드 입력"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          maxLength={6}
        />
        {error && <p className="text-red-400 text-xs mb-2">{error}</p>}
        <p className="text-gray-500 text-xs mb-4">팀 리더에게 6자리 초대코드를 받으세요.</p>
        <div className="flex gap-2 justify-end">
          <button onClick={onClose} className="px-4 py-2 text-sm bg-gray-600 text-white rounded hover:bg-gray-500">
            취소
          </button>
          <button
            onClick={handleJoin}
            disabled={code.trim().length < 6 || joining}
            className="px-4 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-40"
          >
            {joining ? '가입 중...' : '가입'}
          </button>
        </div>
      </div>
    </div>
  );
}
