import type { GoalClip } from '../../types';
import { formatTime } from '../../utils/highlightDetector';

interface Props {
  clips: GoalClip[];
  activeClipId: string | null;
  onPlayClip: (clip: GoalClip) => void;
  onDeleteClip: (id: string) => void;
  onRenameClip: (id: string, label: string) => void;
}

const TYPE_LABELS: Record<GoalClip['type'], string> = {
  'auto-goal': '자동',
  manual: '수동',
};

export default function HighlightClipList({ clips, activeClipId, onPlayClip, onDeleteClip, onRenameClip }: Props) {
  if (clips.length === 0) {
    return (
      <div className="text-gray-400 text-sm text-center py-8">
        감지된 골이 없습니다.
        <br />
        영상을 불러온 뒤 골 감지를 시작하세요.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2 overflow-y-auto max-h-[calc(100vh-300px)]">
      {clips.map((clip) => (
        <div
          key={clip.id}
          className={`flex gap-2 p-2 rounded-lg cursor-pointer transition-colors ${
            activeClipId === clip.id ? 'bg-gray-600 ring-1 ring-red-400' : 'bg-gray-700 hover:bg-gray-650'
          }`}
          onClick={() => onPlayClip(clip)}
        >
          {clip.thumbnail ? (
            <img
              src={clip.thumbnail}
              alt={clip.label}
              className="w-24 h-14 object-cover rounded flex-shrink-0"
            />
          ) : (
            <div className="w-24 h-14 bg-gray-600 rounded flex-shrink-0 flex items-center justify-center text-2xl">
              ⚽
            </div>
          )}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-lg font-bold text-red-400">{clip.goalNumber}골</span>
              <span className={`text-[10px] px-1.5 py-0.5 rounded ${
                clip.type === 'auto-goal' ? 'bg-red-700' : 'bg-green-700'
              }`}>
                {TYPE_LABELS[clip.type]}
              </span>
            </div>
            <input
              className="text-xs bg-transparent border-none outline-none w-full text-gray-300 truncate"
              value={clip.label}
              onChange={(e) => onRenameClip(clip.id, e.target.value)}
              onClick={(e) => e.stopPropagation()}
            />
            <div className="flex items-center gap-2 mt-0.5">
              <span className="text-[11px] text-gray-400">
                {formatTime(clip.startTime)} — {formatTime(clip.endTime)}
              </span>
            </div>
            {clip.type === 'auto-goal' && (
              <div className="flex items-center gap-1 mt-0.5">
                <div className="flex-1 h-1 bg-gray-600 rounded overflow-hidden">
                  <div
                    className="h-full bg-red-400 rounded"
                    style={{ width: `${clip.confidence * 100}%` }}
                  />
                </div>
                <span className="text-[10px] text-gray-500">{Math.round(clip.confidence * 100)}%</span>
              </div>
            )}
          </div>
          <button
            className="self-start text-gray-500 hover:text-red-400 text-xs px-1"
            onClick={(e) => { e.stopPropagation(); onDeleteClip(clip.id); }}
            title="삭제"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
}
