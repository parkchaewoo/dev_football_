import type { HighlightClip } from '../../types';
import { formatTime } from '../../utils/highlightDetector';

interface Props {
  clips: HighlightClip[];
  activeClipId: string | null;
  onPlayClip: (clip: HighlightClip) => void;
  onDeleteClip: (id: string) => void;
  onRenameClip: (id: string, label: string) => void;
}

const TYPE_LABELS: Record<HighlightClip['type'], string> = {
  'auto-audio': '🔊 오디오',
  'auto-motion': '🎬 장면변화',
  manual: '✏️ 수동',
};

const TYPE_COLORS: Record<HighlightClip['type'], string> = {
  'auto-audio': 'bg-amber-600',
  'auto-motion': 'bg-blue-600',
  manual: 'bg-green-600',
};

export default function HighlightClipList({ clips, activeClipId, onPlayClip, onDeleteClip, onRenameClip }: Props) {
  if (clips.length === 0) {
    return (
      <div className="text-gray-400 text-sm text-center py-8">
        감지된 하이라이트가 없습니다.
        <br />
        영상을 불러온 뒤 분석을 시작하세요.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2 overflow-y-auto max-h-[calc(100vh-300px)]">
      <div className="text-xs text-gray-400 px-1">
        총 {clips.length}개 하이라이트
      </div>
      {clips.map((clip) => (
        <div
          key={clip.id}
          className={`flex gap-2 p-2 rounded-lg cursor-pointer transition-colors ${
            activeClipId === clip.id ? 'bg-gray-600 ring-1 ring-blue-400' : 'bg-gray-700 hover:bg-gray-650'
          }`}
          onClick={() => onPlayClip(clip)}
        >
          {clip.thumbnail && (
            <img
              src={clip.thumbnail}
              alt={clip.label}
              className="w-24 h-14 object-cover rounded flex-shrink-0"
            />
          )}
          <div className="flex-1 min-w-0">
            <input
              className="text-sm font-medium bg-transparent border-none outline-none w-full text-white truncate"
              value={clip.label}
              onChange={(e) => onRenameClip(clip.id, e.target.value)}
              onClick={(e) => e.stopPropagation()}
            />
            <div className="flex items-center gap-2 mt-1">
              <span className={`text-[10px] px-1.5 py-0.5 rounded ${TYPE_COLORS[clip.type]}`}>
                {TYPE_LABELS[clip.type]}
              </span>
              <span className="text-xs text-gray-400">
                {formatTime(clip.startTime)} — {formatTime(clip.endTime)}
              </span>
            </div>
            <div className="flex items-center gap-1 mt-1">
              <div className="flex-1 h-1 bg-gray-600 rounded overflow-hidden">
                <div
                  className="h-full bg-yellow-400 rounded"
                  style={{ width: `${clip.confidence * 100}%` }}
                />
              </div>
              <span className="text-[10px] text-gray-500">{Math.round(clip.confidence * 100)}%</span>
            </div>
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
