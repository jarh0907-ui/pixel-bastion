#!/usr/bin/env python3
"""PIXEL BASTION v0.3.9 — both jobs enter buildings, animated operation + readable output."""
from pathlib import Path
import re, sys

root=Path(sys.argv[1])
game=root/'game.js'
html=root/'index.html'
text=game.read_text(encoding='utf-8')
assert 'PIXEL BASTION v0.3.8' in text, 'Run patch_v038.py before patch_v039.py'
assert 'NPC_INTERACTIONS_ENABLED = false' in text, 'Non-movement NPC interactions must stay locked'

def replace_one(before,after):
    global text
    found=text.count(before)
    if found!=1:
        raise RuntimeError(f'v0.3.9: expected one occurrence, got {found}: {before[:130]!r}')
    text=text.replace(before,after,1)

replace_one('PIXEL BASTION v0.3.8','PIXEL BASTION v0.3.9')

# Previously farm residents changed to 'working' and were still drawn on the map.
# Both mine and farm employees now disappear AFTER the entry fade completes, not before.
# They remain counted in total population and in the building's productive workforce.
replace_one(
    "if(v.jobEntryTime<=0){v.jobPhase=b.kind==='mine'?'inside':'working';v.mode='idle';",
    "if(v.jobEntryTime<=0){v.jobPhase='inside';v.mode='idle';"
)

# Building labels must report the real active workforce and its 10-second yield.
# Float the payment only when production actually occurs (not on assignment or during travel).
replace_one(
    'state.economyGoldEarned+=value;',
    """state.economyGoldEarned+=value;
          if(value>0)floating(b.x,b.y-202,'+'+value+' 골드','#ffe0a0');"""
)
replace_one(
    'state.economyFoodProduced+=value;',
    """state.economyFoodProduced+=value;
          if(value>0)floating(b.x,b.y-202,'+'+value+' 식량','#bce9a9');"""
)

# Preserve pixel-accurate placement and 3x2 collision footprint; only animate the
# artwork by 1-2 whole world pixels, plus tiny repeating smoke/harvest pixel motes.
# No changes to PNG assets, buildings' positions, upgrade locks, or spawn rules.
new_renderer = r'''  function drawEconomy(b){
    const w=168,h=172,im=econArt[b.kind],workers=econActive(b);
    const active=workers>0, time=state.elapsed;
    const isMine=b.kind==='mine';
    const jiggleX=active&&isMine?Math.round(Math.sin(time*10+b.id)*1.1):0;
    const bounceY=active?Math.round(Math.sin(time*(isMine?5.4:3.1)+b.id)*1.5):0;
    if(im)ctx.drawImage(im,Math.round(b.x-w/2)+jiggleX,Math.round(b.y-h+43)+bounceY,w,h);
    else{
      ctx.fillStyle=isMine?'#7c7778':'#97784c';
      ctx.fillRect(b.x-64+jiggleX,b.y-77+bounceY,128,115);
    }
    // Ongoing on-site activity. Static buildings do not pulse or emit particles.
    if(active){
      const motes=isMine?3:4;
      for(let i=0;i<motes;i++){
        const progress=(time*(isMine?.46:.30)+i/motes+b.id*.17)%1;
        const drift=Math.sin(time*1.6+i*2.1+b.id)*6;
        const baseX=b.x+(isMine?25:(i%2?32:-33));
        const baseY=b.y-(isMine?82:69);
        ctx.globalAlpha=Math.max(.20,.85-progress*.70);
        ctx.fillStyle=isMine?(i%2?'#d5c8ac':'#a9a7a0'):(i%2?'#bee18d':'#e9d38f');
        ctx.fillRect(Math.round(baseX+drift),Math.round(baseY-progress*25),4,4);
      }
      ctx.globalAlpha=1;
    }
    // Two-line production tag is visible even when the building is not selected.
    // It reports actual yield (zero until an employee finishes entering).
    const gain=workers*(isMine?ECON_MINE_GOLD:ECON_FARM_FOOD);
    const label=isMine?'광산':'밭';
    const unit=isMine?'골드':'식량';
    const bannerY=Math.round(b.y-185),bannerW=156;
    ctx.fillStyle=active?'#203e36e8':'#243139e0';
    ctx.fillRect(Math.round(b.x-bannerW/2),bannerY,bannerW,35);
    ctx.fillStyle=active?'#bbddac':'#aab4ba';
    ctx.fillRect(Math.round(b.x-bannerW/2),bannerY,3,35);
    ctx.textAlign='center';
    ctx.font='bold 12px sans-serif';
    ctx.fillStyle='#f4ecd4';
    ctx.fillText(label+' '+workers+'/1 · '+(active?'작업 중':'생산 대기'),b.x,bannerY+14);
    ctx.fillStyle=active?(isMine?'#ffdc9d':'#c7f0a5'):'#ccd2d0';
    ctx.fillText('+'+gain+' '+unit+' / 10초',b.x,bannerY+29);
    if(state.selection===b){
      ctx.strokeStyle='#f9db95';ctx.lineWidth=2;
      ctx.strokeRect(b.tx*TILE,b.ty*TILE,ECON_WIDTH_TILES*TILE,ECON_HEIGHT_TILES*TILE);
      ctx.fillStyle='#1b302bdd';ctx.fillRect(b.x-59,b.y-146,118,20);
      ctx.textAlign='center';ctx.font='bold 12px Consolas,monospace';ctx.fillStyle='#f5e8bd';
      ctx.fillText(econLabel(b.kind)+' '+econCount(b)+'/1명',b.x,b.y-131);
    }
  }
'''
pattern = re.compile(r'  function drawEconomy\(b\)\{.*?(?=  function drawMiner\(v\)\{)',re.S)
text,count=pattern.subn(lambda match:new_renderer,text,count=1)
assert count==1,'Cannot locate economic building renderer'
assert "jobPhase=b.kind==='mine'?'inside':'working'" not in text
assert "v.jobPhase='inside'" in text
assert "NPC_AUTO_CHAT_ENABLED = false" in text
assert "ECON_WIDTH_TILES = 3, ECON_HEIGHT_TILES = 2" in text
game.write_text(text,encoding='utf-8')

if html.exists():
    h=html.read_text(encoding='utf-8')
    h=h.replace('v0.3.8','v0.3.9')
    html.write_text(h,encoding='utf-8')
print('v0.3.9: farm workers hidden after entry, mine/farm activity animation, output labels and production popups')
