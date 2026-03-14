import { useMemo } from 'react';
import * as THREE from 'three';

// Futsal court dimensions (in meters, scaled)
const COURT_LENGTH = 40;
const COURT_WIDTH = 20;
const HALF_LENGTH = COURT_LENGTH / 2;
const HALF_WIDTH = COURT_WIDTH / 2;
const PENALTY_AREA_LENGTH = 6;
const PENALTY_AREA_WIDTH = 12;
const CENTER_CIRCLE_RADIUS = 3;
const GOAL_WIDTH = 3;
const GOAL_HEIGHT = 2;
const GOAL_DEPTH = 1;
const LINE_COLOR = '#ffffff';
const COURT_COLOR = '#2d8a4e';

function CourtLines() {
  const points = useMemo(() => {
    const lines: THREE.Vector3[][] = [];

    // Outer boundary
    lines.push([
      new THREE.Vector3(-HALF_LENGTH, 0.01, -HALF_WIDTH),
      new THREE.Vector3(HALF_LENGTH, 0.01, -HALF_WIDTH),
      new THREE.Vector3(HALF_LENGTH, 0.01, HALF_WIDTH),
      new THREE.Vector3(-HALF_LENGTH, 0.01, HALF_WIDTH),
      new THREE.Vector3(-HALF_LENGTH, 0.01, -HALF_WIDTH),
    ]);

    // Center line
    lines.push([
      new THREE.Vector3(0, 0.01, -HALF_WIDTH),
      new THREE.Vector3(0, 0.01, HALF_WIDTH),
    ]);

    // Center circle
    const circlePoints: THREE.Vector3[] = [];
    for (let i = 0; i <= 64; i++) {
      const angle = (i / 64) * Math.PI * 2;
      circlePoints.push(
        new THREE.Vector3(
          Math.cos(angle) * CENTER_CIRCLE_RADIUS,
          0.01,
          Math.sin(angle) * CENTER_CIRCLE_RADIUS
        )
      );
    }
    lines.push(circlePoints);

    // Left penalty area
    const halfPenaltyWidth = PENALTY_AREA_WIDTH / 2;
    lines.push([
      new THREE.Vector3(-HALF_LENGTH, 0.01, -halfPenaltyWidth),
      new THREE.Vector3(-HALF_LENGTH + PENALTY_AREA_LENGTH, 0.01, -halfPenaltyWidth),
      new THREE.Vector3(-HALF_LENGTH + PENALTY_AREA_LENGTH, 0.01, halfPenaltyWidth),
      new THREE.Vector3(-HALF_LENGTH, 0.01, halfPenaltyWidth),
    ]);

    // Right penalty area
    lines.push([
      new THREE.Vector3(HALF_LENGTH, 0.01, -halfPenaltyWidth),
      new THREE.Vector3(HALF_LENGTH - PENALTY_AREA_LENGTH, 0.01, -halfPenaltyWidth),
      new THREE.Vector3(HALF_LENGTH - PENALTY_AREA_LENGTH, 0.01, halfPenaltyWidth),
      new THREE.Vector3(HALF_LENGTH, 0.01, halfPenaltyWidth),
    ]);

    // Left penalty arc (quarter circle)
    const leftArc: THREE.Vector3[] = [];
    for (let i = 0; i <= 32; i++) {
      const angle = -Math.PI / 2 + (i / 32) * Math.PI;
      leftArc.push(
        new THREE.Vector3(
          -HALF_LENGTH + PENALTY_AREA_LENGTH + Math.cos(angle) * CENTER_CIRCLE_RADIUS,
          0.01,
          Math.sin(angle) * CENTER_CIRCLE_RADIUS
        )
      );
    }
    lines.push(leftArc);

    // Right penalty arc
    const rightArc: THREE.Vector3[] = [];
    for (let i = 0; i <= 32; i++) {
      const angle = Math.PI / 2 + (i / 32) * Math.PI;
      rightArc.push(
        new THREE.Vector3(
          HALF_LENGTH - PENALTY_AREA_LENGTH + Math.cos(angle) * CENTER_CIRCLE_RADIUS,
          0.01,
          Math.sin(angle) * CENTER_CIRCLE_RADIUS
        )
      );
    }
    lines.push(rightArc);

    return lines;
  }, []);

  return (
    <>
      {points.map((linePoints, i) => (
        <line key={i}>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              args={[new Float32Array(linePoints.flatMap(p => [p.x, p.y, p.z])), 3]}
            />
          </bufferGeometry>
          <lineBasicMaterial color={LINE_COLOR} linewidth={2} />
        </line>
      ))}
    </>
  );
}

