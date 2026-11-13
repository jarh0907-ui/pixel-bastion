#!/usr/bin/env python3
"""PIXEL BASTION v0.4.1: knight training at level-one training ground.

Run after patch_v040.py. Existing economy, villagers and academy are unchanged.
"""
from pathlib import Path
import re,sys
root=Path(sys.argv[1]);gp=root/'game.js';hp=root/'index.html'
s=gp.read_text(encoding='utf-8')
assert 'PIXEL BASTION v0.4.0' in s, 'Apply patch_v040.py first'

def rep(a,b):
    global s
    n=s.count(a)
    if n!=1: raise RuntimeError(f'v0.4.1 patch expected 1 instance, got {n}: {a[:155]!r}')
    s=s.replace(a,b,1)

rep('PIXEL BASTION v0.4.0','PIXEL BASTION v0.4.1')
rep('  const HOUSE_LIMIT = 3;', '''  // Prototype training cost and combat stats (final balance not decided).
  const KNIGHT_TRAIN_SECONDS=10,KNIGHT_GOLD_COST=10,KNIGHT_FOOD_COST=5;
  const KNIGHT_HP=80,KNIGHT_DAMAGE=20,KNIGHT_RANGE=38,KNIGHT_SPEED=68;
  const knightImages={};
  const KNIGHT_MOTIONS={idle:4,walk:4,attack:4,hit:2,death:4};
  function loadKnightArt(){
    for(const motion of Object.keys(KNIGHT_MOTIONS)){
      const img=new Image();
      img.onload=()=>{knightImages[motion]=img;};
      img.src='assets/units/KNIGHT/knight_'+motion+'_4dir.webp';
    }
  }
  const HOUSE_LIMIT = 3;''')
rep('facilityBuildings:[],facilitySerial:0,food:0,productionClock:0,foodClock:0,',
    'facilityBuildings:[],facilitySerial:0,trainedUnits:[],trainedSerial:0,food:0,productionClock:0,foodClock:0,')
rep('tx:p.tx,ty:p.ty,x:p.x,y:p.y};\n    state.facilityBuildings.push(f);',
    'tx:p.tx,ty:p.ty,x:p.x,y:p.y,trainingActive:false,trainingRemaining:0,trainingReady:false};\n    state.facilityBuildings.push(f);')

