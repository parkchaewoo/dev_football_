import { useRef, useState, useCallback } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import FutsalCourt3D, { HALF_LENGTH, HALF_WIDTH } from './FutsalCourt3D';
import PlayerModel from './PlayerModel';
import BallModel from './BallModel';
import { useDragOnPlane } from '../../hooks/useDragOnPlane';
import type { Player, Position3D } from '../../types';

interface SceneProps {
  players: Player[];
  ballPosition: Position3D;
  selectedId: string | null;
  onSelectPlayer: (id: string) => void;
  onSelectBall: () => void;
  onMovePlayer: (id: string, x: number, z: number) => void;
  onMoveBall: (x: number, z: number) => void;
  isPlaying: boolean;
  runningPlayerIds: Set<string>;
  interpolatedPlayers?: Player[];
  interpolatedBall?: Position3D;
}

function DraggablePlayer({
  player,
  selected,
  onSelect,
  onMove,
  setOrbitEnabled,
  isRunning,
  targetPosition,
}: {
  player: Player;
  selected: boolean;
  onSelect: () => void;
  onMove: (x: number, z: number) => void;
  setOrbitEnabled: (enabled: boolean) => void;
  isRunning: boolean;
  targetPosition?: [number, number, number];
}) {
  const { handlePointerDown } = useDragOnPlane(
    (x, z) => {
      const clampedX = Math.max(-HALF_LENGTH, Math.min(HALF_LENGTH, x));
      const clampedZ = Math.max(-HALF_WIDTH, Math.min(HALF_WIDTH, z));
      onMove(clampedX, clampedZ);
    },
    undefined,
    setOrbitEnabled
  );

  return (
    <PlayerModel
      position={[player.position.x, 0, player.position.z]}
      team={player.team}
      number={player.number}
      selected={selected}
      isRunning={isRunning}
      targetPosition={targetPosition}
      onClick={onSelect}
      onPointerDown={handlePointerDown}
    />
  );
}

function DraggableBall({
  position,
  selected,
  onSelect,
  onMove,
  setOrbitEnabled,
  isMoving,
}: {
  position: Position3D;
  selected: boolean;
  onSelect: () => void;
  onMove: (x: number, z: number) => void;
  setOrbitEnabled: (enabled: boolean) => void;
  isMoving: boolean;
}) {
  const { handlePointerDown } = useDragOnPlane(
    (x, z) => {
      const clampedX = Math.max(-HALF_LENGTH, Math.min(HALF_LENGTH, x));
      const clampedZ = Math.max(-HALF_WIDTH, Math.min(HALF_WIDTH, z));
      onMove(clampedX, clampedZ);
    },
    undefined,
    setOrbitEnabled
  );

  return (
    <BallModel
      position={[position.x, position.y, position.z]}
      selected={selected}
      onClick={onSelect}
      onPointerDown={handlePointerDown}
      isMoving={isMoving}
    />
  );
}

function Scene({
  players,
  ballPosition,
  selectedId,
  onSelectPlayer,
  onSelectBall,
  onMovePlayer,
  onMoveBall,
  isPlaying,
  runningPlayerIds,
  interpolatedPlayers,
  interpolatedBall,
}: SceneProps) {
  const [orbitEnabled, setOrbitEnabled] = useState(true);
  const orbitRef = useRef<any>(null);

  const setOrbit = useCallback((enabled: boolean) => {
    setOrbitEnabled(enabled);
    if (orbitRef.current) {
      orbitRef.current.enabled = enabled;
    }
  }, []);

  const displayPlayers = isPlaying && interpolatedPlayers ? interpolatedPlayers : players;
  const displayBall = isPlaying && interpolatedBall ? interpolatedBall : ballPosition;

  return (
    <>
      {/* Lighting */}
      <ambientLight intensity={0.6} />
      <directionalLight
        position={[20, 30, 10]}
        intensity={1}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
      />
      <directionalLight position={[-10, 20, -10]} intensity={0.3} />

      {/* Camera controls */}
      <OrbitControls
        ref={orbitRef}
        enabled={orbitEnabled}
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        maxPolarAngle={Math.PI / 2.1}
        minDistance={5}
        maxDistance={60}
      />

      {/* Court */}
      <FutsalCourt3D />

      {/* Players */}
      {displayPlayers.map((player) => (
        <DraggablePlayer
          key={player.id}
          player={player}
          selected={selectedId === player.id}
          onSelect={() => !isPlaying && onSelectPlayer(player.id)}
          onMove={(x, z) => !isPlaying && onMovePlayer(player.id, x, z)}
          setOrbitEnabled={setOrbit}
          isRunning={runningPlayerIds.has(player.id)}
          targetPosition={undefined}
        />
      ))}

      {/* Ball */}
      <DraggableBall
        position={displayBall}
        selected={selectedId === 'ball'}
        onSelect={() => !isPlaying && onSelectBall()}
        onMove={(x, z) => !isPlaying && onMoveBall(x, z)}
        setOrbitEnabled={setOrbit}
        isMoving={isPlaying}
      />
    </>
  );
}

interface TacticalBoard3DProps {
  players: Player[];
  ballPosition: Position3D;
  selectedId: string | null;
  onSelectPlayer: (id: string) => void;
  onSelectBall: () => void;
  onMovePlayer: (id: string, x: number, z: number) => void;
  onMoveBall: (x: number, z: number) => void;
  isPlaying: boolean;
  runningPlayerIds: Set<string>;
  interpolatedPlayers?: Player[];
  interpolatedBall?: Position3D;
}

export default function TacticalBoard3D(props: TacticalBoard3DProps) {
  return (
    <Canvas
      camera={{
        position: [25, 25, 25],
        fov: 45,
        near: 0.1,
        far: 200,
      }}
      shadows
      style={{ background: '#1a1a2e' }}
    >
      <Scene {...props} />
    </Canvas>
  );
}
