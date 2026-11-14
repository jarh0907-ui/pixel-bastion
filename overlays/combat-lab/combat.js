(() => {
  'use strict';
  const canvas=document.getElementById('arena'),ctx=canvas.getContext('2d');
  const W=canvas.width,H=canvas.height;
  const CELL_W=144,CELL_H=144,ACTIONS=['idle','walk','attack','hit','death'];
  const FRAMES={knight:{idle:4,walk:4,attack:4,hit:2,death:4},archer:{idle:1,walk:4,attack:4,hit:2,death:1},goblin:{idle:1,walk:4,attack:4,hit:2,death:6}};
  const SPEC={
    knight:{label:'기사',team:'ally',hp:32,atk:4,def:2,as:1.0,ms:65,range:37,windup:.31},
    archer:{label:'궁수',team:'ally',hp:20,atk:3,def:0,as:.8,ms:55,range:250,windup:.36},
    goblin:{label:'고블린',team:'enemy',hp:14,atk:2,def:1,as:1.1,ms:70,range:32,windup:.27}
  };
  const sprites={};Object.keys(SPEC).forEach(type=>{const i=new Image();i.src='assets/'+type+'.webp';sprites[type]=i;});
  const arrows=new Image();arrows.src='assets/arrows.webp';
  const el=id=>document.getElementById(id);
  let state={units:[],projectiles:[],floats:[],running:false,paused:false,speed:1,elapsed:0,shots:0,hits:0,kills:0,serial:0};
  let last=0,lastDisplay=-1;
  const clamp=(x,min,max)=>Math.max(min,Math.min(max,x));
  const dist=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
  function note(s,kind='normal'){
    const log=el('events');if(log.textContent.includes('기다리고'))log.textContent='';
    const d=document.createElement('div');d.className=kind;d.textContent='['+state.elapsed.toFixed(1)+'초] '+s;log.prepend(d);
    while(log.childElementCount>35)log.lastChild.remove();
  }
  function floatAt(x,y,text,color){state.floats.push({x,y,text,color,t:0});}
  function create(type,x,y){
    const spec=SPEC[type];return {id:++state.serial,type,team:spec.team,x,y,hp:spec.hp,
      dir:spec.team==='ally'?'right':'left',mode:'idle',anim:0,deathT:0,cd:.15+Math.random()*.3,pending:null,
      stun:0,actionLock:0,hitFlash:0,melee:0,damageDone:0,damageTaken:0};
  }
  function begin(){
    let knights=clamp(Number(el('knights').value)||0,0,15),archers=clamp(Number(el('archers').value)||0,0,15),
      goblins=clamp(Number(el('goblins').value)||0,1,25);
    if(knights+archers===0){knights=1;el('knights').value='1';}
    state={units:[],projectiles:[],floats:[],running:true,paused:false,speed:state.speed,elapsed:0,shots:0,hits:0,kills:0,serial:0};
    const allyTypes=[...Array(knights).fill('knight'),...Array(archers).fill('archer')];
    allyTypes.forEach((type,i)=>{const row=i%8,col=Math.floor(i/8);state.units.push(create(type,200+col*66-(i%2)*12,155+row*49));});
    addGoblins(goblins);
    el('resultText').textContent='⚔ 교전 중';el('resultText').style.color='#e6d69b';el('pauseBtn').disabled=false;
    el('reinforceBtn').disabled=false;el('pauseBtn').textContent='Ⅱ 일시정지';el('statusText').textContent='전투 진행 중';
    el('events').textContent='';note(`기사 ${knights}명 · 궁수 ${archers}명 VS 고블린 ${goblins}명`);
    updateUI();
  }
  function addGoblins(count){
    const current=state.units.filter(u=>u.type==='goblin'&&!dead(u)).length;
    for(let i=0;i<count;i++){
      const v=current+i;state.units.push(create('goblin',825+Math.floor(v/9)*40,135+(v%9)*48));
    }
  }
  function dead(u){return u.hp<=0;}
  function face(u,t){const dx=t.x-u.x,dy=t.y-u.y;u.dir=Math.abs(dx)>Math.abs(dy)?(dx<0?'left':'right'):(dy<0?'up':'down');}
  function closest(u){
    let nearest=null,best=Infinity;
    for(const v of state.units){if(v.team===u.team||dead(v))continue;
      const d=dist(u,v);if(d<best){nearest=v;best=d;}
    }
    return nearest;
  }
  function hurt(target,attacker){
    if(dead(target)||dead(attacker))return;
    const src=SPEC[attacker.type],dst=SPEC[target.type];
    const immune=false; // Keep immunity as a formal exception; none of this test's units are immune.
    const damage=immune?0:Math.max(1,src.atk-dst.def);
    target.hp=Math.max(0,target.hp-damage);target.damageTaken+=damage;attacker.damageDone+=damage;
    state.hits++;
    floatAt(target.x,target.y-103,'−'+damage,'#ffe19d');
    if(target.hp<=0){target.mode='death';target.anim=0;target.deathT=0;target.pending=null;target.actionLock=0;state.kills++;
      note(src.label+' → '+dst.label+' 처치 ('+damage+' 피해)',attacker.team==='ally'?'good':'bad');
    }else{
      target.hitFlash=.15;
      // An attack is visually committed until its windup/pose completes.
      // Getting struck in that window changes HP but cannot turn the attack
      // sprite into a hit sprite mid-swing (the original v0.1 bug).
      if(!(target.mode==='attack'&&target.actionLock>0)){
        target.mode='hit';target.anim=0;target.stun=.26;target.actionLock=.26;
      }
    }
  }
  function shoot(u,t){
    if(dead(t))return;
    const dx=t.x-u.x,dy=t.y-u.y;
    const l=Math.max(1,Math.hypot(dx,dy));
    state.projectiles.push({x:u.x,y:u.y-46,vx:dx/l*440,vy:dy/l*440,targetId:t.id,ownerId:u.id,life:1.5});
    state.shots++;
  }
  function step(dt){
    if(!state.running||state.paused)return;
    dt=Math.min(.075,Math.max(0,dt));state.elapsed+=dt;
    for(const u of state.units){
      u.anim+=dt;
      if(dead(u)){u.deathT+=dt;continue;}
      u.cd=Math.max(0,u.cd-dt);u.stun=Math.max(0,u.stun-dt);u.actionLock=Math.max(0,u.actionLock-dt);u.hitFlash=Math.max(0,u.hitFlash-dt);
      if(u.pending){
        u.pending.time-=dt;
        if(u.pending.time<=0){
          const t=state.units.find(v=>v.id===u.pending.targetId),mode=u.pending.mode;
          if(t&&!dead(t)&&!dead(u)){
            if(mode==='arrow')shoot(u,t);
            else if(dist(u,t)<SPEC[u.type].range+25)hurt(t,u);
          }
          u.pending=null;
        }
      }
      if(u.actionLock>0)continue;
      if(u.mode==='attack'||u.mode==='hit'){u.mode='idle';u.anim=0;}
      if(u.stun>0)continue;
      const target=closest(u);
      if(!target){if(!u.pending)u.mode='idle';continue;}
      const sp=SPEC[u.type],d=dist(u,target);
      face(u,target);
      if(d<=sp.range){
        if(u.cd<=0&&!u.pending){
          u.cd=1/sp.as;u.mode='attack';u.anim=0;u.actionLock=Math.max(.59,sp.windup+.16);
          u.pending={targetId:target.id,time:sp.windup,mode:u.type==='archer'?'arrow':'melee'};
        } // A complete attack stays visible until actionLock expires.
      }else if(!u.pending){
        const movement=Math.min(dt*sp.ms,d-sp.range+.01);
        const dx=(target.x-u.x)/d,dy=(target.y-u.y)/d;
        let nx=u.x+dx*movement,ny=u.y+dy*movement;
        for(const ally of state.units){
          if(ally===u||dead(ally)||ally.team!==u.team)continue;
          const dd=Math.hypot(nx-ally.x,ny-ally.y);
          if(dd<27&&dd>.01){nx+=(nx-ally.x)/dd*(27-dd)*.6;ny+=(ny-ally.y)/dd*(27-dd)*.6;}
        }
        u.x=clamp(nx,40,W-40);u.y=clamp(ny,70,H-27);u.mode='walk';
      }
    }
    for(const arrow of state.projectiles){
      arrow.x+=arrow.vx*dt;arrow.y+=arrow.vy*dt;arrow.life-=dt;
      const t=state.units.find(v=>v.id===arrow.targetId);
      if(!t||dead(t)||!state.units.some(u=>u.id===arrow.ownerId&&!dead(u))){arrow.life=0;continue;}
      if(Math.hypot(arrow.x-t.x,arrow.y-(t.y-45))<28){
        const u=state.units.find(v=>v.id===arrow.ownerId);if(u)hurt(t,u);
        arrow.life=0;
      }
    }
    state.projectiles=state.projectiles.filter(a=>a.life>0);
    for(const f of state.floats){f.t+=dt;f.y-=dt*24;}state.floats=state.floats.filter(f=>f.t<1.1);
    state.units=state.units.filter(u=>!dead(u)||u.deathT<1.7);
    const a=state.units.some(u=>u.team==='ally'&&!dead(u));
    const e=state.units.some(u=>u.team==='enemy'&&!dead(u));
    if(!a||!e){state.running=false;state.projectiles=[];
      const result=a&&!e?'🛡 아군 승리':e&&!a?'👹 고블린 승리':'무승부';
      el('resultText').textContent=result;el('resultText').style.color=a?'#9ae2bc':'#f2b3a2';
      el('statusText').textContent='전투 종료';el('pauseBtn').disabled=true;el('reinforceBtn').disabled=true;
      note(result,a?'good':'bad');
    }
  }
  function drawBackground(){
    ctx.fillStyle='#7b9871';ctx.fillRect(0,0,W,H);
    for(let y=0;y<H;y+=32)for(let x=0;x<W;x+=32){
      const noise=(x*17+y*31)%97;
      ctx.fillStyle=noise<34?'#86a07a':noise<63?'#829a76':'#78936d';ctx.fillRect(x,y,32,32);
      if(noise<15){ctx.fillStyle='#aeb78a';ctx.fillRect(x+10,y+18,3,5);ctx.fillRect(x+13,y+15,3,4);}
      if(noise>89){ctx.fillStyle='#607964';ctx.fillRect(x+18,y+5,5,3);}
    }
    ctx.fillStyle='#7f846e88';ctx.fillRect(W/2-5,0,10,H);
    ctx.fillStyle='#e7dfb6';ctx.font='bold 16px system-ui';ctx.textAlign='left';ctx.fillText('아군 진영',20,37);
    ctx.textAlign='right';ctx.fillText('고블린 진영',W-20,37);
  }
  function drawUnit(u){
    const sp=SPEC[u.type],image=sprites[u.type];
    const act=ACTIONS.indexOf(u.mode);const dir={down:0,up:1,left:2,right:3}[u.dir];
    const frames=FRAMES[u.type][u.mode],fps=u.mode==='death'?3.5:u.mode==='attack'?7:u.mode==='walk'?7:3.3;
    const frame=Math.min(frames-1,Math.floor(u.anim*fps)%frames);
    const drawW=136,drawH=132;const dx=Math.round(u.x-drawW/2),dy=Math.round(u.y-drawH+7);
    ctx.fillStyle='#243b354a';ctx.beginPath();ctx.ellipse(u.x,u.y,31,8,0,0,Math.PI*2);ctx.fill();
    ctx.save();if(dead(u))ctx.globalAlpha=clamp(1-u.deathT/1.7,.05,1);
    if(image.complete&&image.naturalWidth){ctx.imageSmoothingEnabled=false;
      ctx.drawImage(image,frame*CELL_W,(act*4+dir)*CELL_H,CELL_W,CELL_H,dx,dy,drawW,drawH);
    }else{ctx.fillStyle=u.team==='ally'?'#d9ba75':'#9dba5c';ctx.fillRect(u.x-15,u.y-65,30,55);}
    ctx.restore();
    if(!dead(u)){
      const bw=54,hp=Math.max(0,u.hp/sp.hp);
      ctx.fillStyle='#162c31';ctx.fillRect(Math.round(u.x-bw/2-1),Math.round(u.y-124),bw+2,8);
      ctx.fillStyle=u.hitFlash>0?'#fff3c6':u.team==='ally'?'#78c9a2':'#df8b6d';ctx.fillRect(Math.round(u.x-bw/2),Math.round(u.y-123),Math.round(bw*hp),6);
    }
  }
  function draw(){
    drawBackground();
    const order=[...state.units].sort((a,b)=>a.y-b.y);
    for(const u of order)drawUnit(u);
    for(const arrow of state.projectiles){
      const angle=Math.atan2(arrow.vy,arrow.vx);
      const idx=Math.abs(arrow.vx)>Math.abs(arrow.vy)?(arrow.vx>0?1:2):(arrow.vy>0?3:0);
      ctx.save();ctx.translate(Math.round(arrow.x),Math.round(arrow.y));ctx.imageSmoothingEnabled=false;
      if(arrows.complete&&arrows.naturalWidth){ctx.drawImage(arrows,idx*160,0,160,160,-22,-22,44,44);}
      else{ctx.rotate(angle);ctx.fillStyle='#dec092';ctx.fillRect(-14,-2,29,4);}
      ctx.restore();
    }
    ctx.font='bold 18px system-ui';ctx.textAlign='center';
    for(const f of state.floats){ctx.globalAlpha=1-f.t/1.1;ctx.fillStyle='#283b38';ctx.fillText(f.text,f.x+1,f.y+1);ctx.fillStyle=f.color;ctx.fillText(f.text,f.x,f.y);}
    ctx.globalAlpha=1;
    if(!state.running){
      ctx.fillStyle='#122329aa';ctx.fillRect(W/2-196,H/2-48,392,96);
      ctx.textAlign='center';ctx.font='bold 23px system-ui';ctx.fillStyle='#f5deaa';
      ctx.fillText(state.elapsed>0?el('resultText').textContent:'▶ 전투 시작을 눌러줘!',W/2,H/2+8);
    }
  }
  function updateUI(){
    el('allyCount').textContent=state.units.filter(u=>u.team==='ally'&&!dead(u)).length;
    el('enemyCount').textContent=state.units.filter(u=>u.team==='enemy'&&!dead(u)).length;
    el('arrowCount').textContent=state.shots;el('hitCount').textContent=state.hits;
    el('seconds').textContent=state.elapsed.toFixed(1);
    el('speedBtn').textContent='x'+state.speed+' 속도';
  }
  function frame(now){
    const dt=last?clamp((now-last)/1000,0,.05)*state.speed:0;last=now;
    step(dt);draw();
    if(Math.floor(state.elapsed*5)!==lastDisplay){lastDisplay=Math.floor(state.elapsed*5);updateUI();}
    requestAnimationFrame(frame);
  }
  el('startBtn').addEventListener('click',begin);
  el('pauseBtn').addEventListener('click',()=>{if(!state.running)return;state.paused=!state.paused;el('pauseBtn').textContent=state.paused?'▶ 계속':'Ⅱ 일시정지';el('statusText').textContent=state.paused?'일시정지':'전투 진행 중';});
  el('speedBtn').addEventListener('click',()=>{state.speed=state.speed===1?2:state.speed===2?4:1;updateUI();});
  el('reinforceBtn').addEventListener('click',()=>{if(!state.running)return;addGoblins(1);note('고블린 1명 추가 배치','bad');updateUI();});
  canvas.addEventListener('pointerdown',e=>{const r=canvas.getBoundingClientRect(),x=(e.clientX-r.left)*W/r.width,y=(e.clientY-r.top)*H/r.height;const u=state.units.findLast(o=>!dead(o)&&Math.hypot(o.x-x,o.y-y)<45);if(u){const s=SPEC[u.type];note(s.label+': HP '+u.hp+'/'+s.hp+' · ATK '+s.atk+' · DEF '+s.def+' · AS '+s.as+' · MS '+s.ms);}});
  window.PB_COMBAT_TEST=Object.freeze({begin,step:(seconds)=>{const times=Math.ceil(seconds/.05);for(let i=0;i<times;i++)step(seconds/times);updateUI();},
    snapshot:()=>({running:state.running,elapsed:state.elapsed,shots:state.shots,hits:state.hits,kills:state.kills,
      units:state.units.map(u=>({id:u.id,type:u.type,team:u.team,hp:u.hp,x:u.x,y:u.y,mode:u.mode,actionLock:u.actionLock,hitFlash:u.hitFlash})),
      arrows:state.projectiles.length,result:el('resultText').textContent}),
    specs:SPEC});
  updateUI();requestAnimationFrame(frame);
})();