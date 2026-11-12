#!/usr/bin/env python3
"""PIXEL BASTION v0.3.4: female NPC 2 + temporary movement-only citizen mode.

Applied by GitHub Actions after patch_v033.py. Original PNG resources remain unchanged.
"""
import json
import re
import sys
from pathlib import Path

root=Path(sys.argv[1])
source=root/'game.js'
s=source.read_text(encoding='utf-8')
if 'PIXEL BASTION v0.3.4' in s:
    print('v0.3.4 already applied');sys.exit(0)
assert 'PIXEL BASTION v0.3.3' in s, 'Must apply v0.3.3 patch first'

walk_bounds=[
 [[34,17,126,147],[34,17,126,147],[34,17,125,147],[33,17,126,147]],
 [[39,28,120,142],[39,33,120,142],[38,28,121,142],[39,34,120,142]],
 [[36,31,123,144],[35,31,124,143],[35,32,124,142],[36,31,124,143]],
 [[36,24,123,142],[36,22,124,142],[36,22,124,142],[35,21,125,146]]
]
emote_bounds=[[30,12,130,149],[31,12,129,149],[30,10,129,148],[31,22,129,148],[29,10,131,148],[36,22,124,148]]
new={'walk':{'url':'assets/npc/NPC_FEMALE2/female_02_walk_4dir_4frames.png','frameW':160,'frameH':168,'frames':4,'bounds':walk_bounds},
 'emotes':{'url':'assets/npc/NPC_FEMALE2/female_02_emotes_6poses.png','frameW':160,'frameH':168,
 'poses':['surprised','happy','thinking','greeting_wave','talking_01','talking_02'],'bounds':emote_bounds},
 'idle':{'url':'assets/npc/NPC_FEMALE2/female_02_walk_4dir_4frames.png','frameW':160,'frameH':168,'bounds':walk_bounds[0][0]}}
meta=re.search(r'const NPC_SPECS = (\{[^\n]+\});',s)
assert meta,'Could not find NPC sprite metadata'
data=json.loads(meta.group(1))
assert 'male2' in data,'v0.3.3 NPC_MALE2 missing'
data['female2']=new
s=s[:meta.start(1)]+json.dumps(data,ensure_ascii=False,separators=(',',':'))+s[meta.end(1):]

# Add a single shared interaction lock. Residents can continue free roaming and resting.
assert 'const NPC_DRAW_HEIGHT = 90' in s
s,n=re.subn(r'(  const NPC_DRAW_HEIGHT = 90;[^\n]*\n)',
             r'\1  const NPC_INTERACTIONS_ENABLED = false; // Temporarily lock all citizen emotes and manual actions.\n  const NPC_AUTO_CHAT_ENABLED = false; // Temporarily lock citizen-to-citizen conversations.\n',s,count=1)
assert n==1

# Keep the originally established sex selection but alternate the two female sprite variants.
variant_line=re.search(r"^    const variant=gender===.+'female':.+;",s,re.M)
assert variant_line, 'v0.3.3 variant assignment changed'
old=variant_line.group(0)
prefix,tail=old.split("?'female':",1)
new_variant="""    const female1=state.villagers.filter(v=>(v.variant||v.gender)==='female').length;
    const female2=state.villagers.filter(v=>v.variant==='female2').length;
    const variant=gender==='female'?(female2<female1?'female2':'female'):"""+tail
s=s.replace(old,new_variant,1)

# Graceful visual fallback if new PNG has not loaded yet.
old_fallback="const visualVariant=(v.variant==='male2'&&!npcImages.male2.walk)?'male':(v.variant||v.gender);"
new_fallback="const visualVariant=(v.variant==='male2'&&!npcImages.male2.walk)?'male':(v.variant==='female2'&&!npcImages.female2.walk)?'female':(v.variant||v.gender);"
if old_fallback in s:
    s=s.replace(old_fallback,new_fallback,1)

# Disable manual poses and the chat trigger at the actual behavior layer, not only in the UI.
s=s.replace('  function triggerNpcPose(v,pose){', '  function triggerNpcPose(v,pose){\n    if(!NPC_INTERACTIONS_ENABLED)return false;',1)
s=s.replace('  function startNpcChat(a,b){', '  function startNpcChat(a,b){\n    if(!NPC_AUTO_CHAT_ENABLED)return false;',1)

# Do not burn an idle decision on a rejected emotion; residents either rest or move.
old_idle="""        if(chance<.09){
          triggerNpcPose(v,NPC_EMOTE_POSES[Math.floor(rand(0,NPC_EMOTE_POSES.length))]);
        } else if(chance<.23){v.idleTime=rand(.6,1.8);}"""
new_idle="""        if(chance<.23){v.idleTime=rand(.6,1.8);}"""
assert old_idle in s
s=s.replace(old_idle,new_idle,1)

old_auto='    for(let i=0;i<residents.length;i++){\n      const a=residents[i];'
assert old_auto in s
s=s.replace(old_auto,'    if(NPC_AUTO_CHAT_ENABLED)for(let i=0;i<residents.length;i++){\n      const a=residents[i];',1)

# NPC card becomes a read-only information panel: no speech/emotion action buttons.
card_re=re.compile(r"    if\(t\.type==='villager'\)\{\n.*?\n      return;\n    \}", re.S)
card="""    if(t.type==='villager'){
      const residentKind=t.variant==='female2'?'여성 주민 2':t.variant==='female'?'여성 주민 1':t.variant==='male2'?'남성 주민 2':'남성 주민 1';
      ui.inspector.innerHTML=`<div class="inspector-title"><strong>${residentKind} #${t.id}</strong><span class="level">이동 전용</span></div>
      <p class="npc-hint">격자 (${t.tx}, ${t.ty}) · 한 칸에 주민 한 명 · 준무작위 이동<br>현재 감정·인사·대화·상호작용은 모두 잠금 상태입니다.</p>
      <div class="inspector-actions"><button type="button" class="btn btn-ghost" disabled>🔒 상호작용 잠금</button></div>`;
      return;
    }"""
s,n=card_re.subn(lambda m:card,s,count=1)
assert n==1,'Could not replace NPC inspector card'

# Clean up UI messaging and display version.
s=s.replace('PIXEL BASTION v0.3.3','PIXEL BASTION v0.3.4')
s=s.replace('초가집은 최대 3채 · 집 1채당 주민 최대 3명. 주민을 클릭해 모션을 확인하세요.',
            '초가집은 최대 3채 · 집 1채당 주민 최대 3명. 주민의 감정·인사·대화는 임시 잠금입니다.')
source.write_text(s,encoding='utf-8')

html=root/'index.html'
if html.exists():
    t=html.read_text(encoding='utf-8').replace('v0.3.3','v0.3.4')
    t=t.replace('주민 클릭: 감정','주민 상호작용 잠금')
    t=t.replace('주민 클릭으로 상호작용','주민은 이동만 활성화')
    t=t.replace('주민을 클릭하면 감정·대화 모션을 볼 수 있습니다.', '주민의 감정·인사·대화는 임시 잠금 상태입니다.')
    html.write_text(t,encoding='utf-8')

print('PIXEL BASTION v0.3.4 female NPC 2 and movement-only lock applied')