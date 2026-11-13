#!/usr/bin/env python3
"""PIXEL BASTION v0.4.0: placeable training ground and officer academy; training locked."""
from pathlib import Path
import sys
root=Path(sys.argv[1]); jp=root/'game.js';hp=root/'index.html';sp=root/'style.css'
s=jp.read_text(encoding='utf-8')
assert 'PIXEL BASTION v0.3.9' in s, 'Run patch_v039.py first'
assert 'NPC_INTERACTIONS_ENABLED = false' in s

def rep(old,new):
    global s
    n=s.count(old)
    if n!=1: raise RuntimeError('v0.4.0: expected one occurrence, got '+str(n)+': '+repr(old[:135]))
    s=s.replace(old,new,1)
rep('PIXEL BASTION v0.3.9','PIXEL BASTION v0.4.0')

rep('  const HOUSE_LIMIT = 3;', '''  // Military production facilities: building only. Unit rosters, costs and training remain locked.
  const FACILITY_DEFS={
    training:{label:'훈련장',width:3,height:2,drawW:172,drawH:173,url:'assets/reserve/training_ground_01.webp'},
    academy:{label:'사관학교',width:3,height:3,drawW:194,drawH:197,url:'assets/reserve/officer_academy_01.webp'}
  };
  const facilityArt={};
  function loadFacilityArt(){
    for(const [kind,def] of Object.entries(FACILITY_DEFS)){
      const im=new Image();im.onload=()=>{facilityArt[kind]=im;};im.src=def.url;
    }
  }
  const HOUSE_LIMIT = 3;''')
rep("    productionStatus: document.getElementById('productionStatus')", """    productionStatus: document.getElementById('productionStatus'),
    trainingBtn: document.getElementById('trainingBuildBtn'),
    academyBtn: document.getElementById('academyBuildBtn')""")
rep('economyBuildings:[],economySerial:0,food:0,productionClock:0,foodClock:0,',
    'economyBuildings:[],economySerial:0,facilityBuildings:[],facilitySerial:0,food:0,productionClock:0,foodClock:0,')
rep("    if(state.build)toast(state.build==='house'?'초가집 배치: 3×3 빈 지면을 클릭':TOWERS[state.build].label+' 배치: 원하는 지면을 클릭');", """    if(state.build){
      if(state.build==='house')toast('초가집 배치: 3×3 빈 지면을 클릭');
      else if(FACILITY_DEFS[state.build])toast(FACILITY_DEFS[state.build].label+' 배치: 빈 지면을 클릭 (훈련 기능 잠금)');
      else if(state.build==='mine'||state.build==='farm')toast(econLabel(state.build)+' 배치: 빈 지면을 클릭');
      else toast(TOWERS[state.build].label+' 배치: 원하는 지면을 클릭');
    }""")
