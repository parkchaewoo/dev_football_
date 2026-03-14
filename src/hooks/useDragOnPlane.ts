import { useCallback, useRef } from 'react';
import { useThree } from '@react-three/fiber';
import * as THREE from 'three';

const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
const intersection = new THREE.Vector3();

export function useDragOnPlane(
  onDrag: (x: number, z: number) => void,
  onDragEnd?: () => void,
  setOrbitEnabled?: (enabled: boolean) => void
) {
  const { camera, gl } = useThree();
  const raycaster = useRef(new THREE.Raycaster());
  const isDragging = useRef(false);

  const getPlaneIntersection = useCallback(
    (event: PointerEvent) => {
      const rect = gl.domElement.getBoundingClientRect();
      const mouse = new THREE.Vector2(
        ((event.clientX - rect.left) / rect.width) * 2 - 1,
        -((event.clientY - rect.top) / rect.height) * 2 + 1
      );
      raycaster.current.setFromCamera(mouse, camera);
      raycaster.current.ray.intersectPlane(plane, intersection);
      return intersection;
    },
    [camera, gl]
  );

  const handlePointerDown = useCallback(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (e: any) => {
      e.stopPropagation();
      isDragging.current = true;
      setOrbitEnabled?.(false);

      const onPointerMove = (event: PointerEvent) => {
        if (!isDragging.current) return;
        const point = getPlaneIntersection(event);
        onDrag(point.x, point.z);
      };

      const onPointerUp = () => {
        isDragging.current = false;
        setOrbitEnabled?.(true);
        onDragEnd?.();
        gl.domElement.removeEventListener('pointermove', onPointerMove);
        gl.domElement.removeEventListener('pointerup', onPointerUp);
      };

      gl.domElement.addEventListener('pointermove', onPointerMove);
      gl.domElement.addEventListener('pointerup', onPointerUp);
    },
    [gl, getPlaneIntersection, onDrag, onDragEnd, setOrbitEnabled]
  );

  return { handlePointerDown };
}