# Guards and production operate on a dedicated roster, not villager population.
marker='  function homePopulation(home){'
assert s.count(marker)==1
helpers=r'''  function knightSpawnTile(f){
    const d=facilityDef(f.kind),candidates=[];
    for(let x=f.tx;x<f.tx+d.width;x++){
      candidates.push({tx:x,ty:f.ty+d.height},{tx:x,ty:f.ty-1});
    }
    for(let y=f.ty;y<f.ty+d.height;y++){
      candidates.push({tx:f.tx-1,ty:y},{tx:f.tx+d.width,ty:y});
    }
    return candidates.find(c=>npcPassableCell(c.tx,c.ty)&&!tileReserved(c.tx,c.ty)&&
      !state.trainedUnits.some(u=>u.mode!=='death'&&u.tx===c.tx&&u.ty===c.ty))||null;
  }
  function trainKnight(f){
    if(!f||f.kind!=='training'||state.paused||state.gameOver)return false;
    if(f.trainingActive){toast('이 훈련장에서는 이미 기사를 훈련하고 있습니다.');return false;}
    if(state.gold<KNIGHT_GOLD_COST){toast('골드 부족: 기사 훈련에는 '+KNIGHT_GOLD_COST+'골드가 필요합니다.');return false;}
    if(state.food<KNIGHT_FOOD_COST){toast('식량 부족: 기사 훈련에는 식량 '+KNIGHT_FOOD_COST+'개가 필요합니다.');return false;}
    state.gold-=KNIGHT_GOLD_COST;state.food-=KNIGHT_FOOD_COST;
    f.trainingActive=true;f.trainingRemaining=KNIGHT_TRAIN_SECONDS;f.trainingReady=false;
    toast('기사 훈련 시작! · 10초');
    updateUI();updateInspector();return true;
  }
  function stepKnightTraining(dt){
    for(const f of state.facilityBuildings){
      if(f.kind!=='training'||!f.trainingActive)continue;
      if(f.trainingRemaining>0){
        const old=Math.ceil(f.trainingRemaining);
        f.trainingRemaining=Math.max(0,f.trainingRemaining-dt);
        if(state.selection===f&&old!==Math.ceil(f.trainingRemaining))updateInspector();
      }
      if(f.trainingRemaining>0)continue;
      f.trainingReady=true;
      const exit=knightSpawnTile(f);
      if(!exit)continue; // Keep completed training until a safe exit becomes available.
      const u={id:++state.trainedSerial,type:'knight',homeFacilityId:f.id,
        tx:exit.tx,ty:exit.ty,x:cellX(exit.tx),y:cellY(exit.ty),dir:'down',
        hp:KNIGHT_HP,maxHp:KNIGHT_HP,mode:'idle',animTime:0,
        actionTime:0,attackCooldown:.5,damageCooldown:1.2,deathTime:0};
      state.trainedUnits.push(u);
      f.trainingActive=false;f.trainingReady=false;f.trainingRemaining=0;
      spawnParticles(u.x,u.y-22,'#e6c98b',16);
      floating(u.x,u.y-84,'기사 훈련 완료!','#ffe6a4');
      toast('훈련장에서 기사가 배치되었습니다.');
      if(state.selection===f)updateInspector();
      updateUI();
    }
  }
  function stepKnightUnits(dt){
    for(const u of state.trainedUnits){
      u.animTime+=dt;
      if(u.mode==='death'){
        u.deathTime+=dt;continue;
      }
      u.attackCooldown=Math.max(0,u.attackCooldown-dt);
      u.damageCooldown=Math.max(0,u.damageCooldown-dt);
      if(u.actionTime>0){
        u.actionTime=Math.max(0,u.actionTime-dt);
        if(!u.actionTime)u.mode='idle';
        continue;
      }
      let target=null,best=240;
      for(const e of state.enemies){
        if(e.dead)continue;
        const dist=distance(u.x,u.y,e.x,e.y);
        if(dist<best){best=dist;target=e;}
      }
      if(!target){u.mode='idle';continue;}
      const dx=target.x-u.x,dy=target.y-u.y,d=Math.hypot(dx,dy);
      u.dir=Math.abs(dx)>Math.abs(dy)?(dx<0?'left':'right'):(dy<0?'up':'down');
      if(d>KNIGHT_RANGE){
        const move=Math.min(d-KNIGHT_RANGE,KNIGHT_SPEED*dt);
        const nx=u.x+dx/d*move,ny=u.y+dy/d*move;
        const tx=Math.floor(nx/TILE),ty=Math.floor(ny/TILE);
        if(npcPassableCell(tx,ty)&&!state.trainedUnits.some(other=>other!==u&&other.mode!=='death'&&distance(nx,ny,other.x,other.y)<23)){
          u.x=nx;u.y=ny;u.tx=tx;u.ty=ty;u.mode='walk';
        }else u.mode='idle';
      }else{
        u.mode='idle';
        if(u.attackCooldown<=0){
          u.mode='attack';u.animTime=0;u.actionTime=.48;u.attackCooldown=1.3;
          damageEnemy(target,KNIGHT_DAMAGE);
          spawnParticles(target.x,target.y-12,'#e5bd83',4);
        }
        // Temporary contact retaliation. Can be replaced by later combat rules.
        if(u.damageCooldown<=0){
          u.hp-=8;u.damageCooldown=1.5;
          if(u.hp<=0){u.hp=0;u.mode='death';u.animTime=0;u.deathTime=0;
            floating(u.x,u.y-65,'기사 전사','#e79f90');}
          else if(u.mode!=='attack'){
            u.mode='hit';u.animTime=0;u.actionTime=.28;
          }
        }
      }
    }
    state.trainedUnits=state.trainedUnits.filter(u=>u.mode!=='death'||u.deathTime<1.25);
  }
  function drawKnight(u){
    const motion=u.mode,im=knightImages[motion]||knightImages.idle;
    const row={down:0,up:1,left:2,right:3}[u.dir]||0;
    const count=KNIGHT_MOTIONS[motion]||4;
    const frame=Math.min(count-1,Math.floor(u.animTime*(motion==='attack'?8:motion==='walk'?6:motion==='death'?3.2:4))%count);
    ctx.fillStyle='#18272266';ctx.beginPath();ctx.ellipse(u.x,u.y-1,17,5,0,0,Math.PI*2);ctx.fill();
    if(im&&im.complete&&im.naturalWidth){
      // Crop shared transparent padding, anchor the feet and retain original pixel colors.
      ctx.drawImage(im,frame*160+5,row*176+26,150,140,
        Math.round(u.x-50),Math.round(u.y-95),100,95);
    }else{
      ctx.fillStyle='#3c4353';ctx.fillRect(u.x-14,u.y-53,28,45);
      ctx.fillStyle='#e5cca6';ctx.fillRect(u.x-10,u.y-76,20,24);
    }
    if(motion!=='death'){
      const w=40;
      ctx.fillStyle='#172729';ctx.fillRect(u.x-w/2,u.y-103,w,6);
      ctx.fillStyle='#8dc4a1';ctx.fillRect(u.x-w/2+1,u.y-102,Math.round((w-2)*Math.max(0,u.hp)/u.maxHp),4);
    }
  }
'''
s=s.replace(marker,helpers+marker,1)

