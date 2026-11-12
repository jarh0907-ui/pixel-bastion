#!/usr/bin/env python3
"""PIXEL BASTION v0.3.7: buildable mines/farms, one worker each, food/gold economy.
Run after patch_v036.py in GitHub Pages workflow. Original sprites are not modified.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]); jp=root/'game.js'; hp=root/'index.html'; css=root/'style.css'
s=jp.read_text(encoding='utf-8')
assert 'PIXEL BASTION v0.3.6' in s, 'v0.3.6 needs to be patched first'
assert 'NPC_INTERACTIONS_ENABLED = false' in s, 'Keep non-movement NPC interactions locked'

def rep(before, after, count=1):
    global s
    actual=s.count(before)
    if actual != count:
        raise RuntimeError(f'Expected {count} occurrence(s), saw {actual}: {before[:110]!r}')
    s=s.replace(before,after,count)

rep('PIXEL BASTION v0.3.6','PIXEL BASTION v0.3.7')
rep("    houseSub: document.getElementById('houseSubText')", """    houseSub: document.getElementById('houseSubText'),
    food: document.getElementById('foodValue'),
    mineBtn: document.getElementById('mineBuildBtn'),farmBtn: document.getElementById('farmBuildBtn'),
    productionStatus: document.getElementById('productionStatus')""")
rep('  const HOUSE_LIMIT = 3;', '''  // Test-only construction parameters: mine/farm size 3×3 and free until user fixes cost and footprints.
  const ECON_SIZE = 3, ECON_PRODUCTION_INTERVAL = 10, ECON_FOOD_INTERVAL = 60;
  const ECON_WORKERS_LV1 = 1, ECON_MINE_GOLD = 5, ECON_FARM_FOOD = 10;
  const econArt={};
  function loadEconomyArt(){
    for(const [kind,src] of Object.entries({mine:'assets/reserve/mine_entrance_source.png',
      farm:'assets/reserve/farm_plot_source.png'})){
      const im=new Image(); im.onload=()=>econArt[kind]=im; im.src=src;
    }
  }
  const minerSheet=new Image();
  minerSheet.src='assets/reserve/miner_worker_source.png';
  const HOUSE_LIMIT = 3;''')
rep("      houses:[],villagers:[],immigrationClock:0,conversationsStarted:0,conversationsCompleted:0,conversationDurations:[]", """      houses:[],villagers:[],immigrationClock:0,conversationsStarted:0,conversationsCompleted:0,conversationDurations:[],
      economyBuildings:[],economySerial:0,food:0,productionClock:0,foodClock:0,
      moraleLocked:true,economyGoldEarned:0,economyFoodProduced:0,foodConsumed:0""")
rep("    for(const home of state.houses){if(Math.abs(x-home.x)<90 && Math.abs(y-home.y)<90)return '초가집이 있는 땅에는 타워를 세울 수 없습니다.';}", """    for(const home of state.houses){if(Math.abs(x-home.x)<90 && Math.abs(y-home.y)<90)return '초가집이 있는 땅에는 타워를 세울 수 없습니다.';}
    for(const e of state.economyBuildings){if(Math.abs(x-e.x)<85&&Math.abs(y-e.y)<85)return '경제 건물이 있는 땅에는 타워를 세울 수 없습니다.';}""")
rep("    for(const h of state.houses){if(Math.abs(px-h.x)<120&&Math.abs(py-h.y)<120)return '다른 집과 겹칩니다.';}","""    for(const h of state.houses){if(Math.abs(px-h.x)<120&&Math.abs(py-h.y)<120)return '다른 집과 겹칩니다.';}
    for(const b of state.economyBuildings){if(Math.abs(px-b.x)<120&&Math.abs(py-b.y)<120)return '경제 건물과 겹칩니다.';}""")
rep("    for(const tower of state.towers){if(distance(x,y,tower.x,tower.y)<32)return false;}", """    for(const tower of state.towers){if(distance(x,y,tower.x,tower.y)<32)return false;}
    for(const b of state.economyBuildings){if(tx>=b.tx&&tx<b.tx+ECON_SIZE&&ty>=b.ty&&ty<b.ty+ECON_SIZE)return false;}""")
rep("    return state.villagers.some(v=>v.id!==exceptId &&\n      (v.tx===tx&&v.ty===ty || v.moveTo&&v.moveTo.tx===tx&&v.moveTo.ty===ty));", """    return state.villagers.some(v=>v.id!==exceptId && v.jobPhase!=='inside' &&
      (v.tx===tx&&v.ty===ty || v.moveTo&&v.moveTo.tx===tx&&v.moveTo.ty===ty));""")
rep("    for(const v of residents){\n      v.bubbleTime=", """    for(const v of residents){
      if(v.jobBuildingId)continue; // Employed residents follow job path or work, not random roaming.
      v.bubbleTime=""")

# Insert gameplay helpers before homePopulation, which is already below housing construction.
marker='  function homePopulation(home){'
assert s.count(marker)==1
helpers=r'''  function econLabel(kind){return kind==='mine'?'광산':'밭';}
  function econCount(b){return state.villagers.filter(v=>v.jobBuildingId===b.id).length;}
  function econActive(b){return state.villagers.filter(v=>v.jobBuildingId===b.id &&
      (v.jobPhase==='inside'||v.jobPhase==='working')).length;}
  function econPlaceError(tx,ty){
    if(tx<2||ty<2||tx+ECON_SIZE>=MAP-2||ty+ECON_SIZE>=MAP-2)return '월드 밖에는 설치할 수 없습니다.';
    const x=(tx+1.5)*TILE,y=(ty+1.5)*TILE;
    const d=distance(x,y,C,C);
    if(d<245||d>940)return '마을 건설 가능 권역에 설치해 주세요.';
    for(let j=0;j<ECON_SIZE;j++)for(let i=0;i<ECON_SIZE;i++){
      const t=tiles[key(tx+i,ty+j)];
      if(!t||t.obstacle||t.terrain===5||t.terrain===6)return '도로·물·장애물이 없는 3×3 공간이 필요합니다.';
    }
    for(const h of state.houses)if(Math.abs(x-h.x)<120&&Math.abs(y-h.y)<120)return '초가집과 겹칩니다.';
    for(const b of state.economyBuildings)if(Math.abs(x-b.x)<120&&Math.abs(y-b.y)<120)return '다른 경제 건물과 겹칩니다.';
    for(const t of state.towers)if(Math.abs(x-t.x)<82&&Math.abs(y-t.y)<82)return '방어 타워와 겹칩니다.';
    for(const v of state.villagers){
      if(v.jobPhase==='inside')continue;
      for(const c of [v,...(v.moveTo?[v.moveTo]:[])]){
        if(c.tx>=tx-1&&c.tx<tx+ECON_SIZE+1&&c.ty>=ty-1&&c.ty<ty+ECON_SIZE+1)
          return '주민이 서 있는 위치에는 설치할 수 없습니다.';
      }
    }
    return '';
  }
  function buildEconomy(kind,wx,wy){
    if(state.gameOver||!['mine','farm'].includes(kind))return false;
    const p=snapHouse(wx,wy),error=econPlaceError(p.tx,p.ty);
    if(error){toast(error);return false;}
    const b={id:++state.economySerial,type:'economy',kind,level:1,
      tx:p.tx,ty:p.ty,x:p.x,y:p.y};
    state.economyBuildings.push(b);
    state.selection=b;state.build=null;
    spawnParticles(b.x,b.y,'#e0cd8c',12);
    toast(econLabel(kind)+' 건설 완료 · 비용 및 크기는 임시 테스트 규격입니다.');
    updateUI();updateInspector();return true;
  }
  function econEntryCells(b,exceptId=null){
    const cells=[];
    for(let i=0;i<ECON_SIZE;i++){
      cells.push({tx:b.tx+i,ty:b.ty-1},{tx:b.tx+i,ty:b.ty+ECON_SIZE},
        {tx:b.tx-1,ty:b.ty+i},{tx:b.tx+ECON_SIZE,ty:b.ty+i});
    }
    return cells.filter((c,i,a)=>a.findIndex(z=>z.tx===c.tx&&z.ty===c.ty)===i &&
      npcPassableCell(c.tx,c.ty)&&!tileReserved(c.tx,c.ty,exceptId));
  }
  // Exact tile BFS prevents crossing houses, decorative obstacles or other residents.
  function findWorkerRoute(v,b){
    const goals=econEntryCells(b,v.id);
    if(!goals.length)return null;
    const ends=new Set(goals.map(c=>key(c.tx,c.ty)));
    const start=key(v.tx,v.ty),queue=[start],visited=new Set([start]),came=new Map();
    let goal=null;
    for(let i=0;i<queue.length;i++){
      const k=queue[i],x=k%MAP,y=Math.floor(k/MAP);
      if(ends.has(k)){goal=k;break;}
      for(const d of NPC_DIRECTIONS){
        const nx=x+d.dx,ny=y+d.dy,nk=key(nx,ny);
        if(visited.has(nk)||!npcPassableCell(nx,ny)||tileReserved(nx,ny,v.id))continue;
        visited.add(nk);came.set(nk,k);queue.push(nk);
      }
    }
    if(goal===null)return null;
    const path=[];let at=goal;
    while(at!==start){path.push({tx:at%MAP,ty:Math.floor(at/MAP)});at=came.get(at);}
    return path.reverse();
  }
  function selectEmployee(b){
    if(!b||state.gameOver||state.paused)return false;
    if(econCount(b)>=ECON_WORKERS_LV1){toast('1레벨 일꾼은 최대 1명입니다.');return false;}
    const candidates=state.villagers.filter(v=>!v.jobBuildingId && v.partnerId===null)
      .sort((a,c)=>distance(a.x,a.y,b.x,b.y)-distance(c.x,c.y,b.x,b.y));
    for(const v of candidates){
      const path=findWorkerRoute(v,b);
      if(path===null)continue;
      if(v.moveTo){v.x=cellX(v.tx);v.y=cellY(v.ty);v.moveTo=null;}
      v.jobBuildingId=b.id;v.jobKind=b.kind;v.jobPhase='travel';
      v.jobPath=path;v.jobEntryTime=0;v.jobRetry=0;
      v.mode='walk';v.action='';v.actionTime=0;v.bubble='';v.bubbleTime=0;
      toast('주민 #'+v.id+' → '+econLabel(b.kind)+' 일꾼 할당');
      updateInspector();updateUI();return true;
    }
    toast('할당 가능한 주민이 없거나 이동 경로를 찾을 수 없습니다.');return false;
  }
  function releaseEmployee(b){
    const v=state.villagers.find(v=>v.jobBuildingId===b.id);
    if(!v)return false;
    if(v.jobPhase==='inside'){
      const exits=econEntryCells(b,v.id);
      if(!exits.length){v.jobPhase='exiting';toast('광산 출구가 막혀 있어 주민이 나올 수 없습니다.');return false;}
      const c=exits[0];v.tx=c.tx;v.ty=c.ty;v.x=cellX(c.tx);v.y=cellY(c.ty);
    }
    v.jobBuildingId=null;v.jobKind=null;v.jobPhase=null;v.jobPath=[];v.moveTo=null;
    v.idleTime=rand(.4,1.1);v.mode='idle';v.action='';v.actionTime=0;
    toast('일꾼 할당 해제');updateInspector();updateUI();return true;
  }
  function stepEmployees(dt){
    for(const v of state.villagers){
      if(!v.jobBuildingId)continue;
      const b=state.economyBuildings.find(b=>b.id===v.jobBuildingId);
      if(!b) {v.jobBuildingId=null;v.jobPhase=null;v.jobKind=null;v.mode='idle';continue;}
      if(v.jobPhase==='inside'||v.jobPhase==='working')continue;
      if(v.jobPhase==='exiting'){
        const exits=econEntryCells(b,v.id);
        if(exits.length){const c=exits[0];v.tx=c.tx;v.ty=c.ty;v.x=cellX(c.tx);v.y=cellY(c.ty);
          v.jobBuildingId=null;v.jobKind=null;v.jobPhase=null;v.mode='idle';v.idleTime=.7;}
        continue;
      }
      if(v.jobPhase==='entering'){
        v.jobEntryTime-=dt;
        if(v.jobEntryTime<=0){v.jobPhase=b.kind==='mine'?'inside':'working';v.mode='idle';
          v.x=cellX(v.tx);v.y=cellY(v.ty);v.moveTo=null;
          if(state.selection===b)updateInspector();}
        continue;
      }
      if(v.jobPhase!=='travel')continue;
      if(!v.moveTo && !v.jobPath.length){
        const adjacent=econEntryCells(b,v.id).some(c=>c.tx===v.tx&&c.ty===v.ty);
        if(adjacent){v.jobPhase='entering';v.jobEntryTime=.65;v.mode='idle';
          faceOther(v,{tx:b.tx+1,ty:b.ty+1});continue;}
      }
      if(!v.moveTo){
        if(!v.jobPath.length){
          v.jobRetry-=dt;if(v.jobRetry>0)continue;
          const route=findWorkerRoute(v,b);v.jobRetry=.7;
          if(route===null)continue;v.jobPath=route;
        }
        const c=v.jobPath[0];
        if(c && npcPassableCell(c.tx,c.ty) && !tileReserved(c.tx,c.ty,v.id)){
          v.moveTo=v.jobPath.shift();
          const dx=v.moveTo.tx-v.tx,dy=v.moveTo.ty-v.ty;
          v.dir=Math.abs(dx)>Math.abs(dy)?(dx>0?'right':'left'):(dy>0?'down':'up');
        }else{v.jobPath=[];v.jobRetry=.7;continue;}
      }
      if(v.moveTo){
        const x=cellX(v.moveTo.tx),y=cellY(v.moveTo.ty),distanceLeft=distance(v.x,v.y,x,y);
        const step=Math.min(distanceLeft,v.speed*dt);
        if(distanceLeft>0){v.x+=(x-v.x)*step/distanceLeft;v.y+=(y-v.y)*step/distanceLeft;}
        v.walkTime+=dt;
        if(distanceLeft<=step+.01){v.tx=v.moveTo.tx;v.ty=v.moveTo.ty;
          v.x=x;v.y=y;v.moveTo=null;}
      }
    }
  }
  function stepEconomy(dt){
    state.productionClock+=dt;state.foodClock+=dt;
    while(state.productionClock>=ECON_PRODUCTION_INTERVAL){
      state.productionClock-=ECON_PRODUCTION_INTERVAL;
      for(const b of state.economyBuildings){
        const workers=econActive(b);
        if(b.kind==='mine'){
          const value=workers*ECON_MINE_GOLD;state.gold+=value;
          state.economyGoldEarned+=value;
        }else{
          const value=workers*ECON_FARM_FOOD;state.food+=value;
          state.economyFoodProduced+=value;
        }
      }
    }
    while(state.foodClock>=ECON_FOOD_INTERVAL){
      state.foodClock-=ECON_FOOD_INTERVAL;
      // Entire population counts, including workers currently inside a mine.
      const demand=state.villagers.length;
      state.food-=demand;state.foodConsumed+=demand;
      // Morale penalties for negative food are deferred and have NO effect yet.
    }
  }
  function drawEconomy(b){
    const w=144,h=146;
    const im=econArt[b.kind];
    if(im)ctx.drawImage(im,Math.round(b.x-w/2),Math.round(b.y-h+35),w,h);
    else{ctx.fillStyle=b.kind==='mine'?'#7c7778':'#97784c';ctx.fillRect(b.x-55,b.y-64,110,100);}
    if(state.selection===b){
      ctx.strokeStyle='#f9db95';ctx.lineWidth=2;
      ctx.strokeRect(b.tx*TILE,b.ty*TILE,ECON_SIZE*TILE,ECON_SIZE*TILE);
      ctx.fillStyle='#1b302bdd';ctx.fillRect(b.x-54,b.y-121,108,20);
      ctx.textAlign='center';ctx.font='bold 12px Consolas,monospace';ctx.fillStyle='#f5e8bd';
      ctx.fillText(econLabel(b.kind)+' '+econCount(b)+'/1명',b.x,b.y-106);
    }
  }
  function drawMiner(v){
    if(v.jobKind!=='mine'||!minerSheet.complete||!minerSheet.naturalWidth)return false;
    const row={down:0,up:1,left:2,right:3}[v.dir]||0;
    const col=v.jobPhase==='travel'?Math.floor(v.walkTime*NPC_WALK_FPS)%4:0;
    // The source is a 4×4 sprite layout with generous outer margins; use original pixel sampling.
    const sourceX=[270,505,740,970][col],sourceY=[10,270,534,795][row];
    const width=180,height=242;
    ctx.drawImage(minerSheet,sourceX,sourceY,width,height,
      Math.round(v.x-36),Math.round(v.y-NPC_DRAW_HEIGHT),72,NPC_DRAW_HEIGHT);
    return true;
  }
'''
s=s.replace(marker,helpers+marker,1)

# HTML and Canvas integration: render economic buildings as world occupants, with preview and selection.
rep("    for(const h of state.houses)if(h.x>b.left-120&&h.x<b.right+120&&h.y>b.top-180&&h.y<b.bottom+140)all.push({y:h.y+48,kind:'house',obj:h});", """    for(const h of state.houses)if(h.x>b.left-120&&h.x<b.right+120&&h.y>b.top-180&&h.y<b.bottom+140)all.push({y:h.y+48,kind:'house',obj:h});
    for(const e of state.economyBuildings)if(e.x>b.left-120&&e.x<b.right+120&&e.y>b.top-180&&e.y<b.bottom+140)all.push({y:e.y+48,kind:'economy',obj:e});""")
rep("    for(const v of state.villagers)if(v.x>b.left-100&&v.x<b.right+100&&v.y>b.top-120&&v.y<b.bottom+100)all.push({y:v.y,kind:'npc',obj:v});", """    for(const v of state.villagers)if(v.jobPhase!=='inside' && v.jobPhase!=='exiting' && v.x>b.left-100&&v.x<b.right+100&&v.y>b.top-140&&v.y<b.bottom+100)all.push({y:v.y,kind:'npc',obj:v});""")
rep("      }else if(entry.kind==='house')drawHouse(entry.obj);\n      else if(entry.kind==='npc')drawNpc(entry.obj);", """      }else if(entry.kind==='house')drawHouse(entry.obj);
      else if(entry.kind==='economy')drawEconomy(entry.obj);
      else if(entry.kind==='npc'){
        const v=entry.obj;
        ctx.save();if(v.jobPhase==='entering')ctx.globalAlpha=Math.max(.1,v.jobEntryTime/.65);
        if(!drawMiner(v))drawNpc(v);
        ctx.restore();
      }""")
rep("    for(const h of state.houses){miniCtx.fillStyle='#efb36d';miniCtx.fillRect(h.x*sc-2,h.y*sc-2,5,5);}", """    for(const h of state.houses){miniCtx.fillStyle='#efb36d';miniCtx.fillRect(h.x*sc-2,h.y*sc-2,5,5);}
    for(const b of state.economyBuildings){miniCtx.fillStyle=b.kind==='mine'?'#a9a6a6':'#d2d16f';miniCtx.fillRect(b.x*sc-2,b.y*sc-2,5,5);}""")
rep("    for(const v of state.villagers){miniCtx.fillStyle='#d0fcdb';miniCtx.fillRect(v.x*sc,v.y*sc,2,2);}", """    for(const v of state.villagers){if(v.jobPhase==='inside'||v.jobPhase==='exiting')continue;miniCtx.fillStyle='#d0fcdb';miniCtx.fillRect(v.x*sc,v.y*sc,2,2);}""")
rep("    if(state.build==='house'){\n      const h=snapHouse(state.hover.x,state.hover.y);", """    if(state.build==='house'||state.build==='mine'||state.build==='farm'){
      const isEconomy=state.build!=='house';
      const h=snapHouse(state.hover.x,state.hover.y);""")
rep("      const valid=canPlaceHouse(h.tx,h.ty)==='';", "      const valid=(isEconomy?econPlaceError(h.tx,h.ty):canPlaceHouse(h.tx,h.ty))==='';")
rep("      ctx.globalAlpha=.7;drawSprite('house_thatch',h.x-68,h.y-126,136,164);ctx.globalAlpha=1;", """      ctx.globalAlpha=.7;
      if(isEconomy){const img=econArt[state.build];if(img)ctx.drawImage(img,h.x-72,h.y-111,144,146);}
      else drawSprite('house_thatch',h.x-68,h.y-126,136,164);
      ctx.globalAlpha=1;""")
rep("    if(state.build){if(state.build==='house')buildHouse(w.x,w.y);else placeTower(state.build,w.x,w.y);return;}", """    if(state.build){if(state.build==='house')buildHouse(w.x,w.y);
      else if(state.build==='mine'||state.build==='farm')buildEconomy(state.build,w.x,w.y);
      else placeTower(state.build,w.x,w.y);return;}""")
rep("    for(const v of state.villagers){\n      if(Math.abs(w.x-v.x)<", """    for(const v of state.villagers){
      if(v.jobPhase==='inside'||v.jobPhase==='exiting')continue;
      if(Math.abs(w.x-v.x)<""")
rep("    if(!nearest){for(const h of state.houses){", """    if(!nearest){for(const b of state.economyBuildings){
      if(Math.abs(w.x-b.x)<75&&w.y>b.y-118&&w.y<b.y+55){nearest=b;break;}
    }}
    if(!nearest){for(const h of state.houses){""")
rep("      stepVillagers(dt);", """      stepVillagers(dt);
      stepEmployees(dt);
      stepEconomy(dt);""")

# Inspector and button handling. All upgrades remain locked.
rep("    if(t.type==='house'){\n      ui.inspector.innerHTML=", """    if(t.type==='economy'){
      const assigned=econCount(t),working=econActive(t),remaining=ECON_WORKERS_LV1-assigned;
      const free=state.villagers.some(v=>!v.jobBuildingId);
      ui.inspector.innerHTML=`<div class="inspector-title"><strong>§{econLabel(t.kind)}</strong><span class="level">LV.1 / 🔒 강화 잠금</span></div>
        <div class="inspector-stats"><div><span>할당 일꾼</span><strong>§{assigned} / 1명</strong></div>
        <div><span>실제 작업 중</span><strong>§{working}명</strong></div>
        <div><span>10초마다</span><strong>§{t.kind==='mine'?'+5 ◆':' +10 식량'}</strong></div>
        <div><span>건설 비용·면적</span><strong>시험용 무료·3×3</strong></div></div>
        <div class="inspector-actions"><button type="button" data-action="econ-assign" §{(!remaining||!free||state.paused)?'disabled':''}>👷 일꾼 할당</button>
        <button type="button" data-action="econ-release" §{!assigned?'disabled':''}>↩ 할당 해제</button></div>
        <div class="inspector-actions" style="margin-top:8px"><button type="button" disabled>🔒 업그레이드 잠금</button></div>`;
      return;
    }
    if(t.type==='house'){
      ui.inspector.innerHTML=""".replace('§{','${'))
rep("    if(button.dataset.action==='upgrade')upgradeTower();", """    if(button.dataset.action==='econ-assign'&&state.selection&&state.selection.type==='economy')selectEmployee(state.selection);
    if(button.dataset.action==='econ-release'&&state.selection&&state.selection.type==='economy')releaseEmployee(state.selection);
    if(button.dataset.action==='upgrade')upgradeTower();""")
rep("    ui.gold.textContent=Math.floor(state.gold);ui.lives.textContent=Math.max(0,Math.ceil(state.lives));", """    ui.gold.textContent=Math.floor(state.gold);ui.lives.textContent=Math.max(0,Math.ceil(state.lives));
    ui.food.textContent=state.food.toLocaleString('ko-KR');
    ui.food.classList.toggle('negative',state.food<0);
    ui.mineBtn.setAttribute('aria-pressed',String(state.build==='mine'));
    ui.farmBtn.setAttribute('aria-pressed',String(state.build==='farm'));
    ui.productionStatus.textContent='10초 생산 · 60초 식량 소비 · 민심 🔒 잠금';""")
rep("  ui.houseButton.addEventListener('click',selectHouseBuild);", """  ui.houseButton.addEventListener('click',selectHouseBuild);
  ui.mineBtn.addEventListener('click',()=>selectBuild('mine'));
  ui.farmBtn.addEventListener('click',()=>selectBuild('farm'));""")
rep("    else if(k==='5')selectHouseBuild();", """    else if(k==='5')selectHouseBuild();
    else if(k==='6')selectBuild('mine');
    else if(k==='7')selectBuild('farm');""")
rep('  generateWorld();loadSprites();loadNpcImages();reset();', '  generateWorld();loadSprites();loadNpcImages();loadEconomyArt();reset();')
rep("    buildHouse:(x,y)=>buildHouse(x,y),", """    buildHouse:(x,y)=>buildHouse(x,y),
    buildEconomy:(kind,x,y)=>buildEconomy(kind,x,y),
    assignWorker:(id)=>{const b=state.economyBuildings.find(b=>b.id===id);return b?selectEmployee(b):false;},
    releaseWorker:(id)=>{const b=state.economyBuildings.find(b=>b.id===id);return b?releaseEmployee(b):false;},""")
rep("      houseCount:state.houses.length,population:state.villagers.length,populationCapacity:state.houses.length*HOUSE_CAPACITY,", """      houseCount:state.houses.length,population:state.villagers.length,populationCapacity:state.houses.length*HOUSE_CAPACITY,
      food:state.food,moraleLocked:state.moraleLocked,
      goldFromMines:state.economyGoldEarned,foodFromFarms:state.economyFoodProduced,foodConsumed:state.foodConsumed,
      economyBuildings:state.economyBuildings.map(b=>({id:b.id,kind:b.kind,level:b.level,workers:econCount(b),active:econActive(b),tx:b.tx,ty:b.ty,x:b.x,y:b.y})),""")
rep("        movingTo:v.moveTo?{...v.moveTo}:null,dir:v.dir,mode:v.mode,action:v.action,", """        movingTo:v.moveTo?{...v.moveTo}:null,dir:v.dir,mode:v.mode,action:v.action,
        jobBuildingId:v.jobBuildingId||null,jobPhase:v.jobPhase||null,""")

jp.write_text(s,encoding='utf-8')

# Adapt existing UI without disrupting the established tower, resident and battle controls.
h=hp.read_text(encoding='utf-8')
assert 'id="houseBuildBtn"' in h and 'id="populationValue"' in h
h=h.replace('v0.3.6','v0.3.7')
h=h.replace('<div class="settlement-meter provisional"><b>🌾 식량</b><strong>미설정</strong><small>규칙 확정 대기</small></div>',
 '''<div class="settlement-meter"><b>🌾 식량</b><strong id="foodValue">0</strong><small>60초마다 인구 × 1 소비</small></div>''')
h=h.replace('<div class="settlement-meter provisional"><b>♥ 민심</b><strong>미설정</strong><small>규칙 확정 대기</small></div>',
 '''<div class="settlement-meter provisional"><b>♥ 민심</b><strong>🔒 잠금</strong><small>식량 부족 페널티 미적용</small></div>''')
h=h.replace('        <div class="panel-heading"><div><span class="tiny-rect amber"></span><b>방어 타워</b>',
 '''        <div class="panel-heading"><div><span class="tiny-rect amber"></span><b>경제 타워</b></div><span class="shortcut">6 · 7</span></div>
        <div class="settlement-build economy-build">
          <button type="button" id="mineBuildBtn" class="house-build" aria-pressed="false"><img src="assets/reserve/mine_entrance_source.png" alt="광산"><span><strong>광산</strong><em>1레벨 일꾼 1명 · 10초마다 +5골드</em><small>임시 무료 건설 · 3×3칸</small></span></button>
          <button type="button" id="farmBuildBtn" class="house-build" aria-pressed="false"><img src="assets/reserve/farm_plot_source.png" alt="밭"><span><strong>밭</strong><em>1레벨 일꾼 1명 · 10초마다 +10식량</em><small>임시 무료 건설 · 3×3칸</small></span></button>
          <p id="productionStatus">10초 생산 · 60초 식량 소비 · 민심 🔒 잠금</p>
        </div>
        <div class="panel-heading"><div><span class="tiny-rect amber"></span><b>방어 타워</b>''',1)
h=h.replace('1~4: 타워 / 5: 초가집 / 주민 클릭: 감정 / ESC: 취소',
            '1~4: 방어 / 5: 집 / 6: 광산 / 7: 밭 / ESC: 취소')
h=h.replace('주민은 시간이 지나며 자동 입주합니다. 주민을 클릭하면 감정·대화 모션을 볼 수 있습니다.',
            '주민은 시간이 지나며 입주합니다. 대화·감정은 잠금 상태입니다.')
h=hp.write_text(h,encoding='utf-8')
cs=css.read_text(encoding='utf-8')
cs+='''\n/* v0.3.7 economic buildings / food / UI */
.economy-build{display:flex;flex-direction:column;gap:8px}
.economy-build .house-build{min-height:78px}
.economy-build .house-build img{width:65px;height:63px}
.settlement-meter strong.negative{color:#ff9c87}
.inspector-actions button:disabled{opacity:.55;cursor:not-allowed}
'''
css.write_text(cs,encoding='utf-8')
print('v0.3.7 economy patch applied')
