import type { GoalClip, GoalDetectionSettings, AnalysisProgress } from '../types';

const DEFAULT_GOAL_SETTINGS: GoalDetectionSettings = {
  spikeMultiplier: 2.5,
  sustainMultiplier: 1.5,
  minSustainSeconds: 2.0,
  cooldownSeconds: 30,
  clipPaddingBefore: 12,
  clipPaddingAfter: 8,
  playbackRate: 16,
};

let idCounter = 0;
function genClipId(): string {
  return `goal-${Date.now()}-${idCounter++}`;
}

interface EnergySample {
  videoTime: number;
  energy: number;
}

/**
 * Stream audio from video using AnalyserNode at accelerated playback.
 * Memory-safe: never loads entire file into memory.
 */
async function collectAudioEnergy(
  file: File,
  settings: GoalDetectionSettings,
  onProgress: (p: AnalysisProgress) => void,
  abortSignal?: AbortSignal,
): Promise<{ samples: EnergySample[]; duration: number }> {
  const blobUrl = URL.createObjectURL(file);
  const video = document.createElement('video');
  video.src = blobUrl;
  video.muted = true;
  video.preload = 'auto';

  await new Promise<void>((resolve, reject) => {
    video.onloadedmetadata = () => resolve();
    video.onerror = () => reject(new Error('영상을 로드할 수 없습니다'));
  });

  const duration = video.duration;
  const samples: EnergySample[] = [];

  const audioCtx = new AudioContext();
  const source = audioCtx.createMediaElementSource(video);
  const analyser = audioCtx.createAnalyser();
  analyser.fftSize = 2048;
  const gain = audioCtx.createGain();
  gain.gain.value = 0;

  source.connect(analyser);
  analyser.connect(gain);
  gain.connect(audioCtx.destination);

  const dataArray = new Uint8Array(analyser.fftSize);
  let currentRate = settings.playbackRate;
  video.playbackRate = currentRate;

  // Unmute to allow audio processing (gain is 0 so no sound)
  video.muted = false;

  await video.play();

  return new Promise((resolve, reject) => {
    let lastTime = -1;
    let stallCount = 0;

    const interval = setInterval(() => {
      if (abortSignal?.aborted) {
        cleanup();
        reject(new Error('분석이 취소되었습니다'));
        return;
      }

      const videoTime = video.currentTime;

      // Detect stalling and reduce playback rate
      if (Math.abs(videoTime - lastTime) < 0.01) {
        stallCount++;
        if (stallCount > 10 && currentRate > 4) {
          currentRate = Math.max(4, currentRate / 2);
          video.playbackRate = currentRate;
          stallCount = 0;
        }
      } else {
        stallCount = 0;
      }
      lastTime = videoTime;

      // Collect RMS energy from analyser
      analyser.getByteTimeDomainData(dataArray);
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        const normalized = dataArray[i] / 128 - 1;
        sum += normalized * normalized;
      }
      const rms = Math.sqrt(sum / dataArray.length);

      samples.push({ videoTime, energy: rms });

      onProgress({
        phase: 'scanning-audio',
        percent: Math.round((videoTime / duration) * 80),
        currentTime: videoTime,
        totalDuration: duration,
      });

      if (video.ended || videoTime >= duration - 0.5) {
        cleanup();
        resolve({ samples, duration });
      }
    }, 50);

    function cleanup() {
      clearInterval(interval);
      video.pause();
      source.disconnect();
      analyser.disconnect();
      gain.disconnect();
      audioCtx.close();
      URL.revokeObjectURL(blobUrl);
      video.remove();
    }

    video.onended = () => {
      cleanup();
      resolve({ samples, duration });
    };
  });
}

/**
 * Detect goals using burst+sustain pattern on collected energy data.
 */
