import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { getMyTeams } from '../../services/teamService';
import type { Team } from '../../types';
import TeamCreate from './TeamCreate';
import TeamJoin from './TeamJoin';

interface TeamListProps {
  onSelectTeam: (team: Team) => void;
}

export default function TeamList({ onSelectTeam }: TeamListProps) {
  const { profile, logout } = useAuth();
  const [teams, setTeams] = useState<Team[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [showJoin, setShowJoin] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!profile) return;
    getMyTeams(profile.uid).then((t) => {
      setTeams(t);
      setLoading(false);
    });
  }, [profile]);

  const refresh = async () => {
    if (!profile) return;
    setTeams(await getMyTeams(profile.uid));
  };

  if (loading) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-gray-900 text-white">
        로딩 중...
      </div>
    );
  }

  return (
    <div className="w-full h-screen flex items-center justify-center bg-gray-900">
      <div className="bg-gray-800 rounded-2xl p-6 w-full max-w-md shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-bold text-white">내 팀</h1>
            <p className="text-gray-400 text-sm">{profile?.displayName}</p>
          </div>
          <button
            onClick={logout}
            className="px-3 py-1 text-xs bg-gray-700 text-gray-300 rounded hover:bg-gray-600"
          >
            로그아웃
          </button>
        </div>

        {teams.length === 0 ? (
          <p className="text-gray-500 text-center py-8 text-sm">
            아직 가입한 팀이 없습니다.
          </p>
        ) : (
          <div className="flex flex-col gap-2 mb-4 max-h-80 overflow-y-auto">
            {teams.map((team) => (
              <button
                key={team.id}
                onClick={() => onSelectTeam(team)}
                className="flex items-center justify-between p-4 bg-gray-700 rounded-xl hover:bg-gray-600 text-left transition-colors"
              >
                <div>
                  <p className="text-white font-medium">{team.name}</p>
                  <p className="text-gray-400 text-xs">
                    {team.members.length}명 · 초대코드: {team.inviteCode}
                  </p>
                </div>
                <span className="text-gray-500 text-lg">›</span>
              </button>
            ))}
          </div>
        )}

        <div className="flex gap-2">
          <button
            onClick={() => setShowCreate(true)}
            className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700"
          >
            팀 만들기
          </button>
          <button
            onClick={() => setShowJoin(true)}
            className="flex-1 px-4 py-3 bg-green-600 text-white rounded-xl font-medium hover:bg-green-700"
          >
            팀 가입
          </button>
        </div>

        {showCreate && (
          <TeamCreate
            onCreated={() => { setShowCreate(false); refresh(); }}
            onClose={() => setShowCreate(false)}
          />
        )}
        {showJoin && (
          <TeamJoin
            onJoined={(team) => { setShowJoin(false); refresh(); onSelectTeam(team); }}
            onClose={() => setShowJoin(false)}
          />
        )}
      </div>
    </div>
  );
}
