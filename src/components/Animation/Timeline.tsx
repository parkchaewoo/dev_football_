import type { Frame } from '../../types';

interface TimelineProps {
  frames: Frame[];
  currentFrameIndex: number;
  onSelectFrame: (index: number) => void;
  onAddFrame: () => void;
  onDeleteFrame: (index: number) => void;
}

export default function Timeline({
  frames,
  currentFrameIndex,
  onSelectFrame,
  onAddFrame,
  onDeleteFrame,
}: TimelineProps) {
  return (
    <div className="flex items-center gap-2 p-2 bg-gray-800 rounded-lg overflow-x-auto">
      <span className="text-xs text-gray-400 whitespace-nowrap">프레임:</span>
      <div className="flex gap-1">
        {frames.map((_, i) => (
          <div key={i} className="flex items-center">
            <button
              onClick={() => onSelectFrame(i)}
              className={`w-8 h-8 rounded text-xs font-bold ${
                i === currentFrameIndex
                  ? 'bg-yellow-500 text-black'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {i + 1}
            </button>
            {frames.length > 1 && i === currentFrameIndex && (
              <button
                onClick={() => onDeleteFrame(i)}
                className="ml-0.5 text-red-400 hover:text-red-300 text-xs"
              >
                ×
              </button>
            )}
          </div>
        ))}
      </div>
      <button
        onClick={onAddFrame}
        className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 whitespace-nowrap"
      >
        + 프레임
      </button>
    </div>
  );
}
