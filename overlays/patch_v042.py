#!/usr/bin/env python3
"""PIXEL BASTION v0.4.2: enlarge the playable game canvas without changing the world or rules."""
from pathlib import Path
import sys

root=Path(sys.argv[1])
game=root/'game.js'
html=root/'index.html'
css=root/'style.css'

s=game.read_text(encoding='utf-8')
h=html.read_text(encoding='utf-8')
c=css.read_text(encoding='utf-8')

assert 'PIXEL BASTION v0.4.1' in s, 'Run patch_v041.py first'
assert 'id="gameCanvas"' in h, 'Game canvas missing'
assert 'id="speedBtn"' in h, 'Game toolbar missing'
assert 'v0.4.1' in h, 'Expected existing display version'
assert 'stageExpandBtn' not in h and 'stageExpandBtn' not in s

s=s.replace('PIXEL BASTION v0.4.1','PIXEL BASTION v0.4.2',1)
h=h.replace('v0.4.1','v0.4.2')

# The regular game view is larger on desktop; optional focus mode uses the
# available page width for the game alone, with the existing sidebar restored
# at any time. This does not change the canvas resolution or world camera zoom.
needle='<button class="btn btn-minor" id="zoomOutBtn"'
assert h.count(needle)==1
h=h.replace(needle,
    '<button class="btn btn-minor" id="stageExpandBtn" type="button" aria-pressed="false" title="게임 화면을 크게 보기">⛶ 화면 크게</button>\n            '+needle,
    1)

needle="  ui.speedBtn.addEventListener('click',()=>{state.speed=state.speed===1?2:1;ui.speedBtn.textContent='▶ x'+state.speed;});"
assert s.count(needle)==1, 'Expected single speed control listener'
s=s.replace(needle,needle+"""
  // Focus mode changes layout only: preserve current progress, zoom, controls and inputs.
  const stageExpandBtn=document.getElementById('stageExpandBtn');
  stageExpandBtn.addEventListener('click',()=>{
    const app=document.querySelector('.app');
    const expanded=app.classList.toggle('play-focus');
    stageExpandBtn.setAttribute('aria-pressed',String(expanded));
    stageExpandBtn.textContent=expanded?'▣ 메뉴 보기':'⛶ 화면 크게';
    stageExpandBtn.title=expanded?'오른쪽 건설 메뉴 다시 표시':'게임 화면을 크게 보기';
  });""",1)

c += """
/* v0.4.2 — larger game field, same native canvas resolution and gameplay */
.app{width:min(1880px,calc(100% - 24px))}
.game-layout{grid-template-columns:minmax(0,1fr) 292px;gap:12px}
.board-section{min-width:0}
@media(min-width:1600px){.game-layout{grid-template-columns:minmax(0,1fr) 300px}}
@media(min-width:931px) and (max-width:1150px){.game-layout{grid-template-columns:minmax(0,1fr) 270px}}
@media(max-width:930px){.game-layout{grid-template-columns:minmax(0,1fr)}}
@media(max-width:570px){.app{width:calc(100% - 12px)}}
.app.play-focus .game-layout{grid-template-columns:minmax(0,1fr)}
.app.play-focus .sidebar{display:none}
#stageExpandBtn[aria-pressed="true"]{background:#46523c;border-color:#ecd392;color:#ffe2a0}
"""

assert "const KNIGHT_TRAIN_SECONDS=10" in s
assert "NPC_INTERACTIONS_ENABLED = false" in s
assert "id=\"stageExpandBtn\"" in h
game.write_text(s,encoding='utf-8')
html.write_text(h,encoding='utf-8')
css.write_text(c,encoding='utf-8')
print('PIXEL BASTION v0.4.2 — enlarged game canvas and optional focus mode enabled')