function GoalPost({ side }: { side: 'left' | 'right' }) {
  const x = side === 'left' ? -HALF_LENGTH : HALF_LENGTH;
  const dir = side === 'left' ? -1 : 1;
  const postRadius = 0.05;
  const halfGoalWidth = GOAL_WIDTH / 2;

  return (
    <group>
      {/* Left post */}
      <mesh position={[x - dir * GOAL_DEPTH / 2, GOAL_HEIGHT / 2, -halfGoalWidth]}>
        <cylinderGeometry args={[postRadius, postRadius, GOAL_HEIGHT, 8]} />
        <meshStandardMaterial color="#cccccc" metalness={0.8} roughness={0.2} />
      </mesh>
      {/* Right post */}
      <mesh position={[x - dir * GOAL_DEPTH / 2, GOAL_HEIGHT / 2, halfGoalWidth]}>
        <cylinderGeometry args={[postRadius, postRadius, GOAL_HEIGHT, 8]} />
        <meshStandardMaterial color="#cccccc" metalness={0.8} roughness={0.2} />
      </mesh>
      {/* Crossbar */}
      <mesh position={[x - dir * GOAL_DEPTH / 2, GOAL_HEIGHT, 0]} rotation={[0, 0, Math.PI / 2]}>
        <cylinderGeometry args={[postRadius, postRadius, GOAL_WIDTH, 8]} />
        <meshStandardMaterial color="#cccccc" metalness={0.8} roughness={0.2} />
      </mesh>
      {/* Net (transparent mesh) */}
      <mesh position={[x - dir * GOAL_DEPTH / 2, GOAL_HEIGHT / 2, 0]}>
        <boxGeometry args={[GOAL_DEPTH, GOAL_HEIGHT, GOAL_WIDTH]} />
        <meshStandardMaterial
          color="#ffffff"
          transparent
          opacity={0.15}
          wireframe
        />
      </mesh>
    </group>
  );
}

export default function FutsalCourt3D() {
  return (
    <group>
      {/* Court surface */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]} receiveShadow>
        <planeGeometry args={[COURT_LENGTH + 4, COURT_WIDTH + 4]} />
        <meshStandardMaterial color={COURT_COLOR} />
      </mesh>

      {/* Court lines */}
      <CourtLines />

      {/* Center spot */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, 0]}>
        <circleGeometry args={[0.2, 16]} />
        <meshBasicMaterial color={LINE_COLOR} />
      </mesh>

      {/* Penalty spots */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[-HALF_LENGTH + PENALTY_AREA_LENGTH, 0.02, 0]}>
        <circleGeometry args={[0.15, 16]} />
        <meshBasicMaterial color={LINE_COLOR} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[HALF_LENGTH - PENALTY_AREA_LENGTH, 0.02, 0]}>
        <circleGeometry args={[0.15, 16]} />
        <meshBasicMaterial color={LINE_COLOR} />
      </mesh>

      {/* Goals */}
      <GoalPost side="left" />
      <GoalPost side="right" />
    </group>
  );
}

export { COURT_LENGTH, COURT_WIDTH, HALF_LENGTH, HALF_WIDTH };