# Building placement/selection, written separately from the economic worker model.
mark='  function homePopulation(home){'
assert s.count(mark)==1
helpers=r'''  function facilityDef(kind){return FACILITY_DEFS[kind];}
  function rectOverlap(ax,ay,aw,ah,bx,by,bw,bh){
    return ax<bx+bw&&ax+aw>bx&&ay<by+bh&&ay+ah>by;
  }
  function facilitySnap(kind,wx,wy){
    const d=facilityDef(kind),tx=Math.floor(wx/TILE)-Math.floor(d.width/2),
      ty=Math.floor(wy/TILE)-Math.floor(d.height/2);
    return {tx,ty,x:(tx+d.width/2)*TILE,y:(ty+d.height/2)*TILE};
  }
  function facilityPlaceError(kind,tx,ty){
    const d=facilityDef(kind);if(!d)return '알 수 없는 시설입니다.';
    if(tx<2||ty<2||tx+d.width>=MAP-2||ty+d.height>=MAP-2)
      return '월드 밖에는 건설할 수 없습니다.';
    const x=(tx+d.width/2)*TILE,y=(ty+d.height/2)*TILE;
    if(distance(x,y,C,C)<245||distance(x,y,C,C)>940)
      return '마을 건설 권역에 설치해 주세요.';
    for(let j=0;j<d.height;j++)for(let i=0;i<d.width;i++){
      const cell=tiles[key(tx+i,ty+j)];
      if(!cell||cell.obstacle||cell.terrain===5||cell.terrain===6)
        return '길·물·장애물이 없는 공간이 필요합니다.';
    }
    for(const h of state.houses)
      if(rectOverlap(tx,ty,d.width,d.height,h.tx,h.ty,3,3))return '초가집과 겹칩니다.';
    for(const b of state.economyBuildings)
      if(rectOverlap(tx,ty,d.width,d.height,b.tx,b.ty,ECON_WIDTH_TILES,ECON_HEIGHT_TILES))
        return '광산·밭과 겹칩니다.';
    for(const f of state.facilityBuildings){const fd=facilityDef(f.kind);
      if(rectOverlap(tx,ty,d.width,d.height,f.tx,f.ty,fd.width,fd.height))
        return '다른 군사 시설과 겹칩니다.';
    }
    for(const t of state.towers)
      if(t.x>(tx-1)*TILE&&t.x<(tx+d.width+1)*TILE&&
         t.y>(ty-1)*TILE&&t.y<(ty+d.height+1)*TILE)return '방어 타워와 겹칩니다.';
    for(const v of state.villagers){
      if(v.jobPhase==='inside'||v.jobPhase==='exiting')continue;
      for(const c of [v,...(v.moveTo?[v.moveTo]:[])])
        if(c.tx>=tx-1&&c.tx<tx+d.width+1&&c.ty>=ty-1&&c.ty<ty+d.height+1)
          return '주민이 서 있는 위치에는 건설할 수 없습니다.';
    }
    return '';
  }
  function buildFacility(kind,wx,wy){
    if(state.gameOver||!facilityDef(kind))return false;
    const p=facilitySnap(kind,wx,wy),err=facilityPlaceError(kind,p.tx,p.ty);
    if(err){toast(err);return false;}
    const f={id:++state.facilitySerial,type:'facility',kind,level:1,
      tx:p.tx,ty:p.ty,x:p.x,y:p.y};
    state.facilityBuildings.push(f);state.selection=f;state.build=null;
    spawnParticles(f.x,f.y,'#ebcf9e',14);
    toast(facilityDef(kind).label+' 건설 완료 · 훈련/업그레이드는 아직 잠금');
    updateUI();updateInspector();return true;
  }
  function drawFacility(f){
    const d=facilityDef(f.kind),im=facilityArt[f.kind],w=d.drawW,h=d.drawH;
    if(im)ctx.drawImage(im,Math.round(f.x-w/2),Math.round(f.y-h+35),w,h);
    else{ctx.fillStyle=f.kind==='academy'?'#52676c':'#886d4c';
      ctx.fillRect(f.x-w/2,f.y-h+35,w,h);}
    if(state.selection===f){
      ctx.strokeStyle='#f8d58e';ctx.lineWidth=2;
      ctx.strokeRect(f.tx*TILE,f.ty*TILE,d.width*TILE,d.height*TILE);
      ctx.fillStyle='#1f3139e8';ctx.fillRect(f.x-60,f.y-h+11,120,21);
      ctx.font='bold 12px sans-serif';ctx.textAlign='center';ctx.fillStyle='#f8e8bd';
      ctx.fillText(d.label+' · 훈련 잠금',f.x,f.y-h+26);
    }
  }
'''
s=s.replace(mark,helpers+mark,1)

# Prevent every existing build type from overlapping new facilities.
rep("  function canBuild(x,y) {", """  function canBuild(x,y) {
    for(const f of state.facilityBuildings){const d=facilityDef(f.kind);
      if(x>(f.tx-1)*TILE&&x<(f.tx+d.width+1)*TILE&&
         y>(f.ty-1)*TILE&&y<(f.ty+d.height+1)*TILE)
        return '훈련장·사관학교와 겹칩니다.';
    }""")
rep("  function canPlaceHouse(tx,ty){", """  function canPlaceHouse(tx,ty){
    for(const f of state.facilityBuildings){const d=facilityDef(f.kind);
      if(rectOverlap(tx,ty,3,3,f.tx,f.ty,d.width,d.height))
        return '훈련장·사관학교와 겹칩니다.';
    }""")
rep("  function econPlaceError(tx,ty){", """  function econPlaceError(tx,ty){
    for(const f of state.facilityBuildings){const d=facilityDef(f.kind);
      if(rectOverlap(tx,ty,ECON_WIDTH_TILES,ECON_HEIGHT_TILES,f.tx,f.ty,d.width,d.height))
        return '훈련장·사관학교와 겹칩니다.';
    }""")
rep("  function npcPassableCell(tx,ty){", """  function npcPassableCell(tx,ty){
    for(const f of state.facilityBuildings){const d=facilityDef(f.kind);
      if(tx>=f.tx&&tx<f.tx+d.width&&ty>=f.ty&&ty<f.ty+d.height)return false;
    }""")

