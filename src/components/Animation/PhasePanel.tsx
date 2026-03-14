import type { Phase } from '../../types';

interface PhasePanelProps {
  phases: Phase[];
  currentPhaseIndex: number;
  onSelectPhase: (index: number) => void;
  onAddPhase: () => void;
  onDeletePhase: (index: number) => void;
  onRenamePhase: (index: number, name: string) => void;
}

export default function PhasePanel({
  phases,
  currentPhaseIndex,
  onSelectPhase,
  onAddPhase,
  onDeletePhase,
  onRenamePhase,
}: PhasePanelProps) {
  return (
    <div className="flex flex-col gap-1 p-2 bg-gray-800 rounded-lg">
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm font-bold text-gray-300">단계</span>
        <button
          onClick={onAddPhase}
          className="px-2 py-0.5 text-xs bg-green-600 text-white rounded hover:bg-green-700"
        >
          + 추가
        </button>
      </div>
      <div className="flex flex-wrap gap-1">
        {phases.map((phase, i) => (
          <div
            key={phase.id}
            className={`flex items-center gap-1 px-2 py-1 rounded cursor-pointer text-xs ${
              i === currentPhaseIndex
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
            onClick={() => onSelectPhase(i)}
          >
            <input
              className="bg-transparent border-none outline-none w-20 text-xs"
              value={phase.name}
              onChange={(e) => onRenamePhase(i, e.target.value)}
              onClick={(e) => e.stopPropagation()}
            />
            {phases.length > 1 && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeletePhase(i);
                }}
                className="text-red-400 hover:text-red-300 ml-1"
              >
                ×
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