# In combat, time-scaled tick() runs only when not paused. Training also respects 2x speed.
# Training continues during peaceful periods between waves; the combat tick() is active-wave-only.
# World animation (including working mines/farms) must tick between combat waves too.
rep('    state.elapsed+=dt;\n    if(state.spawnQueue.length){',
    '    if(state.spawnQueue.length){')
rep('      const dt=realDt*state.speed;\n      if(state.active)tick(dt);',
    '      const dt=realDt*state.speed;\n      state.elapsed+=dt;\n      if(state.active)tick(dt);')
rep('      stepEconomy(dt);',
    '      stepEconomy(dt);\n      stepKnightTraining(dt);\n      stepKnightUnits(dt);')

# Insert knight into established world depth sorting and minimap without affecting NPCs.
world_anchor="    for(const f of state.facilityBuildings)if(f.x>b.left-170&&f.x<b.right+170&&f.y>b.top-230&&f.y<b.bottom+140)all.push({y:f.y+48,kind:'facility',obj:f});"
rep(world_anchor, world_anchor+"\n    for(const u of state.trainedUnits)if(u.x>b.left-100&&u.x<b.right+100&&u.y>b.top-130&&u.y<b.bottom+100)all.push({y:u.y,kind:'knight',obj:u});")
rep("      else if(entry.kind==='facility')drawFacility(entry.obj);",
    "      else if(entry.kind==='facility')drawFacility(entry.obj);\n      else if(entry.kind==='knight')drawKnight(entry.obj);")
rep("    for(const f of state.facilityBuildings){miniCtx.fillStyle=f.kind==='training'?'#edb67b':'#98bde5';miniCtx.fillRect(f.x*sc-2,f.y*sc-2,5,5);}",
    "    for(const f of state.facilityBuildings){miniCtx.fillStyle=f.kind==='training'?'#edb67b':'#98bde5';miniCtx.fillRect(f.x*sc-2,f.y*sc-2,5,5);}\n    for(const u of state.trainedUnits){if(u.mode==='death')continue;miniCtx.fillStyle='#d1f5a5';miniCtx.fillRect(u.x*sc-1,u.y*sc-1,3,3);}")

# Show real-time training bar directly above the sprite, using the existing facility rendering.
start=s.index('  function drawFacility(f){')
end=s.index('  function homePopulation(home){',start)
part=s[start:end]
needle="    if(state.selection===f){"
assert part.count(needle)==1
part=part.replace(needle,'''    if(f.kind==='training'&&f.trainingActive){
      const bx=f.x-62,by=f.y-h-15;
      const fill=1-f.trainingRemaining/KNIGHT_TRAIN_SECONDS;
      ctx.fillStyle='#142e35e8';ctx.fillRect(bx,by,124,22);
      ctx.fillStyle='#e1b768';ctx.fillRect(bx+3,by+16,Math.round(118*Math.min(1,fill)),3);
      ctx.font='bold 12px sans-serif';ctx.fillStyle='#f7e8be';ctx.textAlign='center';
      ctx.fillText(f.trainingReady?'출구 대기':'기사 훈련 '+Math.ceil(f.trainingRemaining)+'초',f.x,by+12);
    }
''' +needle,1)
s=s[:start]+part+s[end:]