# Draw with regular depth ordering and enable selection.
rep("    for(const e of state.economyBuildings)if(e.x>b.left-120&&e.x<b.right+120&&e.y>b.top-180&&e.y<b.bottom+140)all.push({y:e.y+48,kind:'economy',obj:e});", """    for(const e of state.economyBuildings)if(e.x>b.left-120&&e.x<b.right+120&&e.y>b.top-180&&e.y<b.bottom+140)all.push({y:e.y+48,kind:'economy',obj:e});
    for(const f of state.facilityBuildings)if(f.x>b.left-170&&f.x<b.right+170&&f.y>b.top-230&&f.y<b.bottom+140)all.push({y:f.y+48,kind:'facility',obj:f});""")
rep("      else if(entry.kind==='economy')drawEconomy(entry.obj);", """      else if(entry.kind==='economy')drawEconomy(entry.obj);
      else if(entry.kind==='facility')drawFacility(entry.obj);""")
rep("    for(const b of state.economyBuildings){miniCtx.fillStyle=b.kind==='mine'?'#a9a6a6':'#d2d16f';miniCtx.fillRect(b.x*sc-2,b.y*sc-2,5,5);}", """    for(const b of state.economyBuildings){miniCtx.fillStyle=b.kind==='mine'?'#a9a6a6':'#d2d16f';miniCtx.fillRect(b.x*sc-2,b.y*sc-2,5,5);}
    for(const f of state.facilityBuildings){miniCtx.fillStyle=f.kind==='training'?'#edb67b':'#98bde5';miniCtx.fillRect(f.x*sc-2,f.y*sc-2,5,5);}""")
rep("    if(state.build==='house'||state.build==='mine'||state.build==='farm'){", """    if(FACILITY_DEFS[state.build]){
      const d=facilityDef(state.build),p=facilitySnap(state.build,state.hover.x,state.hover.y);
      const valid=facilityPlaceError(state.build,p.tx,p.ty)==='';
      ctx.fillStyle=valid?'rgba(173,235,178,.23)':'rgba(249,103,99,.26)';
      ctx.fillRect(p.tx*TILE,p.ty*TILE,d.width*TILE,d.height*TILE);
      ctx.strokeStyle=valid?'#ebde9b':'#f59c87';ctx.lineWidth=3;
      ctx.strokeRect(p.tx*TILE,p.ty*TILE,d.width*TILE,d.height*TILE);
      const im=facilityArt[state.build];
      if(im){ctx.globalAlpha=.7;ctx.drawImage(im,Math.round(p.x-d.drawW/2),Math.round(p.y-d.drawH+35),d.drawW,d.drawH);ctx.globalAlpha=1;}
      return;
    }
    if(state.build==='house'||state.build==='mine'||state.build==='farm'){""")
rep("      else if(state.build==='mine'||state.build==='farm')buildEconomy(state.build,w.x,w.y);", """      else if(state.build==='mine'||state.build==='farm')buildEconomy(state.build,w.x,w.y);
      else if(FACILITY_DEFS[state.build])buildFacility(state.build,w.x,w.y);""")
rep("    if(!nearest){for(const b of state.economyBuildings){", """    if(!nearest){for(const f of state.facilityBuildings){
      const d=facilityDef(f.kind);
      if(Math.abs(w.x-f.x)<d.drawW/2&&w.y>f.y-d.drawH+27&&w.y<f.y+35){nearest=f;break;}
    }}
    if(!nearest){for(const b of state.economyBuildings){""")

# Read-only inspection. Costs and units are undecided, so no fake training buttons.
rep("    if(t.type==='economy'){", """    if(t.type==='facility'){
      const d=facilityDef(t.kind),tier=t.kind==='training'?'하급':'중급';
      ui.inspector.innerHTML=
        `<div class="inspector-title"><strong>${d.label}</strong><span class="level">군사 시설 · LV.1</span></div>
        <div class="inspector-stats"><div><span>건설 면적</span><strong>${d.width} × ${d.height}칸</strong></div>
        <div><span>훈련 등급</span><strong>${tier} 유닛</strong></div>
        <div><span>훈련 시스템</span><strong>준비 중</strong></div>
        <div><span>건설 비용</span><strong>미정 (현재 무료)</strong></div></div>
        <div class="inspector-actions"><button type="button" disabled>🔒 유닛 훈련 잠금</button>
        <button type="button" disabled>🔒 업그레이드 잠금</button></div>`;
      return;
    }
    if(t.type==='economy'){""")
