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
    position:relative;
  }}
  #court {{
    position:relative;
    background: linear-gradient(180deg, #2d8a4e 0%, #258844 50%, #2d8a4e 100%);
    border: 2px solid rgba(255,255,255,0.8);
    border-radius: 4px;
    box-shadow: 0 0 60px rgba(0,0,0,0.5), 0 20px 40px rgba(0,0,0,0.3);
    transform-style: preserve-3d;
  }}
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
  /* === GPU-accelerated moving elements === */
  .player, .ball {{
    position:absolute;
    left:0; top:0;
    will-change: transform;
    transform-style: preserve-3d;
    cursor: grab;
    user-select:none;
    -webkit-user-select:none;
  }}
  .player {{ z-index:10; }}
  .ball {{ z-index:9; }}
  .player:active, .ball:active {{ cursor:grabbing; }}
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
    border-radius: 4px 4px 1px 1px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
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
    border: 2px solid #ffd700;
    border-radius: 50%;
    opacity: 0;
    pointer-events:none;
    box-shadow: 0 0 6px rgba(255,215,0,0.5);
    transition: opacity 0.15s;
  }}
  .player.selected .player-ring {{ opacity:1; }}
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
    border: 1px solid rgba(0,0,0,0.1);
  }}
  .ball-ring {{
    position:absolute;
    border: 2px solid #ffd700;
    border-radius:50%;
    opacity:0;
    pointer-events:none;
    transition: opacity 0.15s;
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
  /* Frame indicator */
  #frame-indicator {{
    position:absolute; top:8px; left:50%;
    transform:translateX(-50%);
    color:rgba(255,255,255,0.8); font-size:13px;
    pointer-events:none; z-index:100;
    background:rgba(0,0,0,0.5);
    padding:4px 16px; border-radius:12px;
    opacity:0; transition: opacity 0.3s;
  }}
  #frame-indicator.visible {{ opacity:1; }}
</style>
</head>
<body>
<div id="viewport">
  <div id="scene">
    <div id="court"></div>
  </div>
</div>
<div id="frame-indicator"></div>
<div id="info">드래그: 선수/공 이동 | 우클릭 드래그: 회전 | 스크롤: 줌</div>