# Training ground activates the first unit; academy is intentionally still locked.
needle="    if(t.type==='facility'){"
assert s.count(needle)==1
s=s.replace(needle,'''    if(t.type==='facility'&&t.kind==='training'){
      const busy=t.trainingActive,remaining=busy?Math.ceil(t.trainingRemaining):0;
      ui.inspector.innerHTML=`<div class="inspector-title"><strong>훈련장</strong><span class="level">하급 병력 · LV.1</span></div>
        <div class="inspector-stats"><div><span>훈련 가능한 유닛</span><strong>기사</strong></div>
        <div><span>훈련 시간</span><strong>10초</strong></div>
        <div><span>훈련 비용 (임시)</span><strong>10 골드 · 5 식량</strong></div>
        <div><span>현재 상태</span><strong>${busy?(t.trainingReady?'출구 대기':'훈련 중 · '+remaining+'초'):'훈련 가능'}</strong></div></div>
        <div class="inspector-actions"><button type="button" data-action="train-knight" ${busy||state.paused?'disabled':''}>⚔ 기사 훈련 (10초)</button>
        <button type="button" disabled>🔒 업그레이드 잠금</button></div>
        <p class="npc-hint">기사 기본 전투 수치는 임시입니다. 훈련은 게임 시간으로 진행됩니다.</p>`;
      return;
    }
''' +needle,1)
rep("    if(button.dataset.action==='econ-assign'&&state.selection&&state.selection.type==='economy')selectEmployee(state.selection);",
    "    if(button.dataset.action==='train-knight'&&state.selection?.type==='facility')trainKnight(state.selection);\n    if(button.dataset.action==='econ-assign'&&state.selection&&state.selection.type==='economy')selectEmployee(state.selection);")
rep('generateWorld();loadSprites();loadNpcImages();loadEconomyArt();loadFacilityArt();reset();',
    'generateWorld();loadSprites();loadNpcImages();loadEconomyArt();loadFacilityArt();loadKnightArt();reset();')
rep('    buildFacility:(kind,x,y)=>buildFacility(kind,x,y),',
    '''    buildFacility:(kind,x,y)=>buildFacility(kind,x,y),
    trainKnight:(id)=>{const f=state.facilityBuildings.find(f=>f.id===id);return f?trainKnight(f):false;},''')
needle="      militaryFacilities:state.facilityBuildings.map(f=>({id:f.id,kind:f.kind,level:f.level,tx:f.tx,ty:f.ty,x:f.x,y:f.y,width:facilityDef(f.kind).width,height:facilityDef(f.kind).height})),"
assert s.count(needle)==1
s=s.replace(needle,"      militaryFacilities:state.facilityBuildings.map(f=>({id:f.id,kind:f.kind,level:f.level,tx:f.tx,ty:f.ty,x:f.x,y:f.y,width:facilityDef(f.kind).width,height:facilityDef(f.kind).height,trainingActive:f.trainingActive,trainingRemaining:f.trainingRemaining,trainingReady:f.trainingReady})),\n      knightCount:state.trainedUnits.filter(u=>u.mode!=='death').length,\n      knights:state.trainedUnits.map(u=>({id:u.id,x:u.x,y:u.y,tx:u.tx,ty:u.ty,hp:u.hp,maxHp:u.maxHp,mode:u.mode})),",1)

assert 'NPC_INTERACTIONS_ENABLED = false' in s
assert 'ECON_WIDTH_TILES = 3, ECON_HEIGHT_TILES = 2' in s
assert 'ACADEMY' not in s  # unrelated; current academy UI remains training-locked.
gp.write_text(s,encoding='utf-8')
if hp.exists():
    h=hp.read_text(encoding='utf-8').replace('v0.4.0','v0.4.1')
    h=h.replace('가로 3 × 세로 2칸 · 훈련 잠금','가로 3 × 세로 2칸 · 기사 훈련 가능')
    h=h.replace('하급 유닛 훈련 시설</em>','기사 훈련 10초 · 임시비용 골드 10 / 식량 5</em>')
    hp.write_text(h,encoding='utf-8')
print('PIXEL BASTION v0.4.1 knight training: assets, 10s queue, spawn, prototype guard behavior')