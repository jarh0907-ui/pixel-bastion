#!/usr/bin/env python3
"""PIXEL BASTION v0.4.3: BTD6-like single right-side tower/building palette.

UI-only change: preserve every pre-existing button id, defensive tower data-tower,
its click delegation, active state, selected-building inspector and gameplay rules.
"""
from pathlib import Path
import re,sys

root=Path(sys.argv[1])
gp=root/'game.js'; hp=root/'index.html'; sp=root/'style.css'
s=gp.read_text(encoding='utf-8')
h=hp.read_text(encoding='utf-8')
c=sp.read_text(encoding='utf-8')
assert 'PIXEL BASTION v0.4.2' in s, 'Apply v0.4.2 first'
assert 'v0.4.2' in h
assert 'id="towerList"' in h
assert 'id="stageExpandBtn"' in h
assert 'id="inspector"' in h

start=h.index('      <aside class="sidebar">')
end=h.index('        <div class="section-title"><span>▸</span> 선택한 건물 / 주민</div>',start)
old=h[start:end]
entries=[
  ('arrow','방어'),('cannon','방어'),('frost','방어'),('flame','방어'),
  ('houseBuildBtn','주거'),('mineBuildBtn','경제'),('farmBuildBtn','경제'),
  ('trainingBuildBtn','군사'),('academyBuildBtn','군사')
]
built=[]
for name,group in entries:
    if name.endswith('Btn'):
        matcher=rf'<button\b[^>]*\bid="{name}"[^>]*>.*?</button>'
    else:
        matcher=rf'<button\b[^>]*\bdata-tower="{name}"[^>]*>.*?</button>'
    matches=re.findall(matcher,old,re.S)
    if len(matches)!=1:
        raise RuntimeError(f'expected 1 button for {name}, found {len(matches)}')
    button=matches[0].replace('class="tower-item"','class="tower-item palette-card"',1)
    button=button.replace('class="house-build"','class="house-build palette-card"',1)
    button=button.replace('<button ',f'<button title="{group} 타워 · 클릭해 배치" ',1)
    if group!='방어':
        button=button.replace('</button>','<span class="palette-cost-note">비용 미정</span></button>',1)
    built.append(button)
palette='''      <aside class="sidebar">
        <div class="panel-heading"><div><span class="tiny-rect amber"></span><b>건설 타워</b></div><span class="shortcut">선택 → 맵 배치</span></div>
        <div class="palette-hint">BTD6 방식 · 모든 시설을 오른쪽에서 선택</div>
        <div class="tower-palette" id="towerList" aria-label="전체 건설 타워와 시설">
'''+ '\n'.join('          '+button for button in built)+'''
          <p class="palette-summary" id="productionStatus">10초 생산 · 60초 식량 소비 · 민심 🔒 잠금</p>
        </div>
'''
h=h[:start]+palette+h[end:]
assert h.count('id="towerList"')==1
for name,group in entries:
    if name.endswith('Btn'): assert h.count('id="'+name+'"')==1
    else: assert h.count('data-tower="'+name+'"')==1

# New compact 3-column catalog. Original building-selection inspector stays
# below the catalog. Mobile stays touch-friendly; no fake new functional buttons.
c += '''
/* v0.4.3: integrated, always-visible right-side tower palette */
.sidebar .palette-hint{padding:8px 12px;background:#182c33;color:#b6c8b3;
  font-size:10px;border-bottom:1px solid #395154;letter-spacing:.2px}
.tower-palette{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));
  padding:12px;gap:8px;background:#1b3037;border-bottom:2px solid #30474b}
.tower-palette .palette-card{display:flex;flex-direction:column;justify-content:flex-start;
  align-items:center;text-align:center;gap:5px;padding:8px 3px;min-height:112px;
  min-width:0;width:100%;border:2px solid #51665e;background:#243b42;color:#f1e9d7;
  box-shadow:inset 0 -2px 0 #17282d;position:relative;transition:background .1s,border-color .1s}
.tower-palette .palette-card:hover{border-color:#d9bb79;background:#344e4a}
.tower-palette .palette-card[aria-pressed="true"],
.tower-palette .palette-card.selected{border-color:#ffdc8f;background:#5d5640;
  box-shadow:inset 0 0 0 2px #85734b}
.tower-palette .palette-card img{width:58px;height:58px;object-fit:contain;
  image-rendering:pixelated;flex:none}
.tower-palette .palette-card .tower-preview{width:58px;height:58px;font-size:30px;
  box-shadow:2px 2px #142329}
.tower-palette .palette-card .tower-info,
.tower-palette .palette-card>span:not(.price):not(.tower-preview):not(.palette-cost-note){
  width:100%;min-width:0;flex:none;display:block;text-align:center}
.tower-palette .palette-card strong{display:block;color:#f5ecd5;
  font-size:12px;font-weight:800;white-space:normal;line-height:1.22;word-break:keep-all}
.tower-palette .palette-card strong small,
.tower-palette .palette-card em,
.tower-palette .palette-card span small{display:none}
.tower-palette .palette-card .price,
.tower-palette .palette-card .palette-cost-note{font-size:10px;
  font-weight:800;color:#efcf8d;white-space:nowrap;line-height:1.25}
.tower-palette .palette-card .palette-cost-note{color:#aebdb6;font-weight:600}
.tower-palette .palette-card[data-tower]{border-bottom-color:#b88757}
.tower-palette #houseBuildBtn{border-bottom-color:#82b695}
.tower-palette #mineBuildBtn,.tower-palette #farmBuildBtn{border-bottom-color:#c7b17a}
.tower-palette #trainingBuildBtn,.tower-palette #academyBuildBtn{border-bottom-color:#83a9cc}
.tower-palette .palette-card:disabled{opacity:.52;cursor:not-allowed}
.tower-palette .palette-summary{grid-column:1/-1;margin:3px 0 0;
  padding:7px 5px;color:#9ab5aa;font-size:10px;text-align:center;
  border-top:1px solid #365354;line-height:1.45}
.sidebar>.section-title{background:#20363c}
@media(max-width:930px){.tower-palette{grid-template-columns:repeat(4,minmax(0,1fr))}}
@media(max-width:570px){.tower-palette{grid-template-columns:repeat(3,minmax(0,1fr));gap:7px;
  padding:9px}.tower-palette .palette-card{min-height:105px}}
'''
s=s.replace('PIXEL BASTION v0.4.2','PIXEL BASTION v0.4.3',1)
h=h.replace('v0.4.2','v0.4.3')
assert "ui.towerList.addEventListener('click'" in s
assert "ui.houseButton.addEventListener('click'" in s
assert "ui.mineBtn.addEventListener('click'" in s
assert "ui.trainingBtn.addEventListener('click'" in s
assert "function trainKnight(f)" in s
assert "NPC_INTERACTIONS_ENABLED = false" in s
gp.write_text(s,encoding='utf-8')
hp.write_text(h,encoding='utf-8')
sp.write_text(c,encoding='utf-8')
print('v0.4.3: 9 towers/facilities unified in existing right sidebar; original actions preserved')
