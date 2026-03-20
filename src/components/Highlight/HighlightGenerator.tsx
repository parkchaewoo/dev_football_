import { useState, useRef, useCallback, useEffect } from 'react';
import type { HighlightClip, HighlightSettings, AnalysisProgress } from '../../types';
import { analyzeVideo, getDefaultSettings, formatTime } from '../../utils/highlightDetector';
import { generateId } from '../../utils/storage';
import HighlightClipList from './HighlightClipList';

interface Props {
  onClose: () => void;
}

export default function HighlightGenerator({ onClose }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [videoSrc, setVideoSrc] = useState<string | null>(null);
  const [videoName, setVideoName] = useState('');
  const [clips, setClips] = useState<HighlightClip[]>([]);
  const [activeClipId, setActiveClipId] = useState<string | null>(null);
  const [progress, setProgress] = useState<AnalysisProgress>({ phase: 'idle', percent: 0 });
  const [settings, setSettings] = useState<HighlightSettings>(getDefaultSettings);
  const [showSettings, setShowSettings] = useState(false);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);

  const isAnalyzing = progress.phase !== 'idle' && progress.phase !== 'done';

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (videoSrc) URL.revokeObjectURL(videoSrc);
    const url = URL.createObjectURL(file);
    setVideoSrc(url);
    setVideoName(file.name);
    setClips([]);
    setActiveClipId(null);
    setProgress({ phase: 'idle', percent: 0 });
  }, [videoSrc]);

  const handleAnalyze = useCallback(async () => {
    const video = videoRef.current;
    if (!video || !videoSrc) return;

    try {
      const detectedClips = await analyzeVideo(video, settings, setProgress);
      setClips(detectedClips);
    } catch (err) {
      console.error('Analysis failed:', err);
      setProgress({ phase: 'idle', percent: 0 });
    }
  }, [videoSrc, settings]);

  const handlePlayClip = useCallback((clip: HighlightClip) => {
    const video = videoRef.current;
    if (!video) return;
    setActiveClipId(clip.id);
    video.currentTime = clip.startTime;
    video.play();
  }, []);

  const handleDeleteClip = useCallback((id: string) => {
    setClips((prev) => prev.filter((c) => c.id !== id));
    if (activeClipId === id) setActiveClipId(null);
  }, [activeClipId]);

  const handleRenameClip = useCallback((id: string, label: string) => {
    setClips((prev) => prev.map((c) => (c.id === id ? { ...c, label } : c)));
  }, []);

  const handleAddManualClip = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;
    const start = Math.max(0, video.currentTime - 3);
    const end = Math.min(video.duration, video.currentTime + 4);
    const newClip: HighlightClip = {
      id: generateId(),
      startTime: start,
      endTime: end,
      label: `수동 마크 ${formatTime(video.currentTime)}`,
      type: 'manual',
      confidence: 1,
    };
    setClips((prev) => [...prev, newClip].sort((a, b) => a.startTime - b.startTime));
  }, []);

  const handleExportClipList = useCallback(() => {
    const data = clips.map((c) => ({
      label: c.label,
      start: formatTime(c.startTime),
      end: formatTime(c.endTime),
      startSec: c.startTime.toFixed(1),
      endSec: c.endTime.toFixed(1),
      type: c.type,
      confidence: Math.round(c.confidence * 100) + '%',
    }));
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `highlights-${videoName || 'video'}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [clips, videoName]);

  // Pause at clip end
  useEffect(() => {
    const video = videoRef.current;
    if (!video || !activeClipId) return;
    const clip = clips.find((c) => c.id === activeClipId);
    if (!clip) return;

    const onTimeUpdate = () => {
      if (video.currentTime >= clip.endTime) {
        video.pause();
        setActiveClipId(null);
      }
    };
    video.addEventListener('timeupdate', onTimeUpdate);
    return () => video.removeEventListener('timeupdate', onTimeUpdate);
  }, [activeClipId, clips]);

  // Cleanup URL on unmount
  useEffect(() => {
    return () => {
      if (videoSrc) URL.revokeObjectURL(videoSrc);
    };
  }, [videoSrc]);

  const phaseLabel: Record<AnalysisProgress['phase'], string> = {
    idle: '',
    'analyzing-audio': '오디오 분석 중...',
    'analyzing-video': '영상 분석 중...',
    merging: '클립 병합 중...',
    done: '분석 완료!',
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center">
      <div className="bg-gray-800 rounded-xl shadow-2xl w-[95vw] max-w-6xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700">
          <h2 className="text-lg font-bold">하이라이트 자동 생성기</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setShowSettings((v) => !v)}
              className="px-3 py-1 text-sm bg-gray-700 rounded hover:bg-gray-600"
            >
              설정
            </button>
            <button onClick={onClose} className="px-3 py-1 text-sm bg-gray-700 rounded hover:bg-gray-600">
              닫기
            </button>
          </div>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <div className="px-4 py-3 border-b border-gray-700 bg-gray-750 grid grid-cols-3 gap-4 text-sm">
            <label className="flex flex-col gap-1">
              <span className="text-gray-400">오디오 민감도 ({Math.round(settings.audioThreshold * 100)}%)</span>
              <input
                type="range" min="0.1" max="1" step="0.05"
                value={settings.audioThreshold}
                onChange={(e) => setSettings((s) => ({ ...s, audioThreshold: Number(e.target.value) }))}
              />
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-gray-400">모션 민감도 ({Math.round(settings.motionThreshold * 100)}%)</span>
              <input
                type="range" min="0.1" max="1" step="0.05"
                value={settings.motionThreshold}
                onChange={(e) => setSettings((s) => ({ ...s, motionThreshold: Number(e.target.value) }))}
              />
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-gray-400">클립 앞 여유 ({settings.clipPaddingBefore}초)</span>
              <input
                type="range" min="1" max="10" step="0.5"
                value={settings.clipPaddingBefore}
                onChange={(e) => setSettings((s) => ({ ...s, clipPaddingBefore: Number(e.target.value) }))}
              />
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-gray-400">클립 뒤 여유 ({settings.clipPaddingAfter}초)</span>
              <input
                type="range" min="1" max="10" step="0.5"
                value={settings.clipPaddingAfter}
                onChange={(e) => setSettings((s) => ({ ...s, clipPaddingAfter: Number(e.target.value) }))}
              />
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-gray-400">최소 클립 길이 ({settings.minClipDuration}초)</span>
              <input
                type="range" min="1" max="15" step="0.5"
                value={settings.minClipDuration}
                onChange={(e) => setSettings((s) => ({ ...s, minClipDuration: Number(e.target.value) }))}
              />
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-gray-400">병합 간격 ({settings.mergeGap}초)</span>
              <input
                type="range" min="0.5" max="10" step="0.5"
                value={settings.mergeGap}
                onChange={(e) => setSettings((s) => ({ ...s, mergeGap: Number(e.target.value) }))}
              />
            </label>
          </div>
        )}

        {/* Body */}
        <div className="flex-1 flex min-h-0">
          {/* Video Panel */}
          <div className="flex-1 flex flex-col p-4 min-w-0">
            {!videoSrc ? (
              <div
                className="flex-1 flex flex-col items-center justify-center border-2 border-dashed border-gray-600 rounded-xl cursor-pointer hover:border-blue-500 transition-colors"
                onClick={() => fileInputRef.current?.click()}
              >
                <div className="text-5xl mb-4">🎥</div>
                <p className="text-gray-400 text-lg">풋살 영상을 드래그하거나 클릭하여 선택</p>
                <p className="text-gray-500 text-sm mt-2">MP4, WebM, MOV 지원</p>
              </div>
            ) : (
              <>
                <div className="flex-1 flex items-center justify-center bg-black rounded-lg overflow-hidden min-h-0">
                  <video
                    ref={videoRef}
                    src={videoSrc}
                    className="max-w-full max-h-full"
                    controls
                    crossOrigin="anonymous"
                    onLoadedMetadata={() => setDuration(videoRef.current?.duration || 0)}
                    onTimeUpdate={() => setCurrentTime(videoRef.current?.currentTime || 0)}
                  />
                </div>

                {/* Timeline with highlight markers */}
                {duration > 0 && clips.length > 0 && (
                  <div className="mt-2 h-8 bg-gray-700 rounded relative overflow-hidden">
                    {clips.map((clip) => (
                      <div
                        key={clip.id}
                        className={`absolute top-0 h-full opacity-60 cursor-pointer hover:opacity-90 ${
                          clip.type === 'auto-audio'
                            ? 'bg-amber-500'
                            : clip.type === 'auto-motion'
                            ? 'bg-blue-500'
                            : 'bg-green-500'
                        }`}
                        style={{
                          left: `${(clip.startTime / duration) * 100}%`,
                          width: `${((clip.endTime - clip.startTime) / duration) * 100}%`,
                        }}
                        onClick={() => handlePlayClip(clip)}
                        title={clip.label}
                      />
                    ))}
                    {/* Current position indicator */}
                    <div
                      className="absolute top-0 w-0.5 h-full bg-white z-10"
                      style={{ left: `${(currentTime / duration) * 100}%` }}
                    />
                  </div>
                )}

                {/* Controls */}
                <div className="flex gap-2 mt-3">
                  <button
                    onClick={handleAnalyze}
                    disabled={isAnalyzing}
                    className="px-4 py-2 bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
                  >
                    {isAnalyzing ? phaseLabel[progress.phase] : '자동 분석 시작'}
                  </button>
                  <button
                    onClick={handleAddManualClip}
                    className="px-4 py-2 bg-green-600 rounded-lg hover:bg-green-700 font-medium"
                  >
                    현재 위치 마크
                  </button>
                  {clips.length > 0 && (
                    <button
                      onClick={handleExportClipList}
                      className="px-4 py-2 bg-purple-600 rounded-lg hover:bg-purple-700 font-medium"
                    >
                      클립 목록 내보내기
                    </button>
                  )}
                  <button
                    onClick={() => { fileInputRef.current?.click(); }}
                    className="px-4 py-2 bg-gray-700 rounded-lg hover:bg-gray-600"
                  >
                    다른 영상
                  </button>
                </div>

                {/* Progress bar */}
                {isAnalyzing && (
                  <div className="mt-2">
                    <div className="h-2 bg-gray-700 rounded overflow-hidden">
                      <div
                        className="h-full bg-blue-500 transition-all duration-300"
                        style={{ width: `${progress.percent}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-400 mt-1">{phaseLabel[progress.phase]} {progress.percent}%</p>
                  </div>
                )}
              </>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept="video/*"
              className="hidden"
              onChange={handleFileSelect}
            />
          </div>

          {/* Clip List Panel */}
          <div className="w-80 border-l border-gray-700 p-3 flex flex-col">
            <h3 className="text-sm font-semibold text-gray-300 mb-3">하이라이트 클립</h3>
            <HighlightClipList
              clips={clips}
              activeClipId={activeClipId}
              onPlayClip={handlePlayClip}
              onDeleteClip={handleDeleteClip}
              onRenameClip={handleRenameClip}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
