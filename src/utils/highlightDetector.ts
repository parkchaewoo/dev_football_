import type { HighlightClip, HighlightSettings, AnalysisProgress } from '../types';

const DEFAULT_SETTINGS: HighlightSettings = {
  audioThreshold: 0.6,
  motionThreshold: 0.4,
  clipPaddingBefore: 3,
  clipPaddingAfter: 4,
  minClipDuration: 3,
  mergeGap: 2,
};

let idCounter = 0;
function genClipId(): string {
  return `clip-${Date.now()}-${idCounter++}`;
}

/**
 * Analyze audio track for volume spikes (cheering, whistles, etc.)
 */
export async function analyzeAudio(
  videoEl: HTMLVideoElement,
  settings: HighlightSettings,
  onProgress: (p: AnalysisProgress) => void,
): Promise<HighlightClip[]> {
  onProgress({ phase: 'analyzing-audio', percent: 0 });

  const audioCtx = new AudioContext();
  const response = await fetch(videoEl.src);
  const arrayBuffer = await response.arrayBuffer();

  onProgress({ phase: 'analyzing-audio', percent: 20 });

  const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
  const rawData = audioBuffer.getChannelData(0);
  const sampleRate = audioBuffer.sampleRate;
  const duration = audioBuffer.duration;

  // Downsample: compute RMS energy per 0.25s window
  const windowSize = Math.floor(sampleRate * 0.25);
  const energies: number[] = [];

  for (let i = 0; i < rawData.length; i += windowSize) {
    let sum = 0;
    const end = Math.min(i + windowSize, rawData.length);
    for (let j = i; j < end; j++) {
      sum += rawData[j] * rawData[j];
    }
    energies.push(Math.sqrt(sum / (end - i)));
  }

  onProgress({ phase: 'analyzing-audio', percent: 60 });

  // Normalize energies
  const maxEnergy = Math.max(...energies, 0.001);
  const normalized = energies.map((e) => e / maxEnergy);

  // Find spikes above threshold
  const clips: HighlightClip[] = [];
  const threshold = settings.audioThreshold;

  for (let i = 0; i < normalized.length; i++) {
    if (normalized[i] >= threshold) {
      const time = (i * windowSize) / sampleRate;
      const startTime = Math.max(0, time - settings.clipPaddingBefore);
      const endTime = Math.min(duration, time + settings.clipPaddingAfter);

      clips.push({
        id: genClipId(),
        startTime,
        endTime,
        label: `오디오 감지 ${formatTime(time)}`,
        type: 'auto-audio',
        confidence: normalized[i],
      });
    }
  }

  onProgress({ phase: 'analyzing-audio', percent: 100 });
  audioCtx.close();

  return mergeOverlappingClips(clips, settings.mergeGap);
}

/**
 * Analyze video frames for sudden scene changes / motion bursts.
 * Compares consecutive frames using pixel difference.
 */
