import json
from dataclasses import asdict
from typing import List
from utils.models import Player, Position3D


def generate_board_html(
    players: List[Player],
    ball_position: Position3D,
    ball_height: float = 0.22,
    frames_data: str = "[]",
    is_playing: bool = False,
) -> str:
    players_json = json.dumps([asdict(p) for p in players])
    ball_json = json.dumps(asdict(ball_position))

    return f"""
<!DOCTYPE html>
<html>
<head>
<style>
  html, body {{
    margin: 0; padding: 0;
    width: 100%; height: 100%;
    overflow: hidden;
    background: #1a1a2e;
  }}
  canvas {{ display: block; width: 100%; height: 100%; }}
  #info {{
    position: absolute; top: 8px; left: 8px;
    color: #888; font: 12px sans-serif;
    pointer-events: none; z-index: 10;
  }}
  #error {{
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    color: #ff6b6b; font: 16px sans-serif;
    text-align: center; display: none; z-index: 20;
  }}
</style>
</head>
<body>
<div id="info">마우스 드래그: 선수/공 이동 | 우클릭 드래그: 카메라 회전 | 스크롤: 줌</div>
<div id="error"></div>

<script type="importmap">
{{
  "imports": {{
    "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
    "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
  }}
}}
</script>

<script type="module">
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';

try {{

  // ===== CONFIG =====
  const COURT_LENGTH = 40, COURT_WIDTH = 20;
  const HL = COURT_LENGTH / 2, HW = COURT_WIDTH / 2;
  const PENALTY_LEN = 6, PENALTY_W = 12, CENTER_R = 3;
  const GOAL_W = 3, GOAL_H = 2, GOAL_D = 1;

  let playersData = {players_json};
  let ballData = {ball_json};
  let framesData = {frames_data};
  let isPlaying = {'true' if is_playing else 'false'};

  // ===== SCENE SETUP =====
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x1a1a2e);

  const w = window.innerWidth || 800;
  const h = window.innerHeight || 600;

  const camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 200);
  camera.position.set(25, 25, 25);
  camera.lookAt(0, 0, 0);

  const renderer = new THREE.WebGLRenderer({{ antialias: true }});
  renderer.setSize(w, h);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  document.body.appendChild(renderer.domElement);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.maxPolarAngle = Math.PI / 2.1;
  controls.minDistance = 5;
  controls.maxDistance = 60;
  controls.mouseButtons = {{
    LEFT: null,
    MIDDLE: THREE.MOUSE.DOLLY,
    RIGHT: THREE.MOUSE.ROTATE
  }};
  controls.touches = {{ ONE: null, TWO: THREE.TOUCH.DOLLY_ROTATE }};

  // Lights
  scene.add(new THREE.AmbientLight(0xffffff, 0.6));
  const dirLight = new THREE.DirectionalLight(0xffffff, 1);
  dirLight.position.set(20, 30, 10);
  scene.add(dirLight);
  const dirLight2 = new THREE.DirectionalLight(0xffffff, 0.3);
  dirLight2.position.set(-10, 20, -10);
  scene.add(dirLight2);

  // ===== COURT =====
  const courtGeo = new THREE.PlaneGeometry(COURT_LENGTH + 4, COURT_WIDTH + 4);
  const courtMat = new THREE.MeshStandardMaterial({{ color: 0x2d8a4e }});
  const court = new THREE.Mesh(courtGeo, courtMat);
  court.rotation.x = -Math.PI / 2;
  court.receiveShadow = true;
  scene.add(court);

  // Court lines
  const lineMat = new THREE.LineBasicMaterial({{ color: 0xffffff }});
  function addLine(points) {{
    const geo = new THREE.BufferGeometry().setFromPoints(
      points.map(p => new THREE.Vector3(p[0], 0.02, p[1]))
    );
    scene.add(new THREE.Line(geo, lineMat));
  }}

  // Boundary
  addLine([[-HL,-HW],[HL,-HW],[HL,HW],[-HL,HW],[-HL,-HW]]);
  // Center line
  addLine([[0,-HW],[0,HW]]);
  // Center circle
  const cc = [];
  for (let i = 0; i <= 64; i++) {{
    const a = (i/64)*Math.PI*2;
    cc.push([Math.cos(a)*CENTER_R, Math.sin(a)*CENTER_R]);
  }}
  addLine(cc);
  // Penalty areas
  const hpw = PENALTY_W / 2;
  addLine([[-HL,-hpw],[-HL+PENALTY_LEN,-hpw],[-HL+PENALTY_LEN,hpw],[-HL,hpw]]);
  addLine([[HL,-hpw],[HL-PENALTY_LEN,-hpw],[HL-PENALTY_LEN,hpw],[HL,hpw]]);

  // Center spot
  const spotGeo = new THREE.CircleGeometry(0.2, 16);
  const spotMat = new THREE.MeshBasicMaterial({{ color: 0xffffff }});
  const spot = new THREE.Mesh(spotGeo, spotMat);
  spot.rotation.x = -Math.PI / 2;
  spot.position.y = 0.03;
  scene.add(spot);

  // Goals
  function addGoal(side) {{
    const x = side === 'left' ? -HL : HL;
    const dir = side === 'left' ? -1 : 1;
    const postMat = new THREE.MeshStandardMaterial({{ color: 0xcccccc, metalness: 0.8 }});
    const postGeo = new THREE.CylinderGeometry(0.05, 0.05, GOAL_H, 8);
    const hgw = GOAL_W / 2;

    const lp = new THREE.Mesh(postGeo, postMat);
    lp.position.set(x - dir*GOAL_D/2, GOAL_H/2, -hgw);
    scene.add(lp);
    const rp = new THREE.Mesh(postGeo, postMat);
    rp.position.set(x - dir*GOAL_D/2, GOAL_H/2, hgw);
    scene.add(rp);
    const barGeo = new THREE.CylinderGeometry(0.05, 0.05, GOAL_W, 8);
    const bar = new THREE.Mesh(barGeo, postMat);
    bar.rotation.z = Math.PI / 2;
    bar.position.set(x - dir*GOAL_D/2, GOAL_H, 0);
    scene.add(bar);
    const netGeo = new THREE.BoxGeometry(GOAL_D, GOAL_H, GOAL_W);
    const netMat = new THREE.MeshStandardMaterial({{ color: 0xffffff, transparent: true, opacity: 0.15, wireframe: true }});
    const net = new THREE.Mesh(netGeo, netMat);
    net.position.set(x - dir*GOAL_D/2, GOAL_H/2, 0);
    scene.add(net);
  }}
  addGoal('left');
  addGoal('right');

  // ===== PLAYER MODELS =====
  const TEAM_COLORS = {{
    home: {{ jersey: 0xe53e3e, shorts: 0x1a1a2e, skin: 0xf5d0a9 }},
    away: {{ jersey: 0x3b82f6, shorts: 0xf0f0f0, skin: 0xf5d0a9 }}
  }};

  const playerMeshes = [];
  const playerDragTargets = [];

  function createPlayer(data) {{
    const colors = TEAM_COLORS[data.team];
    const group = new THREE.Group();
    group.userData = {{ id: data.id, type: 'player', team: data.team }};

    // Head
    const head = new THREE.Mesh(
      new THREE.SphereGeometry(0.18, 16, 16),
      new THREE.MeshStandardMaterial({{ color: colors.skin }})
    );
    head.position.y = 1.65;
    group.add(head);

    // Body (jersey) - CapsuleGeometry
    const body = new THREE.Mesh(
      new THREE.CapsuleGeometry(0.2, 0.5, 8, 16),
      new THREE.MeshStandardMaterial({{ color: colors.jersey }})
    );
    body.position.y = 1.15;
    group.add(body);

    // Arms
    const armMat = new THREE.MeshStandardMaterial({{ color: colors.skin }});
    const armGeo = new THREE.CapsuleGeometry(0.06, 0.3, 4, 8);
    const lArm = new THREE.Mesh(armGeo, armMat);
    lArm.position.set(-0.3, 1.15, 0);
    group.add(lArm);
    const rArm = new THREE.Mesh(armGeo, armMat);
    rArm.position.set(0.3, 1.15, 0);
    group.add(rArm);
    group.userData.leftArm = lArm;
    group.userData.rightArm = rArm;

    // Legs
    const legMat = new THREE.MeshStandardMaterial({{ color: colors.shorts }});
    const legGeo = new THREE.CapsuleGeometry(0.08, 0.4, 4, 8);
    const lLeg = new THREE.Mesh(legGeo, legMat);
    lLeg.position.set(-0.1, 0.5, 0);
    group.add(lLeg);
    const rLeg = new THREE.Mesh(legGeo, legMat);
    rLeg.position.set(0.1, 0.5, 0);
    group.add(rLeg);
    group.userData.leftLeg = lLeg;
    group.userData.rightLeg = rLeg;

    // Shoes
    const shoeMat = new THREE.MeshStandardMaterial({{ color: 0x1a1a1a }});
    const shoeGeo = new THREE.BoxGeometry(0.12, 0.08, 0.2);
    const lShoe = new THREE.Mesh(shoeGeo, shoeMat);
    lShoe.position.set(-0.1, 0.1, 0.05);
    group.add(lShoe);
    const rShoe = new THREE.Mesh(shoeGeo, shoeMat);
    rShoe.position.set(0.1, 0.1, 0.05);
    group.add(rShoe);

    // Number label (canvas texture)
    const canvas = document.createElement('canvas');
    canvas.width = 64; canvas.height = 64;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = 'white';
    ctx.font = 'bold 40px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(data.number.toString(), 32, 32);
    const tex = new THREE.CanvasTexture(canvas);
    const numMat = new THREE.SpriteMaterial({{ map: tex }});
    const numSprite = new THREE.Sprite(numMat);
    numSprite.scale.set(0.4, 0.4, 1);
    numSprite.position.y = 2.0;
    group.add(numSprite);

    // Selection ring
    const ringGeo = new THREE.RingGeometry(0.6, 0.75, 32);
    const ringMat = new THREE.MeshBasicMaterial({{ color: 0xffd700, transparent: true, opacity: 0 }});
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = -Math.PI / 2;
    ring.position.y = 0.03;
    group.add(ring);
    group.userData.ring = ring;

    group.position.set(data.position.x, 0, data.position.z);
    group.rotation.y = data.team === 'home' ? Math.PI / 2 : -Math.PI / 2;

    scene.add(group);
    playerMeshes.push(group);

    // Drag target (invisible cylinder)
    const dragTarget = new THREE.Mesh(
      new THREE.CylinderGeometry(0.5, 0.5, 2, 8),
      new THREE.MeshBasicMaterial({{ visible: false }})
    );
    dragTarget.position.copy(group.position);
    dragTarget.position.y = 1;
    dragTarget.userData = {{ id: data.id, type: 'player' }};
    scene.add(dragTarget);
    playerDragTargets.push(dragTarget);

    return group;
  }}

  playersData.forEach(p => createPlayer(p));

  // ===== BALL =====
  const ballGroup = new THREE.Group();
  ballGroup.userData = {{ id: 'ball', type: 'ball' }};
  const ballMesh = new THREE.Mesh(
    new THREE.SphereGeometry(0.22, 16, 16),
    new THREE.MeshStandardMaterial({{ color: 0xf0f0f0, roughness: 0.4 }})
  );
  ballGroup.add(ballMesh);

  // Ball pattern
  const patternMesh = new THREE.Mesh(
    new THREE.DodecahedronGeometry(0.18, 0),
    new THREE.MeshStandardMaterial({{ color: 0x333333, wireframe: true, transparent: true, opacity: 0.3 }})
  );
  ballGroup.add(patternMesh);

  // Ball shadow
  const shadowGeo = new THREE.CircleGeometry(0.2, 16);
  const shadowMat = new THREE.MeshBasicMaterial({{ color: 0x000000, transparent: true, opacity: 0.3 }});
  const ballShadow = new THREE.Mesh(shadowGeo, shadowMat);
  ballShadow.rotation.x = -Math.PI / 2;
  ballShadow.position.set(ballData.x, 0.02, ballData.z);
  scene.add(ballShadow);

  // Ball height line
  const heightLineGeo = new THREE.BufferGeometry();
  const heightLineMat = new THREE.LineBasicMaterial({{ color: 0x999999, transparent: true, opacity: 0.5 }});
  const heightLine = new THREE.Line(heightLineGeo, heightLineMat);
  scene.add(heightLine);

  // Ball selection ring
  const ballRingGeo = new THREE.RingGeometry(0.35, 0.45, 32);
  const ballRingMat = new THREE.MeshBasicMaterial({{ color: 0xffd700, transparent: true, opacity: 0 }});
  const ballRing = new THREE.Mesh(ballRingGeo, ballRingMat);
  ballRing.rotation.x = -Math.PI / 2;
  ballRing.position.y = 0.03;
  scene.add(ballRing);

  // Ball drag target
  const ballDragTarget = new THREE.Mesh(
    new THREE.SphereGeometry(0.5, 8, 8),
    new THREE.MeshBasicMaterial({{ visible: false }})
  );
  ballDragTarget.userData = {{ id: 'ball', type: 'ball' }};
  scene.add(ballDragTarget);

  ballGroup.position.set(ballData.x, ballData.y, ballData.z);
  scene.add(ballGroup);

  function updateBallVisuals() {{
    const p = ballGroup.position;
    ballShadow.position.set(p.x, 0.02, p.z);
    ballShadow.scale.setScalar(Math.max(0.1, 1 - p.y / 10));
    ballRing.position.set(p.x, 0.03, p.z);
    ballDragTarget.position.set(p.x, Math.max(0.5, p.y), p.z);

    if (p.y > 0.3) {{
      const pts = [new THREE.Vector3(p.x, 0.01, p.z), new THREE.Vector3(p.x, p.y, p.z)];
      heightLine.geometry.dispose();
      heightLine.geometry = new THREE.BufferGeometry().setFromPoints(pts);
      heightLine.visible = true;
    }} else {{
      heightLine.visible = false;
    }}
  }}
  updateBallVisuals();

  // ===== DRAG SYSTEM =====
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
  const intersection = new THREE.Vector3();
  let dragging = null;
  let selected = null;

  function selectObject(obj) {{
    if (selected) {{
      if (selected.type === 'player') {{
        const mesh = playerMeshes.find(m => m.userData.id === selected.id);
        if (mesh) mesh.userData.ring.material.opacity = 0;
      }} else {{
        ballRingMat.opacity = 0;
      }}
    }}
    selected = obj;
    if (selected) {{
      if (selected.type === 'player') {{
        const mesh = playerMeshes.find(m => m.userData.id === selected.id);
        if (mesh) mesh.userData.ring.material.opacity = 1;
      }} else {{
        ballRingMat.opacity = 1;
      }}
    }}
  }}

  function getMousePos(e) {{
    const rect = renderer.domElement.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
  }}

  renderer.domElement.addEventListener('pointerdown', (e) => {{
    if (e.button !== 0) return;
    getMousePos(e);
    raycaster.setFromCamera(mouse, camera);

    const targets = [...playerDragTargets, ballDragTarget];
    const hits = raycaster.intersectObjects(targets);
    if (hits.length > 0) {{
      const hit = hits[0].object;
      dragging = hit.userData;
      selectObject(dragging);
      controls.enabled = false;
    }} else {{
      selectObject(null);
    }}
  }});

  renderer.domElement.addEventListener('pointermove', (e) => {{
    if (!dragging) return;
    getMousePos(e);
    raycaster.setFromCamera(mouse, camera);
    raycaster.ray.intersectPlane(groundPlane, intersection);

    const x = Math.max(-HL, Math.min(HL, intersection.x));
    const z = Math.max(-HW, Math.min(HW, intersection.z));

    if (dragging.type === 'player') {{
      const mesh = playerMeshes.find(m => m.userData.id === dragging.id);
      const dragT = playerDragTargets.find(t => t.userData.id === dragging.id);
      if (mesh) {{
        mesh.position.x = x;
        mesh.position.z = z;
        mesh.userData.ring.position.set(0, 0.03, 0);
      }}
      if (dragT) {{
        dragT.position.x = x;
        dragT.position.z = z;
      }}
    }} else if (dragging.type === 'ball') {{
      ballGroup.position.x = x;
      ballGroup.position.z = z;
      updateBallVisuals();
    }}
  }});

  renderer.domElement.addEventListener('pointerup', () => {{
    if (dragging) {{
      dragging = null;
      controls.enabled = true;
    }}
  }});

  // ===== ANIMATION PLAYBACK =====
  let animFrames = [];
  let animPhase = 0;
  let animProgress = 0;
  let runPhases = {{}};

  if (framesData.length > 1) {{
    animFrames = framesData;
  }}

  function lerp(a, b, t) {{ return a + (b - a) * t; }}

  function updateAnimation(delta) {{
    if (!isPlaying || animFrames.length < 2) return;

    animProgress += delta * 0.5;
    if (animProgress >= 1) {{
      animProgress = 0;
      animPhase++;
      if (animPhase >= animFrames.length - 1) {{
        animPhase = 0;
        isPlaying = false;
        return;
      }}
    }}

    const from = animFrames[animPhase];
    const to = animFrames[animPhase + 1];

    from.players.forEach((fp, i) => {{
      const tp = to.players[i];
      const mesh = playerMeshes.find(m => m.userData.id === fp.id);
      if (mesh && tp) {{
        const nx = lerp(fp.position.x, tp.position.x, animProgress);
        const nz = lerp(fp.position.z, tp.position.z, animProgress);
        const dx = Math.abs(tp.position.x - fp.position.x);
        const dz = Math.abs(tp.position.z - fp.position.z);
        const moving = dx > 0.1 || dz > 0.1;

        mesh.position.x = nx;
        mesh.position.z = nz;

        if (moving) {{
          mesh.rotation.y = Math.atan2(tp.position.x - fp.position.x, tp.position.z - fp.position.z);
          runPhases[fp.id] = (runPhases[fp.id] || 0) + delta * 8;
          const swing = Math.sin(runPhases[fp.id]) * 0.8;
          mesh.userData.leftArm.rotation.x = -swing;
          mesh.userData.rightArm.rotation.x = swing;
          mesh.userData.leftLeg.rotation.x = swing;
          mesh.userData.rightLeg.rotation.x = -swing;
        }} else {{
          mesh.userData.leftArm.rotation.x = 0;
          mesh.userData.rightArm.rotation.x = 0;
          mesh.userData.leftLeg.rotation.x = 0;
          mesh.userData.rightLeg.rotation.x = 0;
        }}

        const dragT = playerDragTargets.find(t => t.userData.id === fp.id);
        if (dragT) {{ dragT.position.x = nx; dragT.position.z = nz; }}
      }}
    }});

    // Ball
    const fb = from.ball_position;
    const tb = to.ball_position;
    ballGroup.position.x = lerp(fb.x, tb.x, animProgress);
    ballGroup.position.z = lerp(fb.z, tb.z, animProgress);
    const baseY = lerp(fb.y, tb.y, animProgress);
    const maxH = Math.max(fb.y, tb.y);
    const arc = maxH > 0.5 ? Math.sin(animProgress * Math.PI) * maxH * 0.3 : 0;
    ballGroup.position.y = baseY + arc;
    updateBallVisuals();
  }}

  // ===== RENDER LOOP =====
  const clock = new THREE.Clock();
  function animate() {{
    requestAnimationFrame(animate);
    const delta = clock.getDelta();
    controls.update();
    updateAnimation(delta);
    renderer.render(scene, camera);
  }}
  animate();

  // Resize
  window.addEventListener('resize', () => {{
    const rw = window.innerWidth;
    const rh = window.innerHeight;
    camera.aspect = rw / rh;
    camera.updateProjectionMatrix();
    renderer.setSize(rw, rh);
  }});

}} catch (err) {{
  const errDiv = document.getElementById('error');
  if (errDiv) {{
    errDiv.style.display = 'block';
    errDiv.textContent = 'Three.js 로딩 실패: ' + err.message;
  }}
  console.error('Three.js error:', err);
}}
</script>
</body>
</html>
"""
