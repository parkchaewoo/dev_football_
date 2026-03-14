import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text } from '@react-three/drei';
interface PlayerModelProps {
  position: [number, number, number];
  team: 'home' | 'away';
  number: number;
  isRunning: boolean;
  targetPosition?: [number, number, number];
  selected?: boolean;
  onClick?: () => void;
  onPointerDown?: (e: any) => void;
}

const TEAM_COLORS = {
  home: { jersey: '#e53e3e', shorts: '#1a1a2e', skin: '#f5d0a9' },
  away: { jersey: '#3b82f6', shorts: '#f0f0f0', skin: '#f5d0a9' },
};

export default function PlayerModel({
  position,
  team,
  number,
  isRunning,
  targetPosition,
  selected,
  onClick,
  onPointerDown,
}: PlayerModelProps) {
  const groupRef = useRef<any>(null);
  const leftArmRef = useRef<any>(null);
  const rightArmRef = useRef<any>(null);
  const leftLegRef = useRef<any>(null);
  const rightLegRef = useRef<any>(null);
  const runPhase = useRef(0);

  const colors = TEAM_COLORS[team];

  // Compute rotation to face target
  const rotation = useMemo(() => {
    if (targetPosition) {
      const dx = targetPosition[0] - position[0];
      const dz = targetPosition[2] - position[2];
      if (Math.abs(dx) > 0.01 || Math.abs(dz) > 0.01) {
        return Math.atan2(dx, dz);
      }
    }
    return team === 'home' ? Math.PI / 2 : -Math.PI / 2;
  }, [position, targetPosition, team]);

  useFrame((_, delta) => {
    if (!isRunning) {
      runPhase.current = 0;
      // Reset limbs
      if (leftArmRef.current) leftArmRef.current.rotation.x = 0;
      if (rightArmRef.current) rightArmRef.current.rotation.x = 0;
      if (leftLegRef.current) leftLegRef.current.rotation.x = 0;
      if (rightLegRef.current) rightLegRef.current.rotation.x = 0;
      return;
    }

    runPhase.current += delta * 8;
    const swing = Math.sin(runPhase.current) * 0.8;

    // Arms swing opposite to legs
    if (leftArmRef.current) leftArmRef.current.rotation.x = -swing;
    if (rightArmRef.current) rightArmRef.current.rotation.x = swing;
    if (leftLegRef.current) leftLegRef.current.rotation.x = swing;
    if (rightLegRef.current) rightLegRef.current.rotation.x = -swing;
  });

  return (
    <group
      ref={groupRef}
      position={position}
      rotation={[0, rotation, 0]}
      onClick={onClick}
      onPointerDown={onPointerDown}
    >
      {/* Selection ring */}
      {selected && (
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, 0]}>
          <ringGeometry args={[0.6, 0.75, 32]} />
          <meshBasicMaterial color="#ffd700" />
        </mesh>
      )}

      {/* Head */}
      <mesh position={[0, 1.65, 0]} castShadow>
        <sphereGeometry args={[0.18, 16, 16]} />
        <meshStandardMaterial color={colors.skin} />
      </mesh>

      {/* Body / Jersey */}
      <mesh position={[0, 1.15, 0]} castShadow>
        <capsuleGeometry args={[0.2, 0.5, 8, 16]} />
        <meshStandardMaterial color={colors.jersey} />
      </mesh>

      {/* Left arm - pivots from shoulder */}
      <group position={[-0.3, 1.35, 0]}>
        <mesh ref={leftArmRef} position={[0, -0.2, 0]} castShadow>
          <capsuleGeometry args={[0.06, 0.3, 4, 8]} />
          <meshStandardMaterial color={colors.skin} />
        </mesh>
      </group>

      {/* Right arm */}
      <group position={[0.3, 1.35, 0]}>
        <mesh ref={rightArmRef} position={[0, -0.2, 0]} castShadow>
          <capsuleGeometry args={[0.06, 0.3, 4, 8]} />
          <meshStandardMaterial color={colors.skin} />
        </mesh>
      </group>

      {/* Left leg - shorts + leg */}
      <group position={[-0.1, 0.75, 0]}>
        <mesh ref={leftLegRef} position={[0, -0.25, 0]} castShadow>
          <capsuleGeometry args={[0.08, 0.4, 4, 8]} />
          <meshStandardMaterial color={colors.shorts} />
        </mesh>
      </group>

      {/* Right leg */}
      <group position={[0.1, 0.75, 0]}>
        <mesh ref={rightLegRef} position={[0, -0.25, 0]} castShadow>
          <capsuleGeometry args={[0.08, 0.4, 4, 8]} />
          <meshStandardMaterial color={colors.shorts} />
        </mesh>
      </group>

      {/* Shoes */}
      <mesh position={[-0.1, 0.1, 0.05]} castShadow>
        <boxGeometry args={[0.12, 0.08, 0.2]} />
        <meshStandardMaterial color="#1a1a1a" />
      </mesh>
      <mesh position={[0.1, 0.1, 0.05]} castShadow>
        <boxGeometry args={[0.12, 0.08, 0.2]} />
        <meshStandardMaterial color="#1a1a1a" />
      </mesh>

      {/* Back number */}
      <Text
        position={[0, 1.2, -0.22]}
        rotation={[0, Math.PI, 0]}
        fontSize={0.18}
        color="white"
        anchorX="center"
        anchorY="middle"
        font={undefined}
      >
        {number.toString()}
      </Text>

      {/* Front number */}
      <Text
        position={[0, 1.2, 0.22]}
        fontSize={0.14}
        color="white"
        anchorX="center"
        anchorY="middle"
        font={undefined}
      >
        {number.toString()}
      </Text>
    </group>
  );
}