export async function analyzeMotion(
  videoEl: HTMLVideoElement,
  settings: HighlightSettings,
  onProgress: (p: AnalysisProgress) => void,
): Promise<HighlightClip[]> {
  onProgress({ phase: 'analyzing-video', percent: 0 });

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d', { willReadFrequently: true })!;
  const sampleWidth = 160;
  const sampleHeight = 90;
  canvas.width = sampleWidth;
  canvas.height = sampleHeight;

  const duration = videoEl.duration;
  const sampleInterval = 0.5; // sample every 0.5 seconds
  const totalSamples = Math.floor(duration / sampleInterval);

  let prevData: Uint8ClampedArray | null = null;
  const diffs: { time: number; diff: number }[] = [];

  for (let i = 0; i <= totalSamples; i++) {
    const time = i * sampleInterval;
    await seekTo(videoEl, time);

    ctx.drawImage(videoEl, 0, 0, sampleWidth, sampleHeight);
    const imageData = ctx.getImageData(0, 0, sampleWidth, sampleHeight);
    const data = imageData.data;

    if (prevData) {
      let totalDiff = 0;
      for (let p = 0; p < data.length; p += 4) {
        const dr = Math.abs(data[p] - prevData[p]);
        const dg = Math.abs(data[p + 1] - prevData[p + 1]);
        const db = Math.abs(data[p + 2] - prevData[p + 2]);
        totalDiff += (dr + dg + db) / 3;
      }
      const avgDiff = totalDiff / (sampleWidth * sampleHeight) / 255;
      diffs.push({ time, diff: avgDiff });
    }

    prevData = new Uint8ClampedArray(data);

    if (i % 10 === 0) {
      onProgress({ phase: 'analyzing-video', percent: Math.round((i / totalSamples) * 100) });
    }
  }

  // Normalize and find spikes
  const maxDiff = Math.max(...diffs.map((d) => d.diff), 0.001);
  const threshold = settings.motionThreshold;

  const clips: HighlightClip[] = [];
  for (const { time, diff } of diffs) {
    const normalized = diff / maxDiff;
    if (normalized >= threshold) {
      clips.push({
        id: genClipId(),
        startTime: Math.max(0, time - settings.clipPaddingBefore),
        endTime: Math.min(duration, time + settings.clipPaddingAfter),
        label: `장면 변화 ${formatTime(time)}`,
        type: 'auto-motion',
        confidence: normalized,
      });
    }
  }

  onProgress({ phase: 'analyzing-video', percent: 100 });
  return mergeOverlappingClips(clips, settings.mergeGap);
}

/**
 * Full analysis: audio + motion combined
 */
export async function analyzeVideo(
  videoEl: HTMLVideoElement,
  settings: Partial<HighlightSettings> = {},
  onProgress: (p: AnalysisProgress) => void,
): Promise<HighlightClip[]> {
  const s = { ...DEFAULT_SETTINGS, ...settings };

  const audioClips = await analyzeAudio(videoEl, s, onProgress);
  const motionClips = await analyzeMotion(videoEl, s, onProgress);

  onProgress({ phase: 'merging', percent: 50 });

  const allClips = [...audioClips, ...motionClips];
  const merged = mergeOverlappingClips(allClips, s.mergeGap);

  // Filter by minimum duration
  const filtered = merged.filter((c) => c.endTime - c.startTime >= s.minClipDuration);

  // Generate thumbnails
  for (const clip of filtered) {
    const midTime = (clip.startTime + clip.endTime) / 2;
    clip.thumbnail = await captureThumbnail(videoEl, midTime);
  }

  onProgress({ phase: 'done', percent: 100 });
  return filtered;
}

function mergeOverlappingClips(clips: HighlightClip[], mergeGap: number): HighlightClip[] {
  if (clips.length === 0) return [];

  const sorted = [...clips].sort((a, b) => a.startTime - b.startTime);
  const merged: HighlightClip[] = [sorted[0]];

  for (let i = 1; i < sorted.length; i++) {
    const last = merged[merged.length - 1];
    const current = sorted[i];

    if (current.startTime <= last.endTime + mergeGap) {
      // Merge
      last.endTime = Math.max(last.endTime, current.endTime);
      last.confidence = Math.max(last.confidence, current.confidence);
      if (last.type !== current.type) {
        last.label = `하이라이트 ${formatTime(last.startTime)}`;
      }
    } else {
      merged.push({ ...current });
    }
  }

  return merged;
}

function seekTo(video: HTMLVideoElement, time: number): Promise<void> {
  return new Promise((resolve) => {
    video.currentTime = time;
    video.addEventListener('seeked', () => resolve(), { once: true });
  });
}

async function captureThumbnail(video: HTMLVideoElement, time: number): Promise<string> {
  await seekTo(video, time);
  const canvas = document.createElement('canvas');
  canvas.width = 320;
  canvas.height = 180;
  const ctx = canvas.getContext('2d')!;
  ctx.drawImage(video, 0, 0, 320, 180);
  return canvas.toDataURL('image/jpeg', 0.7);
}

export function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export function getDefaultSettings(): HighlightSettings {
  return { ...DEFAULT_SETTINGS };
}
