#!/usr/bin/env python3
"""PIXEL BASTION v0.3.8: 3x2 economy footprints, slightly larger art, and global labour limits."""
from pathlib import Path
import sys
root=Path(sys.argv[1])
jp=root/'game.js'; hp=root/'index.html'; css=root/'style.css'
s=jp.read_text(encoding='utf-8')
assert 'PIXEL BASTION v0.3.7' in s, 'Apply patch_v037.py first'
def rep(before,after):
    global s
    n=s.count(before)
    if n!=1: raise RuntimeError(f'v0.3.8 patch expected one snippet; got {n}: {before[:120]!r}')
    s=s.replace(before,after,1)
rep("PIXEL BASTION v0.3.7", "PIXEL BASTION v0.3.8")
rep("const ECON_SIZE = 3, ECON_PRODUCTION_INTERVAL = 10, ECON_FOOD_INTERVAL = 60;", "const ECON_WIDTH_TILES = 3, ECON_HEIGHT_TILES = 2, ECON_PRODUCTION_INTERVAL = 10, ECON_FOOD_INTERVAL = 60;")
rep("  function econLabel(kind){", "  function snapEconomy(wx,wy){\n    const tx=Math.floor(wx/TILE)-1,ty=Math.floor(wy/TILE)-1;\n    return {tx,ty,x:(tx+ECON_WIDTH_TILES/2)*TILE,y:(ty+ECON_HEIGHT_TILES/2)*TILE};\n  }\n  function econLabel(kind){")
rep("tx+ECON_SIZE>=MAP-2||ty+ECON_SIZE>=MAP-2", "tx+ECON_WIDTH_TILES>=MAP-2||ty+ECON_HEIGHT_TILES>=MAP-2")
rep("const x=(tx+1.5)*TILE,y=(ty+1.5)*TILE;", "const x=(tx+ECON_WIDTH_TILES/2)*TILE,y=(ty+ECON_HEIGHT_TILES/2)*TILE;")
rep("for(let j=0;j<ECON_SIZE;j++)for(let i=0;i<ECON_SIZE;i++)", "for(let j=0;j<ECON_HEIGHT_TILES;j++)for(let i=0;i<ECON_WIDTH_TILES;i++)")
rep("도로·물·장애물이 없는 3×3 공간이 필요합니다.", "도로·물·장애물이 없는 가로 3칸 × 세로 2칸 공간이 필요합니다.")
rep("const p=snapHouse(wx,wy),error=econPlaceError(p.tx,p.ty);", "const p=snapEconomy(wx,wy),error=econPlaceError(p.tx,p.ty);")
rep("for(const b of state.economyBuildings)if(Math.abs(x-b.x)<120&&Math.abs(y-b.y)<120)", "for(const b of state.economyBuildings)if(Math.abs(x-b.x)<ECON_WIDTH_TILES*TILE&&Math.abs(y-b.y)<ECON_HEIGHT_TILES*TILE)")
rep("if(tx>=b.tx&&tx<b.tx+ECON_SIZE&&ty>=b.ty&&ty<b.ty+ECON_SIZE)", "if(tx>=b.tx&&tx<b.tx+ECON_WIDTH_TILES&&ty>=b.ty&&ty<b.ty+ECON_HEIGHT_TILES)")
rep("    for(let i=0;i<ECON_SIZE;i++){\n      cells.push({tx:b.tx+i,ty:b.ty-1},{tx:b.tx+i,ty:b.ty+ECON_SIZE},\n        {tx:b.tx-1,ty:b.ty+i},{tx:b.tx+ECON_SIZE,ty:b.ty+i});\n    }", "    for(let i=0;i<ECON_WIDTH_TILES;i++){\n      cells.push({tx:b.tx+i,ty:b.ty-1},{tx:b.tx+i,ty:b.ty+ECON_HEIGHT_TILES});\n    }\n    for(let j=0;j<ECON_HEIGHT_TILES;j++){\n      cells.push({tx:b.tx-1,ty:b.ty+j},{tx:b.tx+ECON_WIDTH_TILES,ty:b.ty+j});\n    }")
rep("ctx.strokeRect(b.tx*TILE,b.ty*TILE,ECON_SIZE*TILE,ECON_SIZE*TILE);", "ctx.strokeRect(b.tx*TILE,b.ty*TILE,ECON_WIDTH_TILES*TILE,ECON_HEIGHT_TILES*TILE);")
rep("const w=144,h=146;", "const w=168,h=172;")
rep("Math.round(b.y-h+35)", "Math.round(b.y-h+43)")
rep("ctx.fillRect(b.x-55,b.y-64,110,100)", "ctx.fillRect(b.x-64,b.y-77,128,115)")
rep("ctx.fillRect(b.x-54,b.y-121,108,20)", "ctx.fillRect(b.x-59,b.y-146,118,20)")
rep("b.x,b.y-106", "b.x,b.y-131")
rep("const h=snapHouse(state.hover.x,state.hover.y);\n      const valid=(isEconomy?", "const h=isEconomy?snapEconomy(state.hover.x,state.hover.y):snapHouse(state.hover.x,state.hover.y);\n      const valid=(isEconomy?")
rep("ctx.fillRect(h.tx*TILE,h.ty*TILE,120,120);", "ctx.fillRect(h.tx*TILE,h.ty*TILE,isEconomy?ECON_WIDTH_TILES*TILE:120,isEconomy?ECON_HEIGHT_TILES*TILE:120);")
rep("ctx.strokeStyle=valid?'#e6eaba':'#f59c87';ctx.lineWidth=3;\n      ctx.strokeRect(h.tx*TILE,h.ty*TILE,120,120);", "ctx.strokeStyle=valid?'#e6eaba':'#f59c87';ctx.lineWidth=3;\n      ctx.strokeRect(h.tx*TILE,h.ty*TILE,isEconomy?ECON_WIDTH_TILES*TILE:120,isEconomy?ECON_HEIGHT_TILES*TILE:120);")
rep("if(img)ctx.drawImage(img,h.x-72,h.y-111,144,146);", "if(img)ctx.drawImage(img,h.x-84,h.y-129,168,172);")
rep("if(Math.abs(w.x-b.x)<75&&w.y>b.y-118&&w.y<b.y+55)", "if(Math.abs(w.x-b.x)<86&&w.y>b.y-151&&w.y<b.y+55)")
rep("    const candidates=state.villagers.filter(v=>!v.jobBuildingId && v.partnerId===null)\n      .sort((a,c)=>distance(a.x,a.y,b.x,b.y)-distance(c.x,c.y,b.x,b.y));", "    const candidates=state.villagers.filter(v=>!v.jobBuildingId && v.partnerId===null)\n      .sort((a,c)=>distance(a.x,a.y,b.x,b.y)-distance(c.x,c.y,b.x,b.y));\n    if(!candidates.length){toast('인구 부족: 배치할 주민이 없습니다.');return false;}")
rep("toast('할당 가능한 주민이 없거나 이동 경로를 찾을 수 없습니다.');return false;", "toast('주민이 이동할 수 있는 경로가 없습니다.');return false;")
rep("const free=state.villagers.some(v=>!v.jobBuildingId);", "const free=state.villagers.filter(v=>!v.jobBuildingId).length;")
rep("<div><span>건설 비용·면적</span><strong>시험용 무료·3×3</strong></div>", "<div><span>건설 비용·면적</span><strong>시험용 무료·3×2</strong></div><div><span>미할당 주민</span><strong>${free}명</strong></div>")
rep("${(!remaining||!free||state.paused)?'disabled':''}", "${(!remaining||state.paused)?'disabled':''}")
rep("    buildEconomy:(kind,x,y)=>buildEconomy(kind,x,y),", "    buildEconomy:(kind,x,y)=>buildEconomy(kind,x,y),\n    economyFootprint:()=>({width:ECON_WIDTH_TILES,height:ECON_HEIGHT_TILES}),\n    availableWorkers:()=>state.villagers.filter(v=>!v.jobBuildingId).length,")
assert 'ECON_SIZE' not in s, 'Old 3x3 economy dimension remains'
assert 'const ECON_WORKERS_LV1 = 1' in s
assert 'NPC_INTERACTIONS_ENABLED = false' in s
assert 'NPC_AUTO_CHAT_ENABLED = false' in s
jp.write_text(s,encoding='utf-8')
h=hp.read_text(encoding='utf-8')
assert 'v0.3.7' in h
h=h.replace('v0.3.7','v0.3.8').replace('임시 무료 건설 · 3×3칸','임시 무료 건설 · 가로 3 × 세로 2칸')
hp.write_text(h,encoding='utf-8')
st=css.read_text(encoding='utf-8')
st+='\n/* v0.3.8: keep worker assignment and upgrade controls visible */\n.inspector-actions{flex-wrap:wrap}\n.inspector-actions button{min-width:96px}\n'
css.write_text(st,encoding='utf-8')
print('PIXEL BASTION v0.3.8: economy 3x2, visuals enlarged, available worker count enforced')
