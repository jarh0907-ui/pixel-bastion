#!/usr/bin/env python3
"""Apply PIXEL BASTION v0.3.3 using unmodified original PNG sheets."""
import json, re, sys
from pathlib import Path
site=Path(sys.argv[1])
p=site/'game.js'
s=p.read_text(encoding='utf-8')
if 'PIXEL BASTION v0.3.3' in s: sys.exit(0)
m=re.search(r'const NPC_SPECS = (\{[^\n]+\});',s)
if not m: raise SystemExit('Missing v0.3.2 NPC metadata')
d=json.loads(m.group(1))
d['male']['emotes']['bounds']=[[21,23,150,212],[20,23,148,212],[15,23,140,212],[31,24,158,212],[35,45,150,212],[31,14,170,212],[39,24,162,212]]
d['female']['emotes']['bounds']=[[54,34,182,220],[45,34,169,220],[23,34,143,220],[51,34,180,220],[24,36,145,220],[30,36,177,220]]
d['male2']={
 'walk':{'url':'assets/npc/NPC_MALE2/male2_walk_4dir_4frames.png','frameW':144,'frameH':144,'frames':4,'bounds':[
 [[28,16,115,137],[28,16,116,137],[28,16,115,137],[28,16,115,137]],
 [[31,23,112,137],[29,23,114,137],[30,23,113,137],[31,23,113,137]],
 [[29,21,114,137],[30,21,113,137],[29,25,115,137],[29,21,115,137]],
 [[30,22,114,137],[30,22,114,137],[30,22,113,137],[29,22,115,137]]]},
 'emotes':{'url':'assets/npc/NPC_MALE2/male2_emotes_6poses.png','frameW':220,'frameH':232,'poses':['surprised','happy','thinking','greeting_wave','talking_01','talking_02'],'bounds':[
 [28,20,191,225],[34,23,186,225],[27,15,193,225],[30,33,190,225],[25,16,195,225],[44,37,175,225]]},
 'idle':{'url':'assets/npc/NPC_MALE2/male2_walk_4dir_4frames.png','frameW':144,'frameH':144,'bounds':[28,16,115,137]}
}
s=s[:m.start(1)]+json.dumps(d,ensure_ascii=False,separators=(',',':'))+s[m.end(1):]
s=s.replace('PIXEL BASTION v0.3.2','PIXEL BASTION v0.3.3')
s=s.replace('const NPC_DRAW_HEIGHT = 60','const NPC_DRAW_HEIGHT = 90')
s=s.replace('const npcImages = {male:{},female:{}};','const npcImages = Object.fromEntries(Object.keys(NPC_SPECS).map(name=>[name,{}]));')
s=s.replace("const spec=NPC_SPECS[v.gender]||NPC_SPECS.male;","const visualVariant=(v.variant==='male2'&&!npcImages.male2.walk)?'male':(v.variant||v.gender); const spec=NPC_SPECS[visualVariant]||NPC_SPECS.male;")
s=s.replace("const imgs=npcImages[v.gender]||npcImages.male;","const imgs=npcImages[visualVariant]||npcImages.male;")
s=s.replace("const action=v.gender==='female'&&pose==='greeting_bow'?'greeting_wave':pose;","const action=pose==='greeting_bow'&&!spec.emotes.poses.includes('greeting_bow')?'greeting_wave':pose;")
s=s.replace("const gender=starting?'male':counts.female<counts.male?'female':counts.male<counts.female?'male':state.villagers.some(v=>v.variant==='male2')?(Math.random()<.5?'male':'female'):'male';","""const gender=starting?'male':counts.female<counts.male?'female':counts.male<counts.female?'male':(Math.random()<.5?'male':'female');
    const male1=state.villagers.filter(v=>v.variant==='male'||(!v.variant&&v.gender==='male')).length;
    const male2=state.villagers.filter(v=>v.variant==='male2').length;
    const variant=gender==='female'?'female':starting?'male':male2<male1?'male2':male1<male2?'male':(Math.random()<.5?'male':'male2');""")
s=s.replace("type:'villager',gender,homeId:home.id,","type:'villager',gender,variant,homeId:home.id,")
s=s.replace("${t.gender==='female'?'여성':'남성'} 주민","\${t.variant==='male2'?'남성 주민 2':t.gender==='female'?'여성 주민':'남성 주민 1'}")
s=s.replace("\${t.gender==='male'?'<button type=\"button\" data-pose=\"greeting_bow\">🙇 숙여인사</button>':''}","\${(t.variant||t.gender)==='male'?'<button type=\"button\" data-pose=\"greeting_bow\">🙇 숙여인사</button>':''}")
s=s.replace("villagers:state.villagers.map(v=>({id:v.id,gender:v.gender,","villagers:state.villagers.map(v=>({id:v.id,gender:v.gender,variant:v.variant||v.gender,")
s=s.replace('v.y-87','v.y-117').replace('v.y-71','v.y-101')
s=s.replace('w.y>v.y-72','w.y>v.y-104').replace('Math.abs(w.x-v.x)<27','Math.abs(w.x-v.x)<40')
assert 'const NPC_DRAW_HEIGHT = 90' in s and 'const variant=gender' in s
p.write_text(s,encoding='utf-8')
h=site/'index.html'
if h.is_file():
    h.write_text(h.read_text(encoding='utf-8').replace('v0.3.2','v0.3.3'),encoding='utf-8')
print('PIXEL BASTION v0.3.3 NPC visuals patched')
