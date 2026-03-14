import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { createTeam } from '../../services/teamService';

interface TeamCreateProps {
  onCreated: () => void;
  onClose: () => void;
}

export default function TeamCreate({ onCreated, onClose }: TeamCreateProps) {
  const { profile } = useAuth();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);

  const handleCreate = async () => {
    if (!name.trim() || !profile) return;
    setSaving(true);
    await createTeam(name.trim(), description.trim(), profile.uid);
    setSaving(false);
    onCreated();
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-xl p-6 w-full max-w-sm">
        <h2 className="text-lg font-bold text-white mb-4">새 팀 만들기</h2>
        <input
          className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 mb-3 outline-none focus:border-blue-500"
          placeholder="팀 이름"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <textarea
          className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 mb-4 outline-none focus:border-blue-500 resize-none"
          placeholder="팀 설명 (선택)"
          rows={2}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <div className="flex gap-2 justify-end">
          <button onClick={onClose} className="px-4 py-2 text-sm bg-gray-600 text-white rounded hover:bg-gray-500">
            취소
          </button>
          <button
            onClick={handleCreate}
            disabled={!name.trim() || saving}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-40"
          >
            {saving ? '생성 중...' : '만들기'}
          </button>
        </div>
      </div>
    </div>
  );
}
