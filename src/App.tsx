import { useState, useCallback } from 'react';
import TacticalBoard3D from './components/Board/TacticalBoard3D';
import PhasePanel from './components/Animation/PhasePanel';
import Timeline from './components/Animation/Timeline';
import PlaybackControls from './components/Animation/PlaybackControls';
import BallHeightSlider from './components/Controls/BallHeightSlider';
import ChatRoom from './components/Chat/ChatRoom';
import StrategyList from './components/Strategy/StrategyList';
import StrategyForm from './components/Strategy/StrategyForm';
import HighlightGenerator from './components/Highlight/HighlightGenerator';
import { useAnimation } from './hooks/useAnimation';
import type { Player, Phase, Frame, Strategy } from './types';
import { generateId, saveStrategy } from './utils/storage';
import { HALF_LENGTH } from './components/Board/FutsalCourt3D';

function createDefaultPlayers(): Player[] {
  const home: Player[] = [
    { id: 'h1', team: 'home', number: 1, position: { x: -HALF_LENGTH + 1, y: 0, z: 0 } },
    { id: 'h2', team: 'home', number: 2, position: { x: -HALF_LENGTH + 6, y: 0, z: -6 } },
    { id: 'h3', team: 'home', number: 3, position: { x: -HALF_LENGTH + 6, y: 0, z: 6 } },
    { id: 'h4', team: 'home', number: 4, position: { x: -HALF_LENGTH + 12, y: 0, z: -3 } },
    { id: 'h5', team: 'home', number: 5, position: { x: -HALF_LENGTH + 12, y: 0, z: 3 } },
  ];
  const away: Player[] = [
    { id: 'a1', team: 'away', number: 1, position: { x: HALF_LENGTH - 1, y: 0, z: 0 } },
    { id: 'a2', team: 'away', number: 2, position: { x: HALF_LENGTH - 6, y: 0, z: -6 } },
    { id: 'a3', team: 'away', number: 3, position: { x: HALF_LENGTH - 6, y: 0, z: 6 } },
    { id: 'a4', team: 'away', number: 4, position: { x: HALF_LENGTH - 12, y: 0, z: -3 } },
    { id: 'a5', team: 'away', number: 5, position: { x: HALF_LENGTH - 12, y: 0, z: 3 } },
  ];
  return [...home, ...away];
}

function createDefaultPhase(): Phase {
  return {
    id: generateId(),
    name: '1단계',
    description: '',
    frames: [
      {
        id: generateId(),
        players: createDefaultPlayers(),
        ballPosition: { x: 0, y: 0.22, z: 0 },
      },
    ],
    order: 0,
  };
}

