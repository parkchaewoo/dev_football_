import json
from dataclasses import asdict
from typing import List, Optional
import streamlit.components.v1 as st_components
from utils.models import Player, Position3D


def render_tactical_board(
    players: List[Player],
    ball_position: Position3D,
    frames_data: Optional[list] = None,
    is_playing: bool = False,
    height: int = 600,
    key: str = "tactical_board",
) -> Optional[dict]:
    """2D Canvas 전술 보드를 렌더링합니다."""
    frames_json = json.dumps(frames_data) if frames_data else "[]"
    board_html = generate_board_html(
        players=players,
        ball_position=ball_position,
        frames_data=frames_json,
        is_playing=is_playing,
    )
    st_components.html(board_html, height=height, scrolling=False)
    return None


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
    background: #1a472a;
  }}
  canvas {{
    display: block;
    margin: 0 auto;
  }}
  #info {{
    position: absolute; bottom: 8px; left: 50%;
    transform: translateX(-50%);
    color: rgba(255,255,255,0.7); font: 12px sans-serif;
    pointer-events: none; z-index: 10;
    background: rgba(0,0,0,0.3);
    padding: 4px 12px; border-radius: 12px;
  }}
</style>
</head>
<body>
<canvas id="board"></canvas>
<div id="info">마우스 드래그: 선수/공 이동</div>

