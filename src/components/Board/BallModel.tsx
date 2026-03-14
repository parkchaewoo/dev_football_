import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
interface BallModelProps {
  position: [number, number, number];
  selected?: boolean;
  onClick?: () => void;
  onPointerDown?: (e: any) => void;
  isMoving?: boolean;
}

export default function BallModel({
  position,
  selected,
  onClick,
  onPointerDown,
  isMoving,
}: BallModelProps) {
  const ballRef = useRef<any>(null);
  const spinPhase = useRef(0);

  useFrame((_, delta) => {
    if (isMoving && ballRef.current) {
      spinPhase.current += delta * 5;
      ballRef.current.rotation.x = spinPhase.current;
    }
  });

  const groundY = 0;
  const ballHeight = position[1];
  const isAerial = ballHeight > 0.3;

  return (
    <group>
      {/* Shadow on ground when ball is aerial */}
      {isAerial && (
        <mesh
          rotation={[-Math.PI / 2, 0, 0]}
          position={[position[0], 0.02, position[2]]}
        >
          <circleGeometry args={[0.2 * (1 - ballHeight / 10), 16]} />
          <meshBasicMaterial color="#000000" transparent opacity={0.3} />
        </mesh>
      )}

      {/* Height indicator line */}
      {isAerial && (
        <line>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              args={[new Float32Array([
                position[0], groundY + 0.01, position[2],
                position[0], ballHeight, position[2],
              ]), 3]}
            />
          </bufferGeometry>
          <lineBasicMaterial color="#999999" transparent opacity={0.5} />
        </line>
      )}

      {/* Selection ring */}
      {selected && (
        <mesh
          rotation={[-Math.PI / 2, 0, 0]}
          position={[position[0], isAerial ? 0.02 : position[1] + 0.02, position[2]]}
        >
          <ringGeometry args={[0.35, 0.45, 32]} />
          <meshBasicMaterial color="#ffd700" />
        </mesh>
      )}

      {/* Ball */}
      <mesh
        ref={ballRef}
        position={position}
        castShadow
        onClick={onClick}
        onPointerDown={onPointerDown}
      >
        <sphereGeometry args={[0.22, 16, 16]} />
        <meshStandardMaterial color="#f0f0f0" roughness={0.4} />
      </mesh>

      {/* Ball pentagon pattern (simple) */}
      <mesh position={position}>
        <dodecahedronGeometry args={[0.18, 0]} />
        <meshStandardMaterial
          color="#333333"
          wireframe
          transparent
          opacity={0.3}
        />
      </mesh>
    </group>
  );
}
