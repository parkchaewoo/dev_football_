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
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html, body {{ width:100%; height:100%; overflow:hidden; background:#1a1a2e; font-family:Arial,sans-serif; }}
  #viewport {{
    width:100%; height:100%;
    perspective: 900px;
    display:flex; align-items:center; justify-content:center;
    overflow:hidden;
  }}
  #scene {{
    transform-style: preserve-3d;
    transform: rotateX(55deg) rotateZ(0deg);
    position:relative;
    transition: transform 0.05s linear;
  }}
  #court {{
    position:relative;
    background: linear-gradient(180deg, #2d8a4e 0%, #258844 50%, #2d8a4e 100%);
    border: 2px solid rgba(255,255,255,0.8);
    border-radius: 4px;
    box-shadow: 0 0 60px rgba(0,0,0,0.5), 0 20px 40px rgba(0,0,0,0.3);
    transform-style: preserve-3d;
  }}
  /* Grass stripes */
  #court::before {{
    content:'';
    position:absolute; top:0; left:0; right:0; bottom:0;
    background: repeating-linear-gradient(
      90deg,
      transparent 0px, transparent 40px,
      rgba(255,255,255,0.025) 40px, rgba(255,255,255,0.025) 80px
    );
    pointer-events:none;
    border-radius:4px;
  }}
  .court-line {{
    position:absolute; background:rgba(255,255,255,0.8); pointer-events:none;
  }}
  .court-circle {{
    position:absolute; border:2px solid rgba(255,255,255,0.8);
    border-radius:50%; pointer-events:none;
  }}
  .goal {{
    position:absolute;
    transform-style: preserve-3d;
    pointer-events:none;
  }}
  .goal-frame {{
    position:absolute;
    background: rgba(200,200,200,0.9);
    border: 1px solid #aaa;
    transform-style: preserve-3d;
  }}
  .goal-net {{
    position:absolute;
    background: repeating-linear-gradient(
      45deg,
      transparent 0px, transparent 3px,
      rgba(255,255,255,0.15) 3px, rgba(255,255,255,0.15) 4px
    );
    border: 1px solid rgba(200,200,200,0.5);
  }}
  .goal-post {{
    position:absolute;
    background: linear-gradient(90deg, #ccc, #fff, #ccc);
    transform-origin: bottom center;
    transform: rotateX(-90deg);
    border-radius: 2px;
  }}
  .goal-bar {{
    position:absolute;
    background: linear-gradient(180deg, #ccc, #fff, #ccc);
    transform-origin: bottom center;
    transform: rotateX(-90deg);
    border-radius: 2px;
  }}
  .player {{
    position:absolute;
    transform-style: preserve-3d;
    cursor: grab;
    z-index: 10;
    user-select:none;
    -webkit-user-select:none;
  }}
  .player:active {{ cursor:grabbing; }}
  .player-shadow {{
    position:absolute;
    border-radius:50%;
    background: radial-gradient(ellipse, rgba(0,0,0,0.35) 0%, transparent 70%);
    pointer-events:none;
  }}
  .player-body {{
    position:absolute;
    transform-origin: bottom center;
    transform: rotateX(-90deg);
    transform-style: preserve-3d;
    pointer-events: none;
  }}
  .player-torso {{
    border-radius: 6px 6px 2px 2px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
  }}
  .player-head {{
    position:absolute;
    border-radius:50%;
    background: #f5d0a9;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  }}
  .player-number {{
    position:absolute;
    color:#fff; font-weight:bold; text-align:center;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
    pointer-events:none;
  }}
  .player-ring {{
    position:absolute;
    border: 3px solid #ffd700;
    border-radius: 50%;
    opacity: 0;
    pointer-events:none;
    box-shadow: 0 0 8px rgba(255,215,0,0.5);
  }}
  .player.selected .player-ring {{ opacity:1; }}
  .ball {{
    position:absolute;
    transform-style: preserve-3d;
    cursor:grab;
    z-index:9;
    user-select:none;
    -webkit-user-select:none;
  }}
  .ball:active {{ cursor:grabbing; }}
  .ball-shadow {{
    position:absolute;
    border-radius:50%;
    background: radial-gradient(ellipse, rgba(0,0,0,0.3) 0%, transparent 70%);
    pointer-events:none;
  }}
  .ball-sphere {{
    position:absolute;
    border-radius:50%;
    background: radial-gradient(circle at 35% 35%, #fff 0%, #e8e8e8 40%, #ccc 100%);
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    transform-origin: bottom center;
    transform: rotateX(-90deg);
    pointer-events:none;
    /* Pentagon pattern via box-shadow */
    border: 1px solid rgba(0,0,0,0.1);
  }}
  .ball-ring {{
    position:absolute;
    border: 2px solid #ffd700;
    border-radius:50%;
    opacity:0;
    pointer-events:none;
  }}
  .ball.selected .ball-ring {{ opacity:1; }}
  #info {{
    position:absolute; bottom:8px; left:50%;
    transform:translateX(-50%);
    color:rgba(255,255,255,0.6); font-size:11px;
    pointer-events:none; z-index:100;
    background:rgba(0,0,0,0.3);
    padding:4px 14px; border-radius:12px;
    white-space:nowrap;
  }}
</style>
</head>
<body>
<div id="viewport">
  <div id="scene">
    <div id="court"></div>
  </div>
</div>
<div id="info">드래그: 선수/공 이동 | 우클릭 드래그: 회전 | 스크롤: 줌</div>

<script>
(function() {{
  // ===== CONFIG =====
  const CW = 40, CH = 20;                // Court size in game units
  const SCALE = 14;                        // Pixels per game unit
  const PX_W = CW * SCALE, PX_H = CH * SCALE;
  const PENALTY_LEN = 6, PENALTY_W = 12, CENTER_R = 3;
  const GOAL_W = 3, GOAL_D = 1.5, GOAL_H_PX = 40;
  const P_SIZE = 28;                       // Player diameter in px
  const B_SIZE = 18;                       // Ball diameter in px

  let playersData = {players_json};
  let ballData = {ball_json};
  let framesData = {frames_data};
  let isPlaying = {'true' if is_playing else 'false'};

  const court = document.getElementById('court');
  const sceneEl = document.getElementById('scene');
  const viewport = document.getElementById('viewport');

  court.style.width = PX_W + 'px';
  court.style.height = PX_H + 'px';

  // ===== COURT MARKINGS =====
  function addLineH(x, y, w, h) {{
    const d = document.createElement('div');
    d.className = 'court-line';
    d.style.cssText = 'left:'+x+'px;top:'+y+'px;width:'+w+'px;height:'+(h||2)+'px;';
    court.appendChild(d);
  }}
  function addLineV(x, y, w, h) {{
    const d = document.createElement('div');
    d.className = 'court-line';
    d.style.cssText = 'left:'+x+'px;top:'+y+'px;width:'+(w||2)+'px;height:'+h+'px;';
    court.appendChild(d);
  }}

  // Center line
  addLineV(PX_W/2 - 1, 0, 2, PX_H);
  // Center circle
  const ccSize = CENTER_R * 2 * SCALE;
  const ccEl = document.createElement('div');
  ccEl.className = 'court-circle';
  ccEl.style.cssText = 'left:'+(PX_W/2 - ccSize/2)+'px;top:'+(PX_H/2 - ccSize/2)+'px;width:'+ccSize+'px;height:'+ccSize+'px;';
  court.appendChild(ccEl);
  // Center spot
  const spotEl = document.createElement('div');
  spotEl.style.cssText = 'position:absolute;left:'+(PX_W/2-4)+'px;top:'+(PX_H/2-4)+'px;width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,0.8);pointer-events:none;';
  court.appendChild(spotEl);
  // Penalty areas
  const penW = PENALTY_W * SCALE, penL = PENALTY_LEN * SCALE;
  // Left
  addLineH(0, (PX_H - penW)/2, penL, 2);
  addLineH(0, (PX_H + penW)/2, penL, 2);
  addLineV(penL, (PX_H - penW)/2, 2, penW);
  // Right
  addLineH(PX_W - penL, (PX_H - penW)/2, penL, 2);
  addLineH(PX_W - penL, (PX_H + penW)/2, penL, 2);
  addLineV(PX_W - penL, (PX_H - penW)/2, 2, penW);

  // ===== GOALS (3D upright) =====
  function addGoal(side) {{
    const gW = GOAL_W * SCALE;
    const gD = GOAL_D * SCALE;
    const g = document.createElement('div');
    g.className = 'goal';
    const gx = side === 'left' ? -gD : PX_W;
    g.style.cssText = 'left:'+gx+'px;top:'+(PX_H/2-gW/2)+'px;width:'+gD+'px;height:'+gW+'px;';

    // Net background
    const net = document.createElement('div');
    net.className = 'goal-net';
    net.style.cssText = 'left:0;top:0;width:'+gD+'px;height:'+gW+'px;';
    g.appendChild(net);

    // Left post (standing up in 3D)
    const lp = document.createElement('div');
    lp.className = 'goal-post';
    lp.style.cssText = 'left:' + (side==='left'?gD-3:0) + 'px;top:0;width:4px;height:'+GOAL_H_PX+'px;';
    g.appendChild(lp);
    // Right post
    const rp = document.createElement('div');
    rp.className = 'goal-post';
    rp.style.cssText = 'left:' + (side==='left'?gD-3:0) + 'px;top:'+(gW-4)+'px;width:4px;height:'+GOAL_H_PX+'px;';
    g.appendChild(rp);
    // Crossbar
    const bar = document.createElement('div');
    bar.className = 'goal-bar';
    bar.style.cssText = 'left:' + (side==='left'?gD-3:0) + 'px;top:0;width:4px;height:'+gW+'px;transform:rotateX(-90deg) translateZ(-'+(GOAL_H_PX-2)+'px);';
    g.appendChild(bar);

    court.appendChild(g);
  }}
  addGoal('left');
  addGoal('right');

  // ===== COORD CONVERSION =====
  // Game coords: x=[-20,20] (left-right), z=[-10,10] (top-bottom)
  function gameToPixel(gx, gz) {{
    return [PX_W/2 + gx * SCALE, PX_H/2 + gz * SCALE];
  }}
  function pixelToGame(px, py) {{
    return [(px - PX_W/2) / SCALE, (py - PX_H/2) / SCALE];
  }}

  // ===== CREATE PLAYERS =====
  const playerEls = [];

  function createPlayerEl(data) {{
    const isHome = data.team === 'home';
    const color = isHome ? '#e53e3e' : '#3b82f6';
    const darkColor = isHome ? '#c53030' : '#2563eb';

    const el = document.createElement('div');
    el.className = 'player';
    el.dataset.id = data.id;
    el.dataset.team = data.team;

    const [px, py] = gameToPixel(data.position.x, data.position.z);
    el.style.left = (px - P_SIZE/2) + 'px';
    el.style.top = (py - P_SIZE/2) + 'px';
    el.style.width = P_SIZE + 'px';
    el.style.height = P_SIZE + 'px';

    // Shadow on ground
    const shadow = document.createElement('div');
    shadow.className = 'player-shadow';
    shadow.style.cssText = 'left:-4px;top:2px;width:'+(P_SIZE+8)+'px;height:'+(P_SIZE*0.6)+'px;';
    el.appendChild(shadow);

    // 3D upright body
    const body = document.createElement('div');
    body.className = 'player-body';
    body.style.cssText = 'left:2px;bottom:0;width:'+(P_SIZE-4)+'px;height:'+(P_SIZE*1.6)+'px;';

    // Torso
    const torso = document.createElement('div');
    torso.className = 'player-torso';
    torso.style.cssText = 'position:absolute;bottom:0;left:0;width:100%;height:65%;background:linear-gradient(180deg,'+color+' 0%,'+darkColor+' 100%);';
    body.appendChild(torso);

    // Head
    const head = document.createElement('div');
    head.className = 'player-head';
    const headSize = P_SIZE * 0.5;
    head.style.cssText = 'top:0;left:50%;transform:translateX(-50%);width:'+headSize+'px;height:'+headSize+'px;';
    body.appendChild(head);

    el.appendChild(body);

    // Number (flat on ground, always readable)
    const num = document.createElement('div');
    num.className = 'player-number';
    num.style.cssText = 'left:0;top:0;width:'+P_SIZE+'px;height:'+P_SIZE+'px;line-height:'+P_SIZE+'px;font-size:'+(P_SIZE*0.45)+'px;';
    num.textContent = data.number;
    el.appendChild(num);

    // Selection ring
    const ring = document.createElement('div');
    ring.className = 'player-ring';
    ring.style.cssText = 'left:-6px;top:-6px;width:'+(P_SIZE+12)+'px;height:'+(P_SIZE+12)+'px;';
    el.appendChild(ring);

    court.appendChild(el);
    playerEls.push({{ el, data }});
  }}

  playersData.forEach(p => createPlayerEl(p));

  // ===== CREATE BALL =====
  const ballEl = document.createElement('div');
  ballEl.className = 'ball';
  ballEl.style.width = B_SIZE + 'px';
  ballEl.style.height = B_SIZE + 'px';

  const ballShadow = document.createElement('div');
  ballShadow.className = 'ball-shadow';
  ballShadow.style.cssText = 'left:-3px;top:2px;width:'+(B_SIZE+6)+'px;height:'+(B_SIZE*0.5)+'px;';
  ballEl.appendChild(ballShadow);

  const ballSphere = document.createElement('div');
  ballSphere.className = 'ball-sphere';
  ballSphere.style.cssText = 'left:0;bottom:0;width:'+B_SIZE+'px;height:'+(B_SIZE*1.4)+'px;';
  ballEl.appendChild(ballSphere);

  const ballRing = document.createElement('div');
  ballRing.className = 'ball-ring';
  ballRing.style.cssText = 'left:-5px;top:-5px;width:'+(B_SIZE+10)+'px;height:'+(B_SIZE+10)+'px;';
  ballEl.appendChild(ballRing);

  function updateBallPos() {{
    const [px, py] = gameToPixel(ballData.x, ballData.z);
    ballEl.style.left = (px - B_SIZE/2) + 'px';
    ballEl.style.top = (py - B_SIZE/2) + 'px';
  }}
  updateBallPos();
  court.appendChild(ballEl);

  // ===== DRAG SYSTEM =====
  let dragging = null;
  let dragOffset = {{ x:0, y:0 }};

  function getCourtPos(e) {{
    const rect = court.getBoundingClientRect();
    // Invert CSS 3D transform to get court-space coordinates
    const m = new DOMMatrix(getComputedStyle(sceneEl).transform);
    const inv = m.inverse();
    const vRect = viewport.getBoundingClientRect();
    // Point relative to viewport center
    const cx = e.clientX - vRect.left - vRect.width/2;
    const cy = e.clientY - vRect.top - vRect.height/2;
    // Apply inverse transform (simplified for rotateX only)
    const cosX = Math.cos(55 * Math.PI / 180);
    const py_court = cy / cosX;
    const px_court = cx;
    // Convert to court pixel coords
    const courtPx = PX_W/2 + px_court / currentZoom;
    const courtPy = PX_H/2 + py_court / currentZoom;
    return [courtPx, courtPy];
  }}

  court.addEventListener('pointerdown', (e) => {{
    if (e.button === 2) return; // right-click for rotation
    const target = e.target.closest('.player, .ball');
    if (!target) {{
      // Deselect
      document.querySelectorAll('.player.selected, .ball.selected').forEach(el => el.classList.remove('selected'));
      return;
    }}

    dragging = target;
    dragging.classList.add('selected');
    // Deselect others
    document.querySelectorAll('.player.selected, .ball.selected').forEach(el => {{
      if (el !== dragging) el.classList.remove('selected');
    }});

    court.setPointerCapture(e.pointerId);
    e.preventDefault();
  }});

  court.addEventListener('pointermove', (e) => {{
    if (!dragging) return;
    const [cpx, cpy] = getCourtPos(e);
    const [gx, gz] = pixelToGame(cpx, cpy);
    const clampedX = Math.max(-CW/2, Math.min(CW/2, gx));
    const clampedZ = Math.max(-CH/2, Math.min(CH/2, gz));

    if (dragging.classList.contains('player')) {{
      const pid = dragging.dataset.id;
      const pObj = playerEls.find(p => p.data.id === pid);
      if (pObj) {{
        pObj.data.position.x = clampedX;
        pObj.data.position.z = clampedZ;
        const [nx, ny] = gameToPixel(clampedX, clampedZ);
        dragging.style.left = (nx - P_SIZE/2) + 'px';
        dragging.style.top = (ny - P_SIZE/2) + 'px';
      }}
    }} else if (dragging.classList.contains('ball')) {{
      ballData.x = clampedX;
      ballData.z = clampedZ;
      updateBallPos();
    }}
  }});

  court.addEventListener('pointerup', () => {{
    dragging = null;
  }});

  // ===== CAMERA ROTATION (right-click drag) =====
  let rotX = 55, rotZ = 0;
  let currentZoom = 1;
  let isRotating = false;
  let rotStart = {{ x:0, y:0 }};

  viewport.addEventListener('contextmenu', e => e.preventDefault());

  viewport.addEventListener('pointerdown', (e) => {{
    if (e.button === 2) {{
      isRotating = true;
      rotStart = {{ x: e.clientX, y: e.clientY }};
      viewport.setPointerCapture(e.pointerId);
    }}
  }});

  viewport.addEventListener('pointermove', (e) => {{
    if (!isRotating) return;
    const dx = e.clientX - rotStart.x;
    const dy = e.clientY - rotStart.y;
    rotZ += dx * 0.3;
    rotX = Math.max(20, Math.min(80, rotX + dy * 0.3));
    rotStart = {{ x: e.clientX, y: e.clientY }};
    sceneEl.style.transform = 'rotateX('+rotX+'deg) rotateZ('+rotZ+'deg) scale('+currentZoom+')';
  }});

  viewport.addEventListener('pointerup', (e) => {{
    if (e.button === 2) isRotating = false;
  }});

  // Zoom
  viewport.addEventListener('wheel', (e) => {{
    e.preventDefault();
    currentZoom = Math.max(0.4, Math.min(2.5, currentZoom - e.deltaY * 0.001));
    sceneEl.style.transform = 'rotateX('+rotX+'deg) rotateZ('+rotZ+'deg) scale('+currentZoom+')';
  }}, {{ passive: false }});

  // Initial transform
  sceneEl.style.transform = 'rotateX('+rotX+'deg) rotateZ('+rotZ+'deg) scale('+currentZoom+')';

  // ===== ANIMATION PLAYBACK =====
  let animPhase = 0, animProgress = 0, lastTime = 0;

  function lerp(a, b, t) {{ return a + (b - a) * t; }}

  function updatePlayerPos(pData) {{
    const pObj = playerEls.find(p => p.data.id === pData.id);
    if (pObj) {{
      pObj.data.position.x = pData.position.x;
      pObj.data.position.z = pData.position.z;
      const [px, py] = gameToPixel(pData.position.x, pData.position.z);
      pObj.el.style.left = (px - P_SIZE/2) + 'px';
      pObj.el.style.top = (py - P_SIZE/2) + 'px';
    }}
  }}

  function animLoop(ts) {{
    if (!isPlaying || framesData.length < 2) return;
    if (!lastTime) lastTime = ts;
    const delta = (ts - lastTime) / 1000;
    lastTime = ts;

    animProgress += delta * 0.5;
    if (animProgress >= 1) {{
      animProgress = 0;
      animPhase++;
      if (animPhase >= framesData.length - 1) {{
        animPhase = 0;
        isPlaying = false;
        // Reset ball height visual
        ballSphere.style.height = (B_SIZE * 1.4) + 'px';
        ballSphere.style.bottom = '0px';
        ballShadow.style.opacity = '1';
        return;
      }}
    }}

    const from = framesData[animPhase];
    const to = framesData[animPhase + 1];

    // Interpolate players
    from.players.forEach((fp, i) => {{
      const tp = to.players[i];
      if (tp) {{
        const ix = lerp(fp.position.x, tp.position.x, animProgress);
        const iz = lerp(fp.position.z, tp.position.z, animProgress);
        updatePlayerPos({{ id: fp.id, position: {{ x: ix, z: iz }} }});
      }}
    }});

    // Interpolate ball
    const fb = from.ball_position;
    const tb = to.ball_position;
    ballData.x = lerp(fb.x, tb.x, animProgress);
    ballData.z = lerp(fb.z, tb.z, animProgress);
    updateBallPos();

    // Ball trajectory (parabolic = ball rises visually)
    const trajectory = to.ball_trajectory || "linear";
    const peakHeight = to.ball_peak_height || 0;
    let ballH = 0;

    if (trajectory === "parabolic" && peakHeight > 0) {{
      const t = animProgress;
      ballH = 2*(1-t)*t * peakHeight;
    }}

    // Visual ball height: scale sphere size and offset
    const hPx = ballH * SCALE * 0.5;
    ballSphere.style.height = (B_SIZE * 1.4 + hPx) + 'px';
    ballSphere.style.bottom = '0px';
    ballShadow.style.opacity = (1 - ballH * 0.1).toFixed(2);

    requestAnimationFrame(animLoop);
  }}

  if (isPlaying && framesData.length >= 2) {{
    lastTime = 0;
    animPhase = 0;
    animProgress = 0;
    requestAnimationFrame(animLoop);
  }}

}})();
</script>
</body>
</html>
"""
