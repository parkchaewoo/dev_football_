import { useState } from 'react';

interface StrategyFormProps {
  initialName?: string;
  initialDescription?: string;
  onSave: (name: string, description: string) => void;
  onClose: () => void;
}

export default function StrategyForm({
  initialName = '',
  initialDescription = '',
  onSave,
  onClose,
}: StrategyFormProps) {
  const [name, setName] = useState(initialName);
  const [description, setDescription] = useState(initialDescription);

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-xl p-6 w-full max-w-sm">
        <h2 className="text-lg font-bold text-white mb-4">전략 저장</h2>
        <input
          className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 mb-3 outline-none focus:border-blue-500"
          placeholder="전략 이름"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <textarea
          className="w-full px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 mb-4 outline-none focus:border-blue-500 resize-none"
          placeholder="설명 (선택)"
          rows={3}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <div className="flex gap-2 justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm bg-gray-600 text-white rounded hover:bg-gray-500"
          >
            취소
          </button>
          <button
            onClick={() => name.trim() && onSave(name.trim(), description.trim())}
            disabled={!name.trim()}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-40"
          >
            저장
          </button>
        </div>
      </div>
    </div>
  );
}