export default function App() {
  const [strategyId, setStrategyId] = useState(generateId());
  const [strategyName, setStrategyName] = useState('');
  const [phases, setPhases] = useState<Phase[]>([createDefaultPhase()]);
  const [currentPhaseIndex, setCurrentPhaseIndex] = useState(0);
  const [currentFrameIndex, setCurrentFrameIndex] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [showSaveForm, setShowSaveForm] = useState(false);
  const [showLoadList, setShowLoadList] = useState(false);
  const [showChat, setShowChat] = useState(true);
  const [showHighlight, setShowHighlight] = useState(false);

  const animation = useAnimation(phases);

  const currentPhase = phases[currentPhaseIndex];
  const currentFrame = currentPhase?.frames[currentFrameIndex];
  const players = currentFrame?.players || [];
  const ballPosition = currentFrame?.ballPosition || { x: 0, y: 0.22, z: 0 };

  const updateCurrentFrame = useCallback(
    (updater: (frame: Frame) => Frame) => {
      setPhases((prev) => {
        const next = [...prev];
        const phase = { ...next[currentPhaseIndex] };
        const frames = [...phase.frames];
        frames[currentFrameIndex] = updater(frames[currentFrameIndex]);
        phase.frames = frames;
        next[currentPhaseIndex] = phase;
        return next;
      });
    },
    [currentPhaseIndex, currentFrameIndex]
  );

  const handleMovePlayer = useCallback(
    (id: string, x: number, z: number) => {
      updateCurrentFrame((frame) => ({
        ...frame,
        players: frame.players.map((p) =>
          p.id === id ? { ...p, position: { ...p.position, x, z } } : p
        ),
      }));
    },
    [updateCurrentFrame]
  );

  const handleMoveBall = useCallback(
    (x: number, z: number) => {
      updateCurrentFrame((frame) => ({
        ...frame,
        ballPosition: { ...frame.ballPosition, x, z },
      }));
    },
    [updateCurrentFrame]
  );

  const handleBallHeight = useCallback(
    (height: number) => {
      updateCurrentFrame((frame) => ({
        ...frame,
        ballPosition: { ...frame.ballPosition, y: height },
      }));
    },
    [updateCurrentFrame]
  );

  const addFrame = useCallback(() => {
    const phase = phases[currentPhaseIndex];
    if (!phase) return;
    const lastFrame = phase.frames[phase.frames.length - 1];
    const newFrame: Frame = {
      id: generateId(),
      players: lastFrame.players.map((p) => ({ ...p, position: { ...p.position } })),
      ballPosition: { ...lastFrame.ballPosition },
    };
    setPhases((prev) => {
      const next = [...prev];
      const ph = { ...next[currentPhaseIndex] };
      ph.frames = [...ph.frames, newFrame];
      next[currentPhaseIndex] = ph;
      return next;
    });
    setCurrentFrameIndex(phase.frames.length);
  }, [currentPhaseIndex, phases]);

  const deleteFrame = useCallback(
    (index: number) => {
      setPhases((prev) => {
        const next = [...prev];
        const phase = { ...next[currentPhaseIndex] };
        if (phase.frames.length <= 1) return prev;
        phase.frames = phase.frames.filter((_, i) => i !== index);
        next[currentPhaseIndex] = phase;
        return next;
      });
      setCurrentFrameIndex((prev) => Math.max(0, Math.min(prev, phases[currentPhaseIndex].frames.length - 2)));
    },
    [currentPhaseIndex, phases]
  );

  const addPhase = useCallback(() => {
    const lastPhase = phases[phases.length - 1];
    const lastFrame = lastPhase.frames[lastPhase.frames.length - 1];
    const newPhase: Phase = {
      id: generateId(),
      name: `${phases.length + 1}단계`,
      description: '',
      frames: [
        {
          id: generateId(),
          players: lastFrame.players.map((p) => ({ ...p, position: { ...p.position } })),
          ballPosition: { ...lastFrame.ballPosition },
        },
      ],
      order: phases.length,
    };
    setPhases((prev) => [...prev, newPhase]);
    setCurrentPhaseIndex(phases.length);
    setCurrentFrameIndex(0);
  }, [phases]);

  const deletePhase = useCallback(
    (index: number) => {
      if (phases.length <= 1) return;
      setPhases((prev) => prev.filter((_, i) => i !== index));
      setCurrentPhaseIndex((prev) => Math.min(prev, phases.length - 2));
      setCurrentFrameIndex(0);
    },
    [phases.length]
  );

  const renamePhase = useCallback((index: number, name: string) => {
    setPhases((prev) => {
      const next = [...prev];
      next[index] = { ...next[index], name };
      return next;
    });
  }, []);

  const handleSave = useCallback(
    (name: string, description: string) => {
      const strategy: Strategy = {
        id: strategyId,
        name,
        description,
        phases,
        createdAt: Date.now(),
      };
      saveStrategy(strategy);
      setStrategyName(name);
      setShowSaveForm(false);
    },
    [strategyId, phases]
  );

  const handleLoad = useCallback((strategy: Strategy) => {
    setStrategyId(strategy.id);
    setStrategyName(strategy.name);
    setPhases(strategy.phases);
    setCurrentPhaseIndex(0);
    setCurrentFrameIndex(0);
    setShowLoadList(false);
  }, []);

  const handleNew = useCallback(() => {
    setStrategyId(generateId());
    setStrategyName('');
    setPhases([createDefaultPhase()]);
    setCurrentPhaseIndex(0);
    setCurrentFrameIndex(0);
  }, []);

  return (
    <div className="w-full h-full flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700 shrink-0">
        <h1 className="text-lg font-bold">
          풋살 전술 보드
          {strategyName && (
            <span className="text-sm text-gray-400 ml-2">— {strategyName}</span>
          )}
        </h1>
        <div className="flex gap-2">
          <button onClick={handleNew} className="px-3 py-1 text-sm bg-gray-700 rounded hover:bg-gray-600">
            새 전략
          </button>
          <button onClick={() => setShowSaveForm(true)} className="px-3 py-1 text-sm bg-green-600 rounded hover:bg-green-700">
            저장
          </button>
          <button onClick={() => setShowLoadList(true)} className="px-3 py-1 text-sm bg-blue-600 rounded hover:bg-blue-700">
            불러오기
          </button>
          <button
            onClick={() => setShowHighlight(true)}
            className="px-3 py-1 text-sm bg-orange-600 rounded hover:bg-orange-700"
          >
            하이라이트
          </button>
          <button
            onClick={() => setShowChat((v) => !v)}
            className={`px-3 py-1 text-sm rounded ${showChat ? 'bg-purple-600' : 'bg-gray-700'}`}
          >
            채팅
          </button>
        </div>
      </header>

      {/* Main */}
      <div className="flex-1 flex min-h-0">
        <div className="flex-1 flex flex-col min-w-0">
          <div className="flex-1">
            <TacticalBoard3D
              players={players}
              ballPosition={ballPosition}
              selectedId={selectedId}
              onSelectPlayer={(id) => setSelectedId(id)}
              onSelectBall={() => setSelectedId('ball')}
              onMovePlayer={handleMovePlayer}
              onMoveBall={handleMoveBall}
              isPlaying={animation.isPlaying}
              runningPlayerIds={animation.runningPlayerIds}
              interpolatedPlayers={animation.interpolatedPlayers}
              interpolatedBall={animation.interpolatedBall}
            />
          </div>
          <div className="flex flex-col gap-1 p-2 shrink-0">
            <PhasePanel
              phases={phases}
              currentPhaseIndex={currentPhaseIndex}
              onSelectPhase={(i) => { animation.stop(); setCurrentPhaseIndex(i); setCurrentFrameIndex(0); }}
              onAddPhase={addPhase}
              onDeletePhase={deletePhase}
              onRenamePhase={renamePhase}
            />
            <Timeline
              frames={currentPhase?.frames || []}
              currentFrameIndex={currentFrameIndex}
              onSelectFrame={(i) => { animation.stop(); setCurrentFrameIndex(i); }}
              onAddFrame={addFrame}
              onDeleteFrame={deleteFrame}
            />
            <div className="flex gap-2">
              <div className="flex-1">
                <PlaybackControls
                  isPlaying={animation.isPlaying}
                  speed={animation.speed}
                  onPlay={() => animation.play(false)}
                  onPlayAll={() => animation.play(true)}
                  onStop={animation.stop}
                  onSpeedChange={animation.setSpeed}
                  canPlay={(currentPhase?.frames.length || 0) >= 2}
                />
              </div>
              <div className="w-64">
                <BallHeightSlider
                  height={ballPosition.y}
                  onChange={handleBallHeight}
                  disabled={animation.isPlaying}
                />
              </div>
            </div>
          </div>
        </div>

        {showChat && (
          <div className="w-80 border-l border-gray-700 shrink-0">
            <ChatRoom strategyId={strategyId} />
          </div>
        )}
      </div>

      {showSaveForm && (
        <StrategyForm
          initialName={strategyName}
          onSave={handleSave}
          onClose={() => setShowSaveForm(false)}
        />
      )}
      {showLoadList && (
        <StrategyList onLoad={handleLoad} onClose={() => setShowLoadList(false)} />
      )}
      {showHighlight && (
        <HighlightGenerator onClose={() => setShowHighlight(false)} />
      )}
    </div>
  );
}