<script>
(function() {{
  'use strict';

  // ===== CONFIG =====
  // Real futsal court: 40m x 20m
  // Player shoulder width ~0.5m, ball diameter ~0.21m
  const CW = 40, CH = 20;
  const SCALE = 18;                        // px per meter (court: 720x360px)
  const PX_W = CW * SCALE, PX_H = CH * SCALE;
  const PENALTY_LEN = 6, PENALTY_W = 12, CENTER_R = 3;
  const GOAL_W = 3, GOAL_D = 1.5, GOAL_H_PX = 36;  // 2m goal height
  const P_SIZE = 16;                       // ~0.9m footprint (slightly oversized for usability)
  const B_SIZE = 8;                        // ~0.44m (slightly oversized for visibility)
  const ANIM_SPEED = 0.6;  // frames per second transition

  let playersData = {players_json};
  let ballData = {ball_json};
  let framesData = {frames_data};
  let isPlaying = {'true' if is_playing else 'false'};

  const court = document.getElementById('court');
  const sceneEl = document.getElementById('scene');
  const viewport = document.getElementById('viewport');
  const frameInd = document.getElementById('frame-indicator');

  court.style.width = PX_W + 'px';
  court.style.height = PX_H + 'px';

  // ===== COURT MARKINGS =====
  function addLine(x, y, w, h) {{
    const d = document.createElement('div');
    d.className = 'court-line';
    d.style.cssText = 'left:'+x+'px;top:'+y+'px;width:'+w+'px;height:'+h+'px;';
    court.appendChild(d);
  }}

  addLine(PX_W/2-1, 0, 2, PX_H);  // center
  // Center circle
  const ccSize = CENTER_R * 2 * SCALE;
  const ccEl = document.createElement('div');
  ccEl.className = 'court-circle';
  ccEl.style.cssText = 'left:'+(PX_W/2-ccSize/2)+'px;top:'+(PX_H/2-ccSize/2)+'px;width:'+ccSize+'px;height:'+ccSize+'px;';
  court.appendChild(ccEl);
  // Center spot
  const spotEl = document.createElement('div');
  spotEl.style.cssText = 'position:absolute;left:'+(PX_W/2-4)+'px;top:'+(PX_H/2-4)+'px;width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,0.8);pointer-events:none;';
  court.appendChild(spotEl);
  // Penalty areas
  const penW = PENALTY_W * SCALE, penL = PENALTY_LEN * SCALE;
  addLine(0, (PX_H-penW)/2, penL, 2);
  addLine(0, (PX_H+penW)/2, penL, 2);
  addLine(penL, (PX_H-penW)/2, 2, penW);
  addLine(PX_W-penL, (PX_H-penW)/2, penL, 2);
  addLine(PX_W-penL, (PX_H+penW)/2, penL, 2);
  addLine(PX_W-penL, (PX_H-penW)/2, 2, penW);

  // ===== GOALS =====
  function addGoal(side) {{
    const gW = GOAL_W * SCALE;
    const gD = GOAL_D * SCALE;
    const g = document.createElement('div');
    g.className = 'goal';
    const gx = side === 'left' ? -gD : PX_W;
    g.style.cssText = 'left:'+gx+'px;top:'+(PX_H/2-gW/2)+'px;width:'+gD+'px;height:'+gW+'px;';
    const net = document.createElement('div');
    net.className = 'goal-net';
    net.style.cssText = 'left:0;top:0;width:'+gD+'px;height:'+gW+'px;';
    g.appendChild(net);
    const postX = side==='left' ? gD-3 : 0;
    const lp = document.createElement('div');
    lp.className = 'goal-post';
    lp.style.cssText = 'left:'+postX+'px;top:0;width:4px;height:'+GOAL_H_PX+'px;';
    g.appendChild(lp);
    const rp = document.createElement('div');
    rp.className = 'goal-post';
    rp.style.cssText = 'left:'+postX+'px;top:'+(gW-4)+'px;width:4px;height:'+GOAL_H_PX+'px;';
    g.appendChild(rp);
    const bar = document.createElement('div');
    bar.className = 'goal-bar';
    bar.style.cssText = 'left:'+postX+'px;top:0;width:4px;height:'+gW+'px;transform:rotateX(-90deg) translateZ(-'+(GOAL_H_PX-2)+'px);';
    g.appendChild(bar);
    court.appendChild(g);
  }}
  addGoal('left');
  addGoal('right');

  // ===== COORD HELPERS =====
  function gameToPixel(gx, gz) {{
    return [PX_W/2 + gx * SCALE, PX_H/2 + gz * SCALE];
  }}
  function pixelToGame(px, py) {{
    return [(px - PX_W/2) / SCALE, (py - PX_H/2) / SCALE];
  }}

  // ===== GPU-ACCELERATED POSITION UPDATE =====
  // Use translate3d instead of left/top for GPU compositing
  function setPos(el, px, py) {{
    el.style.transform = 'translate3d(' + px + 'px,' + py + 'px, 0)';
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
    el.style.width = P_SIZE + 'px';
    el.style.height = P_SIZE + 'px';

    // Initial position via translate3d
    const [px, py] = gameToPixel(data.position.x, data.position.z);
    setPos(el, px - P_SIZE/2, py - P_SIZE/2);

    // Shadow
    const shadow = document.createElement('div');
    shadow.className = 'player-shadow';
    shadow.style.cssText = 'left:-4px;top:2px;width:'+(P_SIZE+8)+'px;height:'+(P_SIZE*0.6)+'px;';
    el.appendChild(shadow);

    // 3D body
    const body = document.createElement('div');
    body.className = 'player-body';
    body.style.cssText = 'left:2px;bottom:0;width:'+(P_SIZE-4)+'px;height:'+(P_SIZE*1.6)+'px;';
    const torso = document.createElement('div');
    torso.className = 'player-torso';
    torso.style.cssText = 'position:absolute;bottom:0;left:0;width:100%;height:65%;background:linear-gradient(180deg,'+color+' 0%,'+darkColor+' 100%);';
    body.appendChild(torso);
    const head = document.createElement('div');
    head.className = 'player-head';
    const headSize = P_SIZE * 0.5;
    head.style.cssText = 'top:0;left:50%;transform:translateX(-50%);width:'+headSize+'px;height:'+headSize+'px;';
    body.appendChild(head);
    el.appendChild(body);

    // Number
    const num = document.createElement('div');
    num.className = 'player-number';
    num.style.cssText = 'left:0;top:0;width:'+P_SIZE+'px;height:'+P_SIZE+'px;line-height:'+P_SIZE+'px;font-size:'+(P_SIZE*0.45)+'px;';
    num.textContent = data.number;
    el.appendChild(num);

    // Ring
    const ring = document.createElement('div');
    ring.className = 'player-ring';
    ring.style.cssText = 'left:-6px;top:-6px;width:'+(P_SIZE+12)+'px;height:'+(P_SIZE+12)+'px;';
    el.appendChild(ring);

    court.appendChild(el);

    const pObj = {{
      el, data,
      // Cache current pixel position for smooth updates
      _px: px - P_SIZE/2,
      _py: py - P_SIZE/2,
    }};
    playerEls.push(pObj);
    return pObj;
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

  let ball_px = 0, ball_py = 0;
  function updateBallTransform(bx, bz) {{
    const [px, py] = gameToPixel(bx, bz);
    ball_px = px - B_SIZE/2;
    ball_py = py - B_SIZE/2;
    setPos(ballEl, ball_px, ball_py);
  }}
  updateBallTransform(ballData.x, ballData.z);
  court.appendChild(ballEl);

  // ===== DRAG SYSTEM =====
  let dragging = null;
  let rotX = 55, rotZ = 0, currentZoom = 1;

  function getCourtPos(e) {{
    // Use DOMMatrix to properly invert the 3D transform
    const vRect = viewport.getBoundingClientRect();
    const cx = e.clientX - vRect.left - vRect.width/2;
    const cy = e.clientY - vRect.top - vRect.height/2;
    // Invert using current rotation angles
    const cosX = Math.cos(rotX * Math.PI / 180);
    const cosZ = Math.cos(rotZ * Math.PI / 180);
    const sinZ = Math.sin(rotZ * Math.PI / 180);
    // Undo rotateZ then scale
    const ux = (cx * cosZ + cy * sinZ) / currentZoom;
    const uy = (-cx * sinZ + cy * cosZ) / currentZoom;
    // Undo rotateX (perspective division simplified)
    const courtPx = PX_W/2 + ux;
    const courtPy = PX_H/2 + uy / cosX;
    return [courtPx, courtPy];
  }}

  court.addEventListener('pointerdown', (e) => {{
    if (e.button !== 0) return;
    const target = e.target.closest('.player, .ball');
    if (!target) {{
      document.querySelectorAll('.player.selected, .ball.selected').forEach(el => el.classList.remove('selected'));
      return;
    }}
    dragging = target;
    dragging.classList.add('selected');
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
    const cx = Math.max(-CW/2, Math.min(CW/2, gx));
    const cz = Math.max(-CH/2, Math.min(CH/2, gz));

    if (dragging.classList.contains('player')) {{
      const pid = dragging.dataset.id;
      const pObj = playerEls.find(p => p.data.id === pid);
      if (pObj) {{
        pObj.data.position.x = cx;
        pObj.data.position.z = cz;
        const [nx, ny] = gameToPixel(cx, cz);
        pObj._px = nx - P_SIZE/2;
        pObj._py = ny - P_SIZE/2;
        setPos(dragging, pObj._px, pObj._py);
      }}
    }} else if (dragging.classList.contains('ball')) {{
      ballData.x = cx;
      ballData.z = cz;
      updateBallTransform(cx, cz);
    }}
  }});

  court.addEventListener('pointerup', () => {{ dragging = null; }});

  // ===== CAMERA ROTATION =====
  let isRotating = false;
  let rotStart = {{ x:0, y:0 }};

  function updateSceneTransform() {{
    sceneEl.style.transform = 'rotateX('+rotX+'deg) rotateZ('+rotZ+'deg) scale('+currentZoom+')';
  }}
  updateSceneTransform();

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
    updateSceneTransform();
  }});

  viewport.addEventListener('pointerup', (e) => {{
    if (e.button === 2) isRotating = false;
  }});

  viewport.addEventListener('wheel', (e) => {{
    e.preventDefault();
    currentZoom = Math.max(0.4, Math.min(2.5, currentZoom - e.deltaY * 0.001));
    updateSceneTransform();
  }}, {{ passive: false }});

  // ===== SMOOTH ANIMATION PLAYBACK =====
  let animPhase = 0, animProgress = 0, lastTime = 0;

  function lerp(a, b, t) {{ return a + (b - a) * t; }}

  // Ease-in-out for natural movement feel
  function easeInOut(t) {{
    return t < 0.5 ? 2*t*t : -1+(4-2*t)*t;
  }}

  function animLoop(ts) {{
    if (!isPlaying || framesData.length < 2) {{
      frameInd.classList.remove('visible');
      return;
    }}
    if (!lastTime) lastTime = ts;
    const delta = (ts - lastTime) / 1000;
    lastTime = ts;

    animProgress += delta * ANIM_SPEED;

    // Show frame indicator
    frameInd.textContent = 'Frame ' + (animPhase+1) + ' / ' + framesData.length;
    frameInd.classList.add('visible');

    if (animProgress >= 1) {{
      animProgress = 0;
      animPhase++;
      if (animPhase >= framesData.length - 1) {{
        // Snap to final frame
        const finalFrame = framesData[framesData.length - 1];
        finalFrame.players.forEach(fp => {{
          const pObj = playerEls.find(p => p.data.id === fp.id);
          if (pObj) {{
            const [px, py] = gameToPixel(fp.position.x, fp.position.z);
            pObj._px = px - P_SIZE/2;
            pObj._py = py - P_SIZE/2;
            setPos(pObj.el, pObj._px, pObj._py);
          }}
        }});
        updateBallTransform(finalFrame.ball_position.x, finalFrame.ball_position.z);

        animPhase = 0;
        isPlaying = false;
        frameInd.textContent = 'Complete';
        setTimeout(() => frameInd.classList.remove('visible'), 1500);
        return;
      }}
    }}

    const from = framesData[animPhase];
    const to = framesData[animPhase + 1];
    const t = easeInOut(animProgress);

    // Interpolate players (GPU-accelerated via translate3d)
    from.players.forEach((fp, i) => {{
      const tp = to.players[i];
      if (!tp) return;
      const pObj = playerEls.find(p => p.data.id === fp.id);
      if (!pObj) return;

      const ix = lerp(fp.position.x, tp.position.x, t);
      const iz = lerp(fp.position.z, tp.position.z, t);

      pObj.data.position.x = ix;
      pObj.data.position.z = iz;
      const [px, py] = gameToPixel(ix, iz);
      pObj._px = px - P_SIZE/2;
      pObj._py = py - P_SIZE/2;
      setPos(pObj.el, pObj._px, pObj._py);
    }});

    // Interpolate ball
    const fb = from.ball_position;
    const tb = to.ball_position;
    const bx = lerp(fb.x, tb.x, t);
    const bz = lerp(fb.z, tb.z, t);
    ballData.x = bx;
    ballData.z = bz;
    updateBallTransform(bx, bz);

    // Ball height (parabolic trajectory)
    const trajectory = to.ball_trajectory || "linear";
    const peakHeight = to.ball_peak_height || 0;
    let ballH = 0;

    if (trajectory === "parabolic" && peakHeight > 0) {{
      ballH = 4 * peakHeight * animProgress * (1 - animProgress);
    }} else {{
      ballH = lerp(fb.y || 0, tb.y || 0, t);
    }}

    // Visualize height: lift ball sphere, shrink shadow
    const hPx = ballH * SCALE * 0.5;
    if (hPx > 1) {{
      ballSphere.style.transform = 'rotateX(-90deg) translateY(-' + hPx + 'px)';
      ballShadow.style.opacity = Math.max(0.1, 1 - ballH * 0.15).toFixed(2);
      ballShadow.style.transform = 'scale(' + Math.max(0.3, 1 - ballH * 0.08).toFixed(2) + ')';
    }} else {{
      ballSphere.style.transform = 'rotateX(-90deg)';
      ballShadow.style.opacity = '1';
      ballShadow.style.transform = 'scale(1)';
    }}

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
