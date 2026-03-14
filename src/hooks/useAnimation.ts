import { useState, useRef, useCallback } from 'react';
import type { Position3D, Phase, Player } from '../types';

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

function lerpPosition(a: Position3D, b: Position3D, t: number): Position3D {
  return {
    x: lerp(a.x, b.x, t),
    y: lerp(a.y, b.y, t),
    z: lerp(a.z, b.z, t),
  };
}

// Parabolic interpolation for ball height (natural arc)
function lerpBallPosition(a: Position3D, b: Position3D, t: number): Position3D {
  const baseY = lerp(a.y, b.y, t);
  // Add arc if ball changes height
  const maxHeight = Math.max(a.y, b.y);
  const arc = maxHeight > 0.5 ? Math.sin(t * Math.PI) * maxHeight * 0.3 : 0;
  return {
    x: lerp(a.x, b.x, t),
    y: baseY + arc,
    z: lerp(a.z, b.z, t),
  };
}

export interface AnimationState {
  isPlaying: boolean;
  currentPhaseIndex: number;
  currentFrameIndex: number;
  progress: number; // 0 to 1 between frames
  interpolatedPlayers: Player[];
  interpolatedBall: Position3D;
  runningPlayerIds: Set<string>;
}

export function useAnimation(phases: Phase[]) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [playAll, setPlayAll] = useState(false);
  const [currentPhaseIndex, setCurrentPhaseIndex] = useState(0);
  const [currentFrameIndex, setCurrentFrameIndex] = useState(0);
  const [progress, setProgress] = useState(0);
  const [speed, setSpeed] = useState(1);
  const animationRef = useRef<number | null>(null);
  const lastTimeRef = useRef<number>(0);

  const currentPhase = phases[currentPhaseIndex];
  const frames = currentPhase?.frames || [];

  const getInterpolatedState = useCallback(
    (phaseIdx: number, frameIdx: number, t: number) => {
      const phase = phases[phaseIdx];
      if (!phase || phase.frames.length === 0) {
        return { players: [], ball: { x: 0, y: 0.22, z: 0 }, runningIds: new Set<string>() };
      }

      const currentFrame = phase.frames[frameIdx];
      const nextFrame = phase.frames[frameIdx + 1];

      if (!nextFrame || t === 0) {
        return {
          players: currentFrame.players,
          ball: currentFrame.ballPosition,
          runningIds: new Set<string>(),
        };
      }

      const runningIds = new Set<string>();
      const players = currentFrame.players.map((player) => {
        const nextPlayer = nextFrame.players.find((p) => p.id === player.id);
        if (!nextPlayer) return player;

        const dx = nextPlayer.position.x - player.position.x;
        const dz = nextPlayer.position.z - player.position.z;
        if (Math.abs(dx) > 0.1 || Math.abs(dz) > 0.1) {
          runningIds.add(player.id);
        }

        return {
          ...player,
          position: lerpPosition(player.position, nextPlayer.position, t),
        };
      });

      return {
        players,
        ball: lerpBallPosition(currentFrame.ballPosition, nextFrame.ballPosition, t),
        runningIds,
      };
    },
    [phases]
  );

  const stop = useCallback(() => {
    setIsPlaying(false);
    setPlayAll(false);
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    }
  }, []);

  const animate = useCallback(
    (timestamp: number) => {
      if (!lastTimeRef.current) lastTimeRef.current = timestamp;
      const delta = (timestamp - lastTimeRef.current) / 1000;
      lastTimeRef.current = timestamp;

      setProgress((prev) => {
        const newProgress = prev + delta * speed * 0.5;
        if (newProgress >= 1) {
          // Move to next frame
          setCurrentFrameIndex((prevFrame) => {
            const phase = phases[currentPhaseIndex];
            if (!phase) return prevFrame;

            if (prevFrame + 1 >= phase.frames.length - 1) {
              // End of phase
              if (playAll) {
                setCurrentPhaseIndex((prevPhase) => {
                  if (prevPhase + 1 >= phases.length) {
                    stop();
                    return prevPhase;
                  }
                  return prevPhase + 1;
                });
                return 0;
              } else {
                stop();
                return prevFrame;
              }
            }
            return prevFrame + 1;
          });
          return 0;
        }
        return newProgress;
      });

      animationRef.current = requestAnimationFrame(animate);
    },
    [speed, phases, currentPhaseIndex, playAll, stop]
  );

  const play = useCallback(
    (allPhases = false) => {
      if (frames.length < 2) return;
      setPlayAll(allPhases);
      setIsPlaying(true);
      setProgress(0);
      lastTimeRef.current = 0;
      if (allPhases) {
        setCurrentPhaseIndex(0);
        setCurrentFrameIndex(0);
      }
      animationRef.current = requestAnimationFrame(animate);
    },
    [frames.length, animate]
  );

  const goToFrame = useCallback((phaseIdx: number, frameIdx: number) => {
    stop();
    setCurrentPhaseIndex(phaseIdx);
    setCurrentFrameIndex(frameIdx);
    setProgress(0);
  }, [stop]);

  const state = getInterpolatedState(currentPhaseIndex, currentFrameIndex, isPlaying ? progress : 0);

  return {
    isPlaying,
    currentPhaseIndex,
    currentFrameIndex,
    progress,
    interpolatedPlayers: state.players,
    interpolatedBall: state.ball,
    runningPlayerIds: state.runningIds,
    speed,
    setSpeed,
    play,
    stop,
    goToFrame,
    setCurrentPhaseIndex,
    setCurrentFrameIndex,
  };
}
