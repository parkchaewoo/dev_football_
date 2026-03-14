interface PlaybackControlsProps {
  isPlaying: boolean;
  speed: number;
  onPlay: () => void;
  onPlayAll: () => void;
  onStop: () => void;
  onSpeedChange: (speed: number) => void;
  canPlay: boolean;
}

export default function PlaybackControls({
  isPlaying,
  speed,
  onPlay,
  onPlayAll,
  onStop,
  onSpeedChange,
  canPlay,
}: PlaybackControlsProps) {
  return (
    <div className="flex items-center gap-2 p-2 bg-gray-800 rounded-lg">
      {!isPlaying ? (
        <>
          <button
            onClick={onPlay}
            disabled={!canPlay}
            className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            ▶ 현재 단계 재생
          </button>
          <button
            onClick={onPlayAll}
            disabled={!canPlay}
            className="px-3 py-1 text-sm bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            ▶▶ 전체 재생
          </button>
        </>
      ) : (
        <button
          onClick={onStop}
          className="px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700"
        >
          ■ 정지
        </button>
      )}

      <div className="flex items-center gap-1 ml-2">
        <span className="text-xs text-gray-400">속도:</span>
        {[0.5, 1, 1.5, 2].map((s) => (
          <button
            key={s}
            onClick={() => onSpeedChange(s)}
            className={`px-2 py-0.5 text-xs rounded ${
              speed === s
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {s}x
          </button>
        ))}
      </div>
    </div>
  );
}
