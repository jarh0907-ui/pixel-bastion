#!/usr/bin/env python3
"""PIXEL BASTION v0.4.4: BTD6-style inspector and 3-lane upgrade UI.
No new skill/upgrade rules. Existing defensive 1->3 upgrade stays usable.
All unconfirmed upgrade routes are disabled. No economic or combat changes.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1])
gp=root/'game.js';hp=root/'index.html';sp=root/'style.css'
s=gp.read_text(encoding='utf-8');h=hp.read_text(encoding='utf-8');c=sp.read_text(encoding='utf-8')
assert 'PIXEL BASTION v0.4.3' in s, 'Apply patch_v043.py first'
assert 'id="towerList" aria-label="전체 건설 타워와 시설"' in h
assert 'id="inspector"' in h

heading='<div class="panel-heading"><div><span class="tiny-rect amber"></span><b>건설 타워</b></div><span class="shortcut">선택 → 맵 배치</span></div>'
assert h.count(heading)==1, 'Sidebar title changed'
h=h.replace(heading,'''<div class="panel-heading tower-context-heading"><div><span class="tiny-rect amber"></span>
          <b class="palette-heading-label">건설 타워</b><b class="inspector-heading-label">타워 관리</b></div>
          <span class="shortcut palette-heading-label">선택 → 맵 배치</span>
          <button type="button" id="towerCatalogBtn" class="tower-catalog-back" aria-label="타워 건설 목록으로 돌아가기">◀ 목록</button>
        </div>''',1)

# Decorate the existing inspector instead of rewriting its worker/training controls.
# The original inspector still supplies the actual prices and actions.
anchor='  function updateUI(){'
assert s.count(anchor)==1
ui = r'''  // BTD6-style: selecting a tower replaces the build catalog with the tower
  // inspector. Switching back to the catalog does not restart or alter gameplay.
  const originalInspectorRender=updateInspector;
  updateInspector=function(){
    originalInspectorRender();
    const t=state.selection;
    const sidebar=ui.inspector.closest('.sidebar');
    if(sidebar)sidebar.classList.toggle('inspecting',!!t);
    if(!t||t.type==='villager')return;

    // Remove only old upgrade/evolution controls; retain combat sell, employee
    // assignment and knight training exactly as they previously behaved.
    for(const btn of Array.from(ui.inspector.querySelectorAll('button'))){
      if(btn.dataset.action==='upgrade' ||
          (btn.disabled&&/업그레이드|강화|진화/.test(btn.textContent))){
        const box=btn.closest('.inspector-actions');
        btn.remove();
        if(box&&!box.querySelector('button'))box.remove();
      }
    }
    const combat=!!TOWERS[t.type];
    const current=combat?towerStats(t):null;
    const max=combat&&t.level>=3;
    const next=combat&&!max?towerStats({...t,level:t.level+1}):null;
    const paths=[
      {n:1,name:combat?'기본 강화':'강화 경로 1',stage:combat?t.level:0,
        desc:combat?(max?'최대 레벨 도달':
          '공격 '+current.damage+' → '+next.damage+' · 사거리 '+current.range+' → '+next.range)
          :'효과 및 조건 미정'},
      {n:2,name:'강화 경로 2',stage:0,desc:'효과 및 조건 미정'},
      {n:3,name:'강화 경로 3',stage:0,desc:'효과 및 조건 미정'}
    ];
    const lanes=paths.map(path=>{
      const available=combat&&path.n===1;
      const markers=Array.from({length:3},(_,i)=>
        '<i class="route-node '+(i<path.stage?'owned':'')+'" aria-hidden="true"></i>').join('');
      const command=available?
        '<button type="button" class="route-button" data-action="upgrade" '+
        (max||state.gold<current.price?'disabled':'')+'>'+
        (max?'최고 레벨':'강화 ◆ '+current.price)+'</button>':
        '<span class="route-locked">🔒 미구현</span>';
      return '<div class="btd-route route-'+path.n+(available?' route-available':' route-disabled')+'">'+
          '<div class="route-top"><strong>'+path.name+'</strong><span class="route-grade">'+
          (available?path.stage+'/3':'잠금')+'</span></div>'+
          '<div class="route-progress">'+markers+'</div>'+
          '<p class="route-detail">'+path.desc+'</p>'+
          '<div class="route-bottom">'+command+'</div></div>';
    }).join('');
    const note=combat?
      '기존 1→3레벨 강화를 첫 번째 경로로 표시합니다. 두 번째와 세 번째 경로는 아직 설계되지 않았습니다.':
      '업그레이드 효과와 조건이 확정되지 않아 모든 경로를 잠가 두었습니다.';
    const panel='<section class="btd-upgrade-panel" aria-label="타워 업그레이드 경로">'+
      '<div class="btd-upgrade-heading"><strong>업그레이드</strong><span>3경로 UI</span></div>'+
      lanes+'<p class="route-disclaimer">'+note+'</p></section>';
    const stats=ui.inspector.querySelector('.inspector-stats');
    if(stats)stats.insertAdjacentHTML('afterend',panel);
    else ui.inspector.insertAdjacentHTML('beforeend',panel);
  };
  document.getElementById('towerCatalogBtn').addEventListener('click',()=>{
    state.selection=null;
    updateInspector();
    updateUI();
  });

'''
s=s.replace(anchor,ui+anchor,1)

c += '''
/* v0.4.4: BTD6-inspired selected-tower context and three-route upgrade view */
.tower-context-heading{min-height:48px}
.tower-catalog-back{display:none;font:800 12px sans-serif;color:#f0d5a0;
  background:#354743;border:2px solid #ac996c;border-radius:2px;
  padding:7px 10px;cursor:pointer;white-space:nowrap}
.tower-catalog-back:hover{background:#566045}
.sidebar:not(.inspecting) .inspector-heading-label,
.sidebar:not(.inspecting)>.section-title,
.sidebar:not(.inspecting)>.inspector,
.sidebar:not(.inspecting)>.side-note{display:none}
.sidebar.inspecting .palette-heading-label,
.sidebar.inspecting .tower-palette,
.sidebar.inspecting .palette-hint,
.sidebar.inspecting>.section-title,
.sidebar.inspecting>.side-note{display:none}
.sidebar.inspecting .tower-catalog-back{display:inline-flex}
.sidebar.inspecting>.inspector{display:block}
.sidebar.inspecting{align-self:start}
.sidebar.inspecting .inspector-title{margin-bottom:12px}
.btd-upgrade-panel{border-top:2px solid #5b655b;margin:13px -12px 0;padding:10px 12px 3px;
  background:#182e33}
.btd-upgrade-heading{display:flex;align-items:center;justify-content:space-between;
  gap:8px;color:#f4e4b8;margin:2px 0 10px}
.btd-upgrade-heading strong{font-size:14px}
.btd-upgrade-heading span{font:700 10px sans-serif;color:#a9bcb7}
.btd-route{position:relative;border:2px solid #4c6461;padding:9px 10px 10px;
  margin-bottom:9px;background:#253a3e;box-shadow:inset 0 -2px #182a30}
.btd-route.route-1{border-left:5px solid #d5a563}
.btd-route.route-2{border-left:5px solid #76a4c9}
.btd-route.route-3{border-left:5px solid #9eaa79}
.btd-route.route-disabled{background:#233239;border-color:#4b575b}
.btd-route.route-disabled.route-1{border-left-color:#d5a563}
.btd-route.route-disabled.route-2{border-left-color:#76a4c9}
.btd-route.route-disabled.route-3{border-left-color:#9eaa79}
.route-top{display:flex;justify-content:space-between;align-items:center;gap:6px}
.route-top strong{font-size:12px;color:#f0e4ce}
.route-grade{font:800 11px Consolas,monospace;color:#e9c47f}
.route-progress{display:grid;grid-template-columns:repeat(3,1fr);gap:4px;margin:8px 0}
.route-node{height:12px;background:#344b4d;border:1px solid #607478;
  box-shadow:inset 0 -2px #1b3033}
.route-node.owned{background:#d6ad64;border-color:#f5d496;box-shadow:inset 0 -2px #a0753e}
.route-detail{color:#a6bcb6;font-size:11px;line-height:1.5;margin:0 0 8px}
.route-bottom{display:flex;justify-content:flex-end;align-items:center}
.route-button{font:800 12px sans-serif;background:#d9b66e;color:#263126;
  border:2px solid #f6d997;padding:6px 11px;cursor:pointer;min-height:32px}
.route-button:hover:not(:disabled){background:#f2d88f}
.route-button:disabled{opacity:.52;cursor:not-allowed}
.route-locked{font:700 10px sans-serif;color:#a6aaa4;padding:5px 2px}
.route-disclaimer{margin:9px 1px 3px;color:#94aba7;font-size:10px;line-height:1.55}
.sidebar.inspecting .inspector-actions{margin:12px 0}
@media(min-width:931px) and (max-width:1150px){
  .sidebar.inspecting .inspector{padding:10px}
}
'''
assert 'function trainKnight(f)' in s
assert "function upgradeTower()" in s
assert "NPC_INTERACTIONS_ENABLED = false" in s
assert "KNIGHT_TRAIN_SECONDS=10" in s
s=s.replace('PIXEL BASTION v0.4.3','PIXEL BASTION v0.4.4',1)
h=h.replace('v0.4.3','v0.4.4')
gp.write_text(s,encoding='utf-8');hp.write_text(h,encoding='utf-8');sp.write_text(c,encoding='utf-8')
print('v0.4.4 BTD6-style contextual inspector; real tower upgrades retained, other routes locked')
