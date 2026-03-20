import { useState, useRef, useCallback, useEffect } from 'react';
import type { GoalClip, GoalDetectionSettings, AnalysisProgress } from '../../types';
import { analyzeGoals, getDefaultGoalSettings, formatTime } from '../../utils/highlightDetector';
import { generateId } from '../../utils/storage';
import HighlightClipList from './HighlightClipList';

interface Props {
  onClose: () => void;
}

export default function HighlightGenerator({ onClose }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoSrc, setVideoSrc] = useState<string | null>(null);
  const [videoName, setVideoName] = useState('');
  const [clips, setClips] = useState<GoalClip[]>([]);
  const [activeClipId, setActiveClipId] = useState<string | null>(null);
  const [progress, setProgress] = useState<AnalysisProgress>({ phase: 'idle', percent: 0 });
  const [settings, setSettings] = useState<GoalDetectionSettings>(getDefaultGoalSettings);
  const [showSettings, setShowSettings] = useState(false);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);

  const isAnalyzing = progress.phase !== 'idle' && progress.phase !== 'done';

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (videoSrc) URL.revokeObjectURL(videoSrc);
    const url = URL.createObjectURL(file);
    setVideoFile(file);
    setVideoSrc(url);
    setVideoName(file.name);
    setClips([]);
    setActiveClipId(null);
    setProgress({ phase: 'idle', percent: 0 });
  }, [videoSrc]);

  const handleAnalyze = useCallback(async () => {
    if (!videoFile) return;

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const detectedClips = await analyzeGoals(
        videoFile,
        settings,
        setProgress,
        controller.signal,
      );
      setClips(detectedClips);
    } catch (err) {
      if ((err as Error).message !== '분석이 취소되었습니다') {
        console.error('Goal detection failed:', err);
      }
      setProgress({ phase: 'idle', percent: 0 });
    } finally {
      abortControllerRef.current = null;
    }
  }, [videoFile, settings]);

  const handleCancel = useCallback(() => {
    abortControllerRef.current?.abort();
    setProgress({ phase: 'idle', percent: 0 });
  }, []);

  const handlePlayClip = useCallback((clip: GoalClip) => {
    const video = videoRef.current;
    if (!video) return;
    setActiveClipId(clip.id);
    video.currentTime = clip.startTime;
    video.play();
  }, []);

  const handleDeleteClip = useCallback((id: string) => {
    setClips((prev) => {
      const filtered = prev.filter((c) => c.id !== id);
      return filtered.map((c, i) => ({ ...c, goalNumber: i + 1, label: `${i + 1}골 (${formatTime(c.detectedTime)})` }));
    });
    if (activeClipId === id) setActiveClipId(null);
  }, [activeClipId]);

  const handleRenameClip = useCallback((id: string, label: string) => {
    setClips((prev) => prev.map((c) => (c.id === id ? { ...c, label } : c)));
  }, []);

  const handleAddManualClip = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;
    const time = video.currentTime;
    const nextNumber = clips.length + 1;
    const newClip: GoalClip = {
      id: generateId(),
      goalNumber: nextNumber,
      startTime: Math.max(0, time - settings.clipPaddingBefore),
      endTime: Math.min(video.duration, time + settings.clipPaddingAfter),
      detectedTime: time,
      label: `${nextNumber}골 (${formatTime(time)})`,
      type: 'manual',
      confidence: 1,
    };
    setClips((prev) => [...prev, newClip].sort((a, b) => a.startTime - b.startTime));
  }, [clips.length, settings.clipPaddingBefore, settings.clipPaddingAfter]);

  const handleExportClipList = useCallback(() => {
    const data = clips.map((c) => ({
      goalNumber: c.goalNumber,
      label: c.label,
      start: formatTime(c.startTime),
      end: formatTime(c.endTime),
      detectedAt: formatTime(c.detectedTime),
      startSec: c.startTime.toFixed(1),
      endSec: c.endTime.toFixed(1),
      type: c.type,
      confidence: Math.round(c.confidence * 100) + '%',
    }));
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `goals-${videoName || 'video'}.json`;
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
    'scanning-audio': '오디오 스캔 중...',
    'detecting-goals': '골 감지 중...',
    'generating-thumbnails': '썸네일 생성 중...',
    done: '감지 완료!',
  };

  // Sensitivity display: lower spikeMultiplier = more sensitive
  const sensitivityPercent = Math.round(((4 - settings.spikeMultiplier) / 2.5) * 100);

  return (
    <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center">
      <div className="bg-gray-800 rounded-xl shadow-2xl w-[95vw] max-w-6xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700">
          <h2 className="text-lg font-bold">골 하이라이트 생성기</h2>
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
          <div className="px-4 py-3 border-b border-gray-700 bg-gray-750 grid grid-cols-2 gap-4 text-sm">
            <label className="flex flex-col gap-1">
              <span className="text-gray-400">감지 민감도 ({sensitivityPercent}%)</span>
              <input
                type="range" min="1.5" max="4" step="0.1"
                value={settings.spikeMultiplier}
                onChange={(e) => setSettings((s) => ({ ...s, spikeMultiplier: Number(e.target.value) }))}
              />
              <span className="text-[10px] text-gray-500">낮은 값 = 더 민감 (오탐 증가)</span>
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-gray-400">최소 지속 시간 ({settings.minSustainSeconds}초)</span>
              <input
                type="range" min="1" max="5" step="0.5"
                value={settings.minSustainSeconds}
                onChange={(e) => setSettings((s) => ({ ...s, minSustainSeconds: Number(e.target.value) }))}
              />
              <span className="text-[10px] text-gray-500">환호가 유지되어야 하는 최소 시간</span>
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-gray-400">클립 앞 여유 ({settings.clipPaddingBefore}초)</span>
              <input
                type="range" min="5" max="20" step="1"
                value={settings.clipPaddingBefore}
                onChange={(e) => setSettings((s) => ({ ...s, clipPaddingBefore: Number(e.target.value) }))}
              />
              <span className="text-[10px] text-gray-500">골 전 빌드업 시간</span>
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-gray-400">클립 뒤 여유 ({settings.clipPaddingAfter}초)</span>
              <input
                type="range" min="3" max="15" step="1"
                value={settings.clipPaddingAfter}
                onChange={(e) => setSettings((s) => ({ ...s, clipPaddingAfter: Number(e.target.value) }))}
              />
              <span className="text-[10px] text-gray-500">골 후 세레머니 시간</span>
            </label>
          </div>
        )}

        {/* Body */}
        <div className="flex-1 flex min-h-0">
          {/* Video Panel */}
          <div className="flex-1 flex flex-col p-4 min-w-0">
            {!videoSrc ? (
              <div
                className="flex-1 flex flex-col items-center justify-center border-2 border-dashed border-gray-600 rounded-xl cursor-pointer hover:border-red-500 transition-colors"
                onClick={() => fileInputRef.current?.click()}
              >
                <div className="text-5xl mb-4">⚽</div>
                <p className="text-gray-400 text-lg">풋살 영상을 클릭하여 선택</p>
                <p className="text-gray-500 text-sm mt-2">MP4, WebM, MOV 지원 (긴 영상 OK)</p>
              </div>
            ) : (
              <>
                <div className="flex-1 flex items-center justify-center bg-black rounded-lg overflow-hidden min-h-0">
                  <video
                    ref={videoRef}
                    src={videoSrc}
                    className="max-w-full max-h-full"
                    controls
                    onLoadedMetadata={() => setDuration(videoRef.current?.duration || 0)}
                    onTimeUpdate={() => setCurrentTime(videoRef.current?.currentTime || 0)}
                  />
                </div>

                {/* Timeline with goal markers */}
                {duration > 0 && clips.length > 0 && (
                  <div className="mt-2 h-10 bg-gray-700 rounded relative overflow-hidden">
                    {clips.map((clip) => (
                      <div
                        key={clip.id}
                        className={`absolute top-0 h-full cursor-pointer transition-opacity ${
                          activeClipId === clip.id ? 'opacity-90 bg-red-500' : 'opacity-50 bg-red-600 hover:opacity-80'
                        }`}
                        style={{
                          left: `${(clip.startTime / duration) * 100}%`,
                          width: `${Math.max(0.5, ((clip.endTime - clip.startTime) / duration) * 100)}%`,
                        }}
                        onClick={() => handlePlayClip(clip)}
                        title={clip.label}
                      >
                        <span className="absolute inset-0 flex items-center justify-center text-[10px] font-bold text-white">
                          {clip.goalNumber}골
                        </span>
                      </div>
                    ))}
                    <div
                      className="absolute top-0 w-0.5 h-full bg-white z-10"
                      style={{ left: `${(currentTime / duration) * 100}%` }}
                    />
                  </div>
                )}

                {/* Controls */}
                <div className="flex gap-2 mt-3 flex-wrap">
                  {isAnalyzing ? (
                    <button
                      onClick={handleCancel}
                      className="px-4 py-2 bg-red-700 rounded-lg hover:bg-red-800 font-medium"
                    >
                      분석 취소
                    </button>
                  ) : (
                    <button
                      onClick={handleAnalyze}
                      className="px-4 py-2 bg-red-600 rounded-lg hover:bg-red-700 font-medium"
                    >
                      골 감지 시작
                    </button>
                  )}
                  <button
                    onClick={handleAddManualClip}
                    disabled={isAnalyzing}
                    className="px-4 py-2 bg-green-600 rounded-lg hover:bg-green-700 font-medium disabled:opacity-50"
                  >
                    현재 위치 골 마크
                  </button>
                  {clips.length > 0 && (
                    <button
                      onClick={handleExportClipList}
                      className="px-4 py-2 bg-purple-600 rounded-lg hover:bg-purple-700 font-medium"
                    >
                      골 목록 내보내기
                    </button>
                  )}
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isAnalyzing}
                    className="px-4 py-2 bg-gray-700 rounded-lg hover:bg-gray-600 disabled:opacity-50"
                  >
                    다른 영상
                  </button>
                </div>

                {/* Progress bar */}
                {isAnalyzing && (
                  <div className="mt-2">
                    <div className="h-2 bg-gray-700 rounded overflow-hidden">
                      <div
                        className="h-full bg-red-500 transition-all duration-300"
                        style={{ width: `${progress.percent}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-400 mt-1">
                      {phaseLabel[progress.phase]} {progress.percent}%
                      {progress.currentTime != null && progress.totalDuration != null && (
                        <span className="ml-2">
                          ({formatTime(progress.currentTime)} / {formatTime(progress.totalDuration)})
                        </span>
                      )}
                    </p>
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
            <h3 className="text-sm font-semibold text-gray-300 mb-3">
              감지된 골 {clips.length > 0 && `(${clips.length})`}
            </h3>
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