<script>
(function() {{
  const COURT_W = 40, COURT_H = 20;
  const PENALTY_LEN = 6, PENALTY_W = 12, CENTER_R = 3;
  const GOAL_W = 3, GOAL_D = 1.5;
  const PADDING = 30;
  const PLAYER_R = 14;
  const BALL_R = 9;

  let playersData = {players_json};
  let ballData = {ball_json};
  let framesData = {frames_data};
  let isPlaying = {'true' if is_playing else 'false'};

  const canvas = document.getElementById('board');
  const ctx = canvas.getContext('2d');

  let scale = 1;
  let offsetX = 0, offsetY = 0;

  function resize() {{
    const w = window.innerWidth;
    const h = window.innerHeight;
    canvas.width = w;
    canvas.height = h;

    const scaleX = (w - PADDING * 2) / COURT_W;
    const scaleY = (h - PADDING * 2) / COURT_H;
    scale = Math.min(scaleX, scaleY);
    offsetX = w / 2;
    offsetY = h / 2;
  }}

  // Convert court coords to canvas pixels
  function toCanvas(cx, cz) {{
    return [offsetX + cx * scale, offsetY + cz * scale];
  }}

  // Convert canvas pixels to court coords
  function toCourt(px, py) {{
    return [(px - offsetX) / scale, (py - offsetY) / scale];
  }}

  // ===== DRAWING =====
  function drawCourt() {{
    // Background
    ctx.fillStyle = '#2d8a4e';
    const [tlx, tly] = toCanvas(-COURT_W/2 - 2, -COURT_H/2 - 2);
    const [brx, bry] = toCanvas(COURT_W/2 + 2, COURT_H/2 + 2);
    ctx.fillRect(tlx, tly, brx - tlx, bry - tly);

    // Grass stripes
    ctx.fillStyle = 'rgba(255,255,255,0.03)';
    for (let i = -COURT_W/2; i < COURT_W/2; i += 4) {{
      if (Math.floor((i + COURT_W/2) / 4) % 2 === 0) {{
        const [sx, sy] = toCanvas(i, -COURT_H/2);
        const [ex, ey] = toCanvas(i + 4, COURT_H/2);
        ctx.fillRect(sx, sy, ex - sx, ey - sy);
      }}
    }}

    ctx.strokeStyle = 'rgba(255,255,255,0.85)';
    ctx.lineWidth = 2;

    // Boundary
    const [bx1, by1] = toCanvas(-COURT_W/2, -COURT_H/2);
    const [bx2, by2] = toCanvas(COURT_W/2, COURT_H/2);
    ctx.strokeRect(bx1, by1, bx2 - bx1, by2 - by1);

    // Center line
    const [cx1, cy1] = toCanvas(0, -COURT_H/2);
    const [cx2, cy2] = toCanvas(0, COURT_H/2);
    ctx.beginPath();
    ctx.moveTo(cx1, cy1);
    ctx.lineTo(cx2, cy2);
    ctx.stroke();

    // Center circle
    const [ccx, ccy] = toCanvas(0, 0);
    ctx.beginPath();
    ctx.arc(ccx, ccy, CENTER_R * scale, 0, Math.PI * 2);
    ctx.stroke();

    // Center spot
    ctx.fillStyle = 'rgba(255,255,255,0.85)';
    ctx.beginPath();
    ctx.arc(ccx, ccy, 3, 0, Math.PI * 2);
    ctx.fill();

    // Penalty areas
    ctx.strokeStyle = 'rgba(255,255,255,0.85)';
    const hpw = PENALTY_W / 2;
    // Left
    const [lp1x, lp1y] = toCanvas(-COURT_W/2, -hpw);
    const [lp2x, lp2y] = toCanvas(-COURT_W/2 + PENALTY_LEN, hpw);
    ctx.strokeRect(lp1x, lp1y, lp2x - lp1x, lp2y - lp1y);
    // Right
    const [rp1x, rp1y] = toCanvas(COURT_W/2 - PENALTY_LEN, -hpw);
    const [rp2x, rp2y] = toCanvas(COURT_W/2, hpw);
    ctx.strokeRect(rp1x, rp1y, rp2x - rp1x, rp2y - rp1y);

    // Goals
    ctx.lineWidth = 3;
    ctx.strokeStyle = '#ccc';
    ctx.fillStyle = 'rgba(255,255,255,0.1)';
    const hgw = GOAL_W / 2;
    // Left goal
    const [lg1x, lg1y] = toCanvas(-COURT_W/2 - GOAL_D, -hgw);
    const [lg2x, lg2y] = toCanvas(-COURT_W/2, hgw);
    ctx.fillRect(lg1x, lg1y, lg2x - lg1x, lg2y - lg1y);
    ctx.strokeRect(lg1x, lg1y, lg2x - lg1x, lg2y - lg1y);
    // Right goal
    const [rg1x, rg1y] = toCanvas(COURT_W/2, -hgw);
    const [rg2x, rg2y] = toCanvas(COURT_W/2 + GOAL_D, hgw);
    ctx.fillRect(rg1x, rg1y, rg2x - rg1x, rg2y - rg1y);
    ctx.strokeRect(rg1x, rg1y, rg2x - rg1x, rg2y - rg1y);

    ctx.lineWidth = 2;
  }}

  function drawPlayer(p, isSelected) {{
    const [px, py] = toCanvas(p.position.x, p.position.z);
    const isHome = p.team === 'home';
    const jerseyColor = isHome ? '#e53e3e' : '#3b82f6';
    const shortsColor = isHome ? '#1a1a2e' : '#e0e0e0';

    // Shadow
    ctx.fillStyle = 'rgba(0,0,0,0.2)';
    ctx.beginPath();
    ctx.ellipse(px + 2, py + 2, PLAYER_R, PLAYER_R * 0.7, 0, 0, Math.PI * 2);
    ctx.fill();

    // Selection ring
    if (isSelected) {{
      ctx.strokeStyle = '#ffd700';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(px, py, PLAYER_R + 5, 0, Math.PI * 2);
      ctx.stroke();
      ctx.lineWidth = 2;
    }}

    // Body circle (jersey)
    const grad = ctx.createRadialGradient(px - 3, py - 3, 2, px, py, PLAYER_R);
    grad.addColorStop(0, lightenColor(jerseyColor, 30));
    grad.addColorStop(1, jerseyColor);
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(px, py, PLAYER_R, 0, Math.PI * 2);
    ctx.fill();

    // Border
    ctx.strokeStyle = 'rgba(0,0,0,0.3)';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Direction indicator (small triangle)
    const dir = isHome ? 1 : -1;
    ctx.fillStyle = 'rgba(255,255,255,0.6)';
    ctx.beginPath();
    ctx.moveTo(px + dir * (PLAYER_R + 4), py);
    ctx.lineTo(px + dir * (PLAYER_R - 2), py - 4);
    ctx.lineTo(px + dir * (PLAYER_R - 2), py + 4);
    ctx.closePath();
    ctx.fill();

    // Number
    ctx.fillStyle = '#fff';
    ctx.font = 'bold ' + Math.max(11, PLAYER_R - 2) + 'px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.shadowColor = 'rgba(0,0,0,0.5)';
    ctx.shadowBlur = 2;
    ctx.fillText(p.number.toString(), px, py + 1);
    ctx.shadowBlur = 0;
  }}

  function drawBall(bx, bz, isSelected, height) {{
    const [px, py] = toCanvas(bx, bz);
    const displayR = BALL_R + (height || 0) * 2;

    // Shadow (offset more when ball is higher)
    const shadowOffset = (height || 0) * 3;
    ctx.fillStyle = 'rgba(0,0,0,0.25)';
    ctx.beginPath();
    ctx.ellipse(px + shadowOffset, py + shadowOffset, BALL_R * 0.8, BALL_R * 0.5, 0, 0, Math.PI * 2);
    ctx.fill();

    // Selection ring
    if (isSelected) {{
      ctx.strokeStyle = '#ffd700';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(px, py, displayR + 5, 0, Math.PI * 2);
      ctx.stroke();
      ctx.lineWidth = 2;
    }}

    // Ball
    const grad = ctx.createRadialGradient(px - 2, py - 2, 1, px, py, displayR);
    grad.addColorStop(0, '#ffffff');
    grad.addColorStop(0.7, '#e8e8e8');
    grad.addColorStop(1, '#cccccc');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(px, py, displayR, 0, Math.PI * 2);
    ctx.fill();

    // Pentagon pattern
    ctx.strokeStyle = 'rgba(0,0,0,0.15)';
    ctx.lineWidth = 1;
    for (let i = 0; i < 5; i++) {{
      const a = (i / 5) * Math.PI * 2 - Math.PI / 2;
      const r = displayR * 0.55;
      ctx.beginPath();
      ctx.moveTo(px, py);
      ctx.lineTo(px + Math.cos(a) * r, py + Math.sin(a) * r);
      ctx.stroke();
    }}

    // Border
    ctx.strokeStyle = 'rgba(0,0,0,0.3)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(px, py, displayR, 0, Math.PI * 2);
    ctx.stroke();
  }}

  function lightenColor(hex, amt) {{
    let r = parseInt(hex.slice(1,3), 16);
    let g = parseInt(hex.slice(3,5), 16);
    let b = parseInt(hex.slice(5,7), 16);
    r = Math.min(255, r + amt);
    g = Math.min(255, g + amt);
    b = Math.min(255, b + amt);
    return '#' + [r,g,b].map(c => c.toString(16).padStart(2,'0')).join('');
  }}

  function drawArrow(fromX, fromZ, toX, toZ, color) {{
    const [x1, y1] = toCanvas(fromX, fromZ);
    const [x2, y2] = toCanvas(toX, toZ);
    const dx = x2 - x1, dy = y2 - y1;
    const dist = Math.sqrt(dx*dx + dy*dy);
    if (dist < 5) return;

    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 4]);
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
    ctx.setLineDash([]);

    // Arrowhead
    const angle = Math.atan2(dy, dx);
    const headLen = 8;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(x2, y2);
    ctx.lineTo(x2 - headLen * Math.cos(angle - 0.4), y2 - headLen * Math.sin(angle - 0.4));
    ctx.lineTo(x2 - headLen * Math.cos(angle + 0.4), y2 - headLen * Math.sin(angle + 0.4));
    ctx.closePath();
    ctx.fill();
  }}

  // ===== STATE =====
  let dragging = null;
  let selected = null;
  let ballHeight = 0;

  // Animation state
  let animPhase = 0;
  let animProgress = 0;
  let lastTime = 0;

  function hitTest(canvasX, canvasY) {{
    // Check ball first
    const [bpx, bpy] = toCanvas(ballData.x, ballData.z);
    const bdx = canvasX - bpx, bdy = canvasY - bpy;
    if (bdx*bdx + bdy*bdy <= (BALL_R + 6) * (BALL_R + 6)) {{
      return {{ type: 'ball' }};
    }}

    // Check players (reverse order so top-drawn ones are checked first)
    for (let i = playersData.length - 1; i >= 0; i--) {{
      const p = playersData[i];
      const [ppx, ppy] = toCanvas(p.position.x, p.position.z);
      const pdx = canvasX - ppx, pdy = canvasY - ppy;
      if (pdx*pdx + pdy*pdy <= (PLAYER_R + 4) * (PLAYER_R + 4)) {{
        return {{ type: 'player', id: p.id, index: i }};
      }}
    }}
    return null;
  }}

  // ===== EVENTS =====
  canvas.addEventListener('pointerdown', (e) => {{
    if (e.button !== 0) return;
    const rect = canvas.getBoundingClientRect();
    const cx = e.clientX - rect.left;
    const cy = e.clientY - rect.top;

    const hit = hitTest(cx, cy);
    if (hit) {{
      dragging = hit;
      selected = hit;
      canvas.setPointerCapture(e.pointerId);
    }} else {{
      selected = null;
    }}
    draw();
  }});

  canvas.addEventListener('pointermove', (e) => {{
    if (!dragging) return;
    const rect = canvas.getBoundingClientRect();
    const cx = e.clientX - rect.left;
    const cy = e.clientY - rect.top;
    const [courtX, courtZ] = toCourt(cx, cy);

    const clampedX = Math.max(-COURT_W/2, Math.min(COURT_W/2, courtX));
    const clampedZ = Math.max(-COURT_H/2, Math.min(COURT_H/2, courtZ));

    if (dragging.type === 'player') {{
      const p = playersData[dragging.index];
      p.position.x = clampedX;
      p.position.z = clampedZ;
    }} else if (dragging.type === 'ball') {{
      ballData.x = clampedX;
      ballData.z = clampedZ;
    }}
    draw();
  }});

  canvas.addEventListener('pointerup', () => {{
    dragging = null;
  }});

  // ===== ANIMATION =====
  function lerp(a, b, t) {{ return a + (b - a) * t; }}

  function updateAnimation(timestamp) {{
    if (!isPlaying || framesData.length < 2) return false;

    if (!lastTime) lastTime = timestamp;
    const delta = (timestamp - lastTime) / 1000;
    lastTime = timestamp;

    animProgress += delta * 0.5;
    if (animProgress >= 1) {{
      animProgress = 0;
      animPhase++;
      if (animPhase >= framesData.length - 1) {{
        animPhase = 0;
        isPlaying = false;
        ballHeight = 0;
        return false;
      }}
    }}

    const from = framesData[animPhase];
    const to = framesData[animPhase + 1];

    // Interpolate players
    from.players.forEach((fp, i) => {{
      const tp = to.players[i];
      const pd = playersData.find(p => p.id === fp.id);
      if (pd && tp) {{
        pd.position.x = lerp(fp.position.x, tp.position.x, animProgress);
        pd.position.z = lerp(fp.position.z, tp.position.z, animProgress);
      }}
    }});

    // Interpolate ball
    const fb = from.ball_position;
    const tb = to.ball_position;
    ballData.x = lerp(fb.x, tb.x, animProgress);
    ballData.z = lerp(fb.z, tb.z, animProgress);

    // Ball trajectory
    const trajectory = to.ball_trajectory || "linear";
    const peakH = to.ball_peak_height || 0;
    if (trajectory === "parabolic" && peakH > 0) {{
      const t = animProgress;
      ballHeight = (1-t)*(1-t)*0 + 2*(1-t)*t*peakH + t*t*0;
    }} else {{
      ballHeight = 0;
    }}

    return true;
  }}

  function animLoop(timestamp) {{
    if (isPlaying) {{
      updateAnimation(timestamp);
      draw();
      requestAnimationFrame(animLoop);
    }}
  }}

  if (isPlaying && framesData.length >= 2) {{
    lastTime = 0;
    animPhase = 0;
    animProgress = 0;
    requestAnimationFrame(animLoop);
  }}

  // ===== MAIN DRAW =====
  function draw() {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Dark background
    ctx.fillStyle = '#1a472a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    drawCourt();

    // Draw movement arrows during animation
    if (isPlaying && framesData.length >= 2 && animPhase < framesData.length - 1) {{
      const to = framesData[animPhase + 1];
      framesData[animPhase].players.forEach((fp, i) => {{
        const tp = to.players[i];
        if (tp) {{
          const dx = Math.abs(tp.position.x - fp.position.x);
          const dz = Math.abs(tp.position.z - fp.position.z);
          if (dx > 0.3 || dz > 0.3) {{
            const color = fp.team === 'home' ? 'rgba(229,62,62,0.4)' : 'rgba(59,130,246,0.4)';
            drawArrow(fp.position.x, fp.position.z, tp.position.x, tp.position.z, color);
          }}
        }}
      }});
    }}

    // Draw players (home first, then away on top)
    const homePlayers = playersData.filter(p => p.team === 'home');
    const awayPlayers = playersData.filter(p => p.team === 'away');
    homePlayers.forEach(p => drawPlayer(p, selected && selected.type === 'player' && selected.id === p.id));
    awayPlayers.forEach(p => drawPlayer(p, selected && selected.type === 'player' && selected.id === p.id));

    // Draw ball
    drawBall(ballData.x, ballData.z, selected && selected.type === 'ball', ballHeight);
  }}

  // Init
  resize();
  draw();
  window.addEventListener('resize', () => {{ resize(); draw(); }});
}})();
</script>
</body>
</html>
"""