function detectGoals(
  samples: EnergySample[],
  duration: number,
  settings: GoalDetectionSettings,
): GoalClip[] {
  if (samples.length === 0) return [];

  // Estimate sample interval from collected data
  const avgInterval = samples.length > 1
    ? (samples[samples.length - 1].videoTime - samples[0].videoTime) / (samples.length - 1)
    : 0.8;

  // Rolling baseline window: 30 seconds of video time
  const windowSamples = Math.max(1, Math.floor(30 / avgInterval));
  const halfWindow = Math.floor(windowSamples / 2);

  const goals: GoalClip[] = [];
  const cooldownSamples = Math.floor(settings.cooldownSeconds / avgInterval);
  const sustainSamples = Math.max(1, Math.floor(settings.minSustainSeconds / avgInterval));

  let i = 0;
  let goalNumber = 1;

  while (i < samples.length) {
    // Compute rolling median baseline
    const windowStart = Math.max(0, i - halfWindow);
    const windowEnd = Math.min(samples.length, i + halfWindow);
    const windowEnergies = samples.slice(windowStart, windowEnd).map((s) => s.energy);
    windowEnergies.sort((a, b) => a - b);
    const baseline = windowEnergies[Math.floor(windowEnergies.length / 2)] || 0.001;

    const currentEnergy = samples[i].energy;

    // Check spike
    if (currentEnergy > baseline * settings.spikeMultiplier) {
      // Verify sustained duration
      let sustainEnd = i;
      while (
        sustainEnd < samples.length &&
        samples[sustainEnd].energy > baseline * settings.sustainMultiplier
      ) {
        sustainEnd++;
      }

      const sustainDuration = sustainEnd > i
        ? samples[Math.min(sustainEnd, samples.length - 1)].videoTime - samples[i].videoTime
        : 0;

      if (sustainDuration >= settings.minSustainSeconds) {
        // Goal detected
        const detectedTime = samples[i].videoTime;
        const peakEnergy = Math.max(
          ...samples.slice(i, sustainEnd).map((s) => s.energy),
        );
        const confidence = Math.min(
          1,
          Math.max(0, (peakEnergy / baseline - settings.spikeMultiplier) / settings.spikeMultiplier),
        );

        goals.push({
          id: genClipId(),
          goalNumber,
          startTime: Math.max(0, detectedTime - settings.clipPaddingBefore),
          endTime: Math.min(duration, detectedTime + settings.clipPaddingAfter),
          detectedTime,
          label: `${goalNumber}골 (${formatTime(detectedTime)})`,
          type: 'auto-goal',
          confidence,
        });

        goalNumber++;
        i = sustainEnd + cooldownSamples;
        continue;
      }
    }

    i++;
  }

  return goals;
}

/**
 * Main entry point: analyze video file for goals.
 */
export async function analyzeGoals(
  file: File,
  settings: Partial<GoalDetectionSettings> = {},
  onProgress: (p: AnalysisProgress) => void,
  abortSignal?: AbortSignal,
): Promise<GoalClip[]> {
  const s = { ...DEFAULT_GOAL_SETTINGS, ...settings };

  // Phase 1: Stream audio and collect energy (0-80%)
  const { samples, duration } = await collectAudioEnergy(file, s, onProgress, abortSignal);

  // Phase 2: Detect goals from energy data (80-90%)
  onProgress({ phase: 'detecting-goals', percent: 85 });
  const goals = detectGoals(samples, duration, s);

  // Phase 3: Generate thumbnails (90-100%)
  if (goals.length > 0) {
    onProgress({ phase: 'generating-thumbnails', percent: 90 });
    const thumbVideo = document.createElement('video');
    thumbVideo.src = URL.createObjectURL(file);
    thumbVideo.preload = 'auto';
    thumbVideo.crossOrigin = 'anonymous';

    await new Promise<void>((resolve) => {
      thumbVideo.onloadedmetadata = () => resolve();
    });

    for (let idx = 0; idx < goals.length; idx++) {
      if (abortSignal?.aborted) break;
      goals[idx].thumbnail = await captureThumbnail(thumbVideo, goals[idx].detectedTime);
      onProgress({
        phase: 'generating-thumbnails',
        percent: 90 + Math.round((idx / goals.length) * 10),
      });
    }

    URL.revokeObjectURL(thumbVideo.src);
    thumbVideo.remove();
  }

  onProgress({ phase: 'done', percent: 100 });
  return goals;
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
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export function getDefaultGoalSettings(): GoalDetectionSettings {
  return { ...DEFAULT_GOAL_SETTINGS };
}