rep("    ui.farmBtn.setAttribute('aria-pressed',String(state.build==='farm'));", """    ui.farmBtn.setAttribute('aria-pressed',String(state.build==='farm'));
    ui.trainingBtn.setAttribute('aria-pressed',String(state.build==='training'));
    ui.academyBtn.setAttribute('aria-pressed',String(state.build==='academy'));""")
rep("  ui.farmBtn.addEventListener('click',()=>selectBuild('farm'));", """  ui.farmBtn.addEventListener('click',()=>selectBuild('farm'));
  ui.trainingBtn.addEventListener('click',()=>selectBuild('training'));
  ui.academyBtn.addEventListener('click',()=>selectBuild('academy'));""")
rep("    else if(k==='7')selectBuild('farm');", """    else if(k==='7')selectBuild('farm');
    else if(k==='8')selectBuild('training');
    else if(k==='9')selectBuild('academy');""")
rep('generateWorld();loadSprites();loadNpcImages();loadEconomyArt();reset();',
    'generateWorld();loadSprites();loadNpcImages();loadEconomyArt();loadFacilityArt();reset();')
rep("    buildEconomy:(kind,x,y)=>buildEconomy(kind,x,y),", """    buildEconomy:(kind,x,y)=>buildEconomy(kind,x,y),
    buildFacility:(kind,x,y)=>buildFacility(kind,x,y),""")
rep("      economyBuildings:state.economyBuildings.map(b=>({id:b.id,kind:b.kind,level:b.level,workers:econCount(b),active:econActive(b),tx:b.tx,ty:b.ty,x:b.x,y:b.y})),", """      economyBuildings:state.economyBuildings.map(b=>({id:b.id,kind:b.kind,level:b.level,workers:econCount(b),active:econActive(b),tx:b.tx,ty:b.ty,x:b.x,y:b.y})),
      militaryFacilities:state.facilityBuildings.map(f=>({id:f.id,kind:f.kind,level:f.level,tx:f.tx,ty:f.ty,x:f.x,y:f.y,width:facilityDef(f.kind).width,height:facilityDef(f.kind).height})),""")

assert 'NPC_INTERACTIONS_ENABLED = false' in s
assert 'NPC_AUTO_CHAT_ENABLED = false' in s
assert 'ECON_WIDTH_TILES = 3, ECON_HEIGHT_TILES = 2' in s
jp.write_text(s,encoding='utf-8')

h=hp.read_text(encoding='utf-8')
assert 'v0.3.9' in h and 'id="mineBuildBtn"' in h
h=h.replace('v0.3.9','v0.4.0')
anchor='''          <p id="productionStatus">10초 생산 · 60초 식량 소비 · 민심 🔒 잠금</p>'''
assert h.count(anchor)==1
h=h.replace(anchor, anchor+'''
        </div>
        <div class="panel-heading"><div><span class="tiny-rect amber"></span><b>군사 훈련 시설</b></div><span class="shortcut">8 · 9</span></div>
        <div class="settlement-build economy-build">
          <button type="button" id="trainingBuildBtn" class="house-build" aria-pressed="false"><img src="assets/reserve/training_ground_01.webp" alt="훈련장"><span><strong>훈련장</strong><em>하급 유닛 훈련 시설</em><small>가로 3 × 세로 2칸 · 훈련 잠금</small></span></button>
          <button type="button" id="academyBuildBtn" class="house-build" aria-pressed="false"><img src="assets/reserve/officer_academy_01.webp" alt="사관학교"><span><strong>사관학교</strong><em>중급 유닛 훈련 시설</em><small>3×3칸 · 훈련 잠금</small></span></button>
        '''.rstrip(),1)
# Existing closure from the economic section remains exactly once.
h=h.replace('1~4: 방어 / 5: 집 / 6: 광산 / 7: 밭 / ESC: 취소',
            '1~4: 방어 / 5: 집 / 6: 광산 / 7: 밭 / 8: 훈련장 / 9: 사관학교 / ESC: 취소')
hp.write_text(h,encoding='utf-8')
st=sp.read_text(encoding='utf-8')
st+='\n/* v0.4.0 training facilities - buildable, unit training intentionally locked */\n'
sp.write_text(st,encoding='utf-8')
print('PIXEL BASTION v0.4.0: training ground 3x2, academy 3x3, no unit training enabled')