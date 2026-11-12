#!/usr/bin/env python3
"""PIXEL BASTION v0.3.5: male NPC 3; keep all citizens in movement-only mode."""
import json, re, sys
from pathlib import Path

root=Path(sys.argv[1])
path=root/'game.js'
s=path.read_text(encoding='utf-8')
if 'PIXEL BASTION v0.3.5' in s:
    print('v0.3.5 already applied')
    sys.exit(0)
assert 'PIXEL BASTION v0.3.4' in s, 'Apply patch_v034.py first'
assert 'NPC_INTERACTIONS_ENABLED = false' in s
assert 'NPC_AUTO_CHAT_ENABLED = false' in s

entry={
 'walk':{
   'url':'assets/npc/NPC_MALE3/male3_walk_4dir_4frames.png',
   'frameW':160,'frameH':176,'frames':4,
   'bounds':[
    [[32,35,127,161],[33,35,127,161],[33,35,127,161],[33,35,127,161]],
    [[32,35,128,161],[32,35,128,161],[31,35,128,161],[31,35,128,161]],
    [[28,35,131,161],[29,35,131,161],[29,35,131,161],[28,35,132,161]],
    [[27,35,133,161],[28,35,132,161],[27,35,132,161],[26,35,133,161]]
   ]},
 'emotes':{
   'url':'assets/npc/NPC_MALE3/male3_emotes_6poses.png',
   'frameW':160,'frameH':176,
   'poses':['surprised','happy','thinking','greeting_wave','talking_01','talking_02'],
   'bounds':[[27,8,132,161],[28,8,132,161],[30,10,130,161],[28,22,131,161],[30,10,129,161],[31,22,128,161]]
 },
 'idle':{
   'url':'assets/npc/NPC_MALE3/male3_walk_4dir_4frames.png',
   'frameW':160,'frameH':176,
   'bounds':[32,35,127,161]
 }
}
meta=re.search(r'const NPC_SPECS = (\{[^\n]+\});',s)
assert meta,'NPC_SPECS missing'
specs=json.loads(meta.group(1))
assert all(n in specs for n in ('male','female','male2','female2'))
specs['male3']=entry
s=s[:meta.start(1)]+json.dumps(specs,ensure_ascii=False,separators=(',',':'))+s[meta.end(1):]

# Add the third male appearance without changing total population, home limits, or gender balance.
pat=re.compile(r'^    const variant=gender===.+;$',re.M)
hit=pat.search(s)
assert hit,'Variant assignment missing'
replacement="""    const maleKinds=['male','male2','male3'];
    const maleVariantCount={
      male:state.villagers.filter(v=>(v.variant||v.gender)==='male').length,
      male2:state.villagers.filter(v=>v.variant==='male2').length,
      male3:state.villagers.filter(v=>v.variant==='male3').length
    };
    const maleAppearance=maleKinds.reduce((best,k)=>maleVariantCount[k]<maleVariantCount[best]?k:best,'male');
    const variant=gender==='female'?(female2<female1?'female2':'female'):(starting?'male':maleAppearance);"""
s=s[:hit.start()]+replacement+s[hit.end():]

# Preserve a nonblank resident while new images load.
old="const visualVariant=(v.variant==='male2'&&!npcImages.male2.walk)?'male':(v.variant==='female2'&&!npcImages.female2.walk)?'female':(v.variant||v.gender);"
new="const visualVariant=(v.variant==='male3'&&!npcImages.male3.walk)?'male':(v.variant==='male2'&&!npcImages.male2.walk)?'male':(v.variant==='female2'&&!npcImages.female2.walk)?'female':(v.variant||v.gender);"
assert old in s,'Visual fallback changed'
s=s.replace(old,new,1)

old_label="const residentKind=t.variant==='female2'?'여성 주민 2':t.variant==='female'?'여성 주민 1':t.variant==='male2'?'남성 주민 2':'남성 주민 1';"
new_label="const residentKind=t.variant==='male3'?'남성 주민 3':t.variant==='female2'?'여성 주민 2':t.variant==='female'?'여성 주민 1':t.variant==='male2'?'남성 주민 2':'남성 주민 1';"
assert old_label in s,'Resident label changed'
s=s.replace(old_label,new_label,1)

s=s.replace('PIXEL BASTION v0.3.4','PIXEL BASTION v0.3.5')
assert 'NPC_INTERACTIONS_ENABLED = false' in s
assert 'NPC_AUTO_CHAT_ENABLED = false' in s
assert 'const NPC_DRAW_HEIGHT = 90' in s
path.write_text(s,encoding='utf-8')
html=root/'index.html'
if html.is_file():
    html.write_text(html.read_text(encoding='utf-8').replace('v0.3.4','v0.3.5'),encoding='utf-8')
print('PIXEL BASTION v0.3.5 male3 integrated; movement-only lock retained')
