#!/usr/bin/env python3
"""PIXEL BASTION v0.3.6 — add female NPC 3 (movement-only)."""
import json,re,sys
from pathlib import Path
root=Path(sys.argv[1]);path=root/'game.js'
s=path.read_text(encoding='utf-8')
if 'PIXEL BASTION v0.3.6' in s:
    print('v0.3.6 already applied');sys.exit(0)
assert 'PIXEL BASTION v0.3.5' in s,'Apply patch_v035.py first'
assert 'NPC_INTERACTIONS_ENABLED = false' in s
assert 'NPC_AUTO_CHAT_ENABLED = false' in s
assert 'const NPC_DRAW_HEIGHT = 90' in s
entry={
 'walk':{'url':'assets/npc/NPC_FEMALE3/female3_walk_4dir_4frames.png','frameW':190,'frameH':200,'frames':4,'bounds':[
 [[30,19,159,196],[31,19,159,196],[30,19,159,196],[30,19,159,196]],
 [[35,22,155,196],[35,21,154,196],[35,23,155,196],[35,23,154,196]],
 [[34,30,156,196],[34,31,156,196],[35,30,154,196],[32,29,157,196]],
 [[34,32,156,196],[33,33,156,196],[33,33,156,196],[34,33,156,196]]]},
 'emotes':{'url':'assets/npc/NPC_FEMALE3/female3_emotes_6poses.png','frameW':260,'frameH':300,
   'poses':['surprised','happy','thinking','greeting_wave','talking_01','talking_02'],
   'bounds':[[41,25,218,300],[0,26,260,300],[25,30,234,300],[33,36,227,300],[26,29,234,300],[43,35,217,300]]},
 'idle':{'url':'assets/npc/NPC_FEMALE3/female3_walk_4dir_4frames.png','frameW':190,'frameH':200,
   'bounds':[30,19,159,196]}
}
m=re.search(r'const NPC_SPECS = (\{[^\n]+\});',s)
assert m,'NPC_SPECS missing'
specs=json.loads(m.group(1))
assert all(k in specs for k in ['male','male2','male3','female','female2'])
specs['female3']=entry
s=s[:m.start(1)]+json.dumps(specs,ensure_ascii=False,separators=(',',':'))+s[m.end(1):]
pat=r"    const variant=gender==='female'\?\(female2<female1\?'female2':'female'\):\(starting\?'male':maleAppearance\);"
replacement="""    const femaleKinds=['female','female2','female3'];
    const femaleVariantCount={
      female:state.villagers.filter(v=>(v.variant||v.gender)==='female').length,
      female2:state.villagers.filter(v=>v.variant==='female2').length,
      female3:state.villagers.filter(v=>v.variant==='female3').length
    };
    const femaleAppearance=femaleKinds.reduce((best,k)=>femaleVariantCount[k]<femaleVariantCount[best]?k:best,'female');
    const variant=gender==='female'?femaleAppearance:(starting?'male':maleAppearance);"""
s,n=re.subn(pat,replacement,s,count=1)
assert n==1,'Female variant assignment changed'
vpat=r"const visualVariant=\(v\.variant==='male3'.+?;\n"
vm=re.search(vpat,s)
assert vm,'Visual fallback changed'
visual=vm.group(0)
visual=visual.replace("(v.variant==='female2'&&!npcImages.female2.walk)?'female':",
 "(v.variant==='female3'&&!npcImages.female3.walk)?'female':(v.variant==='female2'&&!npcImages.female2.walk)?'female':")
s=s[:vm.start()]+visual+s[vm.end():]
s=s.replace("const residentKind=t.variant==='male3'?", "const residentKind=t.variant==='female3'?'여성 주민 3':t.variant==='male3'?",1)
s=s.replace('PIXEL BASTION v0.3.5','PIXEL BASTION v0.3.6')
assert 'NPC_AUTO_CHAT_ENABLED = false' in s
path.write_text(s,encoding='utf-8')
h=root/'index.html'
if h.exists():h.write_text(h.read_text(encoding='utf-8').replace('v0.3.5','v0.3.6'),encoding='utf-8')
print('v0.3.6 female NPC3 behavior registered; interactions remain locked')
