import { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginScreen from './components/Auth/LoginScreen';
import TeamList from './components/Team/TeamList';
import TacticalBoard3D from './components/Board/TacticalBoard3D';
import PhasePanel from './components/Animation/PhasePanel';
import Timeline from './components/Animation/Timeline';
import PlaybackControls from './components/Animation/PlaybackControls';
import BallHeightSlider from './components/Controls/BallHeightSlider';
import ChatRoom from './components/Chat/ChatRoom';
import StrategyForm from './components/Strategy/StrategyForm';
import StrategyFeed from './components/Strategy/StrategyFeed';
import CommentSection from './components/Social/CommentSection';
import LikeButton from './components/Social/LikeButton';
import InjuryHospital from './components/Injury/InjuryHospital';
import TeamBoard from './components/Board/TeamBoard';
import { useAnimation } from './hooks/useAnimation';
import type { Player, Phase, Frame, Team, StrategyMeta } from './types';
import { generateId } from './utils/storage';
import { saveStrategyToFirestore } from './services/strategyService';
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

function TacticalBoardApp() {
  const { user, profile } = useAuth();
  const [currentTeam, setCurrentTeam] = useState<Team | null>(null);
  const [strategyId, setStrategyId] = useState<string | null>(null);
  const [strategyName, setStrategyName] = useState('');
  const [phases, setPhases] = useState<Phase[]>([createDefaultPhase()]);
  const [currentPhaseIndex, setCurrentPhaseIndex] = useState(0);
  const [currentFrameIndex, setCurrentFrameIndex] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [showSaveForm, setShowSaveForm] = useState(false);
  const [showFeed, setShowFeed] = useState<'team' | 'public' | null>(null);
  const [showChat, setShowChat] = useState(true);
  const [showComments, setShowComments] = useState(false);
  const [showInjury, setShowInjury] = useState(false);
  const [showBoard, setShowBoard] = useState(false);

  const animation = useAnimation(phases);

  // If not logged in
  if (!user || !profile) return <LoginScreen />;
  // If no team selected
  if (!currentTeam) return <TeamList onSelectTeam={setCurrentTeam} />;

  const currentPhase = phases[currentPhaseIndex];
  const currentFrame = currentPhase?.frames[currentFrameIndex];
  const players = currentFrame?.players || [];
  const ballPosition = currentFrame?.ballPosition || { x: 0, y: 0.22, z: 0 };

  const updateCurrentFrame = (updater: (frame: Frame) => Frame) => {
    setPhases((prev) => {
      const next = [...prev];
      const phase = { ...next[currentPhaseIndex] };
      const frames = [...phase.frames];
      frames[currentFrameIndex] = updater(frames[currentFrameIndex]);
      phase.frames = frames;
      next[currentPhaseIndex] = phase;
      return next;
    });
  };

  const handleMovePlayer = (id: string, x: number, z: number) => {
    updateCurrentFrame((frame) => ({
      ...frame,
      players: frame.players.map((p) =>
        p.id === id ? { ...p, position: { ...p.position, x, z } } : p
      ),
    }));
  };

  const handleMoveBall = (x: number, z: number) => {
    updateCurrentFrame((frame) => ({
      ...frame,
      ballPosition: { ...frame.ballPosition, x, z },
    }));
  };

  const handleBallHeight = (height: number) => {
    updateCurrentFrame((frame) => ({
      ...frame,
      ballPosition: { ...frame.ballPosition, y: height },
    }));
  };

  const addFrame = () => {
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
  };

  const deleteFrame = (index: number) => {
    setPhases((prev) => {
      const next = [...prev];
      const phase = { ...next[currentPhaseIndex] };
      if (phase.frames.length <= 1) return prev;
      phase.frames = phase.frames.filter((_, i) => i !== index);
      next[currentPhaseIndex] = phase;
      return next;
    });
    setCurrentFrameIndex((prev) => Math.max(0, Math.min(prev, phases[currentPhaseIndex].frames.length - 2)));
  };

  const addPhase = () => {
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
  };

  const deletePhase = (index: number) => {
    if (phases.length <= 1) return;
    setPhases((prev) => prev.filter((_, i) => i !== index));
    setCurrentPhaseIndex((prev) => Math.min(prev, phases.length - 2));
    setCurrentFrameIndex(0);
  };

  const renamePhase = (index: number, name: string) => {
    setPhases((prev) => {
      const next = [...prev];
      next[index] = { ...next[index], name };
      return next;
    });
  };

  const handleSave = async (name: string, description: string, visibility: 'public' | 'private' | 'team') => {
    const id = await saveStrategyToFirestore(
      { name, description, phases },
      profile.uid,
      profile.displayName,
      currentTeam.id,
      currentTeam.name,
      visibility,
      strategyId || undefined
    );
    setStrategyId(id);
    setStrategyName(name);
    setShowSaveForm(false);
  };

  const handleLoadFromFeed = (strategy: StrategyMeta) => {
    setStrategyId(strategy.id);
    setStrategyName(strategy.name);
    setPhases(strategy.phases);
    setCurrentPhaseIndex(0);
    setCurrentFrameIndex(0);
    setShowFeed(null);
  };

  const handleNew = () => {
    setStrategyId(null);
    setStrategyName('');
    setPhases([createDefaultPhase()]);
    setCurrentPhaseIndex(0);
    setCurrentFrameIndex(0);
  };

  return (
    <div className="w-full h-full flex flex-col bg-gray-900 text-white">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700 shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setCurrentTeam(null)}
            className="text-gray-400 hover:text-white text-sm"
          >
            ← 팀 목록
          </button>
          <h1 className="text-lg font-bold">
            {currentTeam.name}
            {strategyName && (
              <span className="text-sm text-gray-400 ml-2">— {strategyName}</span>
            )}
          </h1>
        </div>
        <div className="flex gap-2">
          <button onClick={handleNew} className="px-3 py-1 text-sm bg-gray-700 rounded hover:bg-gray-600">
            새 전략
          </button>
          <button onClick={() => setShowSaveForm(true)} className="px-3 py-1 text-sm bg-green-600 rounded hover:bg-green-700">
            저장
          </button>
          <button onClick={() => setShowFeed('team')} className="px-3 py-1 text-sm bg-blue-600 rounded hover:bg-blue-700">
            팀 전술
          </button>
          <button onClick={() => setShowFeed('public')} className="px-3 py-1 text-sm bg-indigo-600 rounded hover:bg-indigo-700">
            공개 전술
          </button>
          <button onClick={() => setShowInjury(true)} className="px-3 py-1 text-sm bg-emerald-600 rounded hover:bg-emerald-700">
            부상/병원
          </button>
          <button onClick={() => setShowBoard(true)} className="px-3 py-1 text-sm bg-amber-600 rounded hover:bg-amber-700">
            게시판
          </button>
          <button
            onClick={() => setShowChat((v) => !v)}
            className={`px-3 py-1 text-sm rounded ${showChat ? 'bg-purple-600' : 'bg-gray-700'}`}
          >
            채팅
          </button>
          {strategyId && (
            <button
              onClick={() => setShowComments((v) => !v)}
              className={`px-3 py-1 text-sm rounded ${showComments ? 'bg-orange-600' : 'bg-gray-700'}`}
            >
              댓글
            </button>
          )}
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

            {/* Social section */}
            {strategyId && showComments && (
              <div className="flex items-start gap-4 p-2 bg-gray-800 rounded-lg mt-1">
                <div className="flex-1">
                  <CommentSection strategyId={strategyId} />
                </div>
                <LikeButton strategyId={strategyId} initialCount={0} />
              </div>
            )}
          </div>
        </div>

        {showChat && (
          <div className="w-80 border-l border-gray-700 shrink-0">
            <ChatRoom strategyId={strategyId || 'general'} />
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
      {showFeed && (
        <StrategyFeed
          teamId={currentTeam.id}
          mode={showFeed}
          onLoad={handleLoadFromFeed}
          onClose={() => setShowFeed(null)}
        />
      )}
      {showInjury && (
        <InjuryHospital onClose={() => setShowInjury(false)} />
      )}
      {showBoard && (
        <TeamBoard team={currentTeam} onClose={() => setShowBoard(false)} />
      )}
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <TacticalBoardApp />
    </AuthProvider>
  );
}
