# PIXEL BASTION 🏰

**제4 프로젝트 · 2D 도트 그래픽 중앙 성 방어 + 마을 경영**

현재 웹게임 코드 기준: **v0.3.6 (여성 NPC 3 추가 · 이동 전용 모드)**

- 반오픈월드 84×84 타일, 중앙 성 방어, 4종 타워, 사방에서 적 등장
- 하급 초가집 3×3, 최대 3채, 1채당 최대 인구 3명, 점진적 입주
- 남녀 주민: 준무작위 1칸 이동, 동일 칸 중복 점유 금지, 대화·감정·인사·수동 상호작용 임시 잠금
- 주민 외형 총 6종(남 3 / 여 3), 4방향 걷기, 3.8FPS, 화면상 높이 90px
- 식량·민심·진화 시스템은 아직 미구현 또는 잠금

## 최초 등록: 분할 ZIP 두 개

두 파일을 **압축 해제하지 않고** 저장소 최상위(root)에 각각 업로드합니다.

1. `PIXEL_BASTION_v0.3.2_PART1_GAME_MALE.zip` — 게임 코드, 남성 NPC 및 게임 기본 그래픽
2. `PIXEL_BASTION_v0.3.2_PART2_FEMALE.zip` — 여성 NPC 리소스

[GitHub 파일 업로드](https://github.com/jarh0907-ui/pixel-bastion/upload/main) → `Commit changes`

배포 작업은 둘 모두 있는 경우 자동으로 압축을 풀어 하나의 웹사이트로 합칩니다. 첫 번째 ZIP만 있을 경우에는 이미지 누락을 막기 위해 실패 처리합니다.

전체 통합 ZIP `PIXEL_BASTION_v0.3.2_FEMALE_NPC_GITHUB.zip` 한 개를 업로드하거나, `index.html`, `game.js`, `style.css`, `assets/` 를 압축 해제하여 직접 루트에 올려도 됩니다.

## GitHub Pages 설정

1. [Settings → Pages](https://github.com/jarh0907-ui/pixel-bastion/settings/pages)에서 **Source: GitHub Actions** 선택
2. [Actions](https://github.com/jarh0907-ui/pixel-bastion/actions)에서 `Deploy PIXEL BASTION` 성공 여부 확인
3. 성공 시 https://jarh0907-ui.github.io/pixel-bastion/ 에서 실행

## 이후 게임 업데이트

초기 리소스가 저장소에 등록되면, `overlays/` 에 같은 상대 경로로 올린 파일을 배포 과정에서 덮어씁니다.

- `overlays/game.js` → 게임 로직 변경
- `overlays/style.css` → UI 변경
- `overlays/index.html` → 화면 수정
- `overlays/assets/config.js` → 이미지 연결 설정
- `overlays/assets/npc/...` → 새 NPC 이미지 교체

즉, 게임 전체 ZIP은 최초에만 필요하며 이후 텍스트 코드 변경은 GitHub 연결을 통해 직접 업데이트할 수 있습니다.

> 최초 v0.3.2 분할 ZIP 등록은 완료되었으며 이후 코드는 GitHub에서 직접 갱신합니다.


## v0.3.3 GitHub 직접 업데이트
- `overlays/patch_v033.py`가 배포 시 v0.3.2 게임 코드에 자동 적용됩니다.
- 기존 60px 주민 표시 높이 → 90px, 기존 3.8 FPS 유지.
- NPC 1(남성), NPC 2(남성), NPC(여성) 세 종류로 분화하고, 감정 표현 시 몸 높이를 고정합니다.
- **남성2의 사용자 제공 원본 PNG 2장 등록 완료:** `overlays/assets/npc/NPC_MALE2/male2_walk_4dir_4frames.png`, `overlays/assets/npc/NPC_MALE2/male2_emotes_6poses.png`.
- GitHub Actions가 기존 분할 ZIP을 조립한 뒤 해당 PNG를 병합하고 `patch_v033.py`에서 원본 PNG를 바로 참조합니다.
- 이미지 2장은 원본 바이트를 변경하지 않고 업로드했습니다. 이후 신규 이미지도 동일한 바이너리 Git 객체 방식으로 반영할 수 있습니다.


## v0.3.4: 여성 NPC 2 및 임시 상호작용 잠금
- 사용자 제공 **여성 NPC 2**의 원본 걷기 PNG(4방향 × 4프레임)와 감정 PNG(6포즈) 등록
- NPC 외형 4종: 남성 1 / 남성 2 / 여성 1 / 여성 2. 입주 시 4종을 고르게 순환
- 주민은 기존과 동일하게 **한 칸에 1명**, 준무작위 이동, 일정 시간 대기
- **잠금:** 주민끼리 5~10초 자동 대화, 자동 감정, 수동 인사·감정·대화. 게임 화면과 선택 패널에서도 모션 버튼 숨김
- 잠금은 일시적이며 감정 이미지 리소스는 보존함
- NPC 표시 높이 90px 고정, 기존 걷기 프레임 속도 유지
- 코드 및 배포 파이프라인: `overlays/patch_v034.py` 가 `patch_v033.py` 다음에 적용됨
- 신규 PNG: `overlays/assets/npc/NPC_FEMALE2/`에서 배포 파일로 자동 포함
- **기존 타워 디펜스, 주택, 입주, 자원 규칙은 변경 없음**


## v0.3.5: 남성 NPC 3 추가
- 새 외형 남성 3 — 4방향 × 4프레임 걷기 및 6포즈 감정 리소스
- 원본 PNG 바이트 그대로 저장: `overlays/assets/npc/NPC_MALE3/male3_walk_4dir_4frames.png`, `male3_emotes_6poses.png`
- 주민 외형 5종: 남성 1·2·3, 여성 1·2. 입주 시 남성 외형 종류를 균형 있게 분배
- 모든 주민의 화면상 높이 90px 유지, 같은 타일 중복 점유 금지
- **이동과 대기만 활성화. 자동 대화·감정·인사·수동 상호작용은 계속 잠금**
- `overlays/patch_v035.py`가 기존 v0.3.4 게임 코드 다음에 적용됨


## v0.3.6: 여성 NPC 3 추가
- 사용자 제공 이미지 한 장에서 **4방향×4프레임 걷기**와 **6종 감정 포즈**를 각각 분리
- 원본 픽셀을 재생성·보간하지 않고 투명 PNG로 제작 (큰 인물 원화는 게임용 걷기 시트에서 제외)
- 등록 경로: `overlays/assets/npc/NPC_FEMALE3/female3_walk_4dir_4frames.png`, `female3_emotes_6poses.png`
- 새로운 주민 외형 총 **6종(남성 1·2·3 / 여성 1·2·3)**. 여성 주민 생성 시 외형의 수를 고려해 배정
- 표시 높이 **90px**, 걷기 **3.8FPS**, 1칸당 주민 1명, 준무작위 이동 유지
- **대기·이동만 활성화**. 대화·감정 표현·인사·수동 상호작용은 계속 잠금, 감정 PNG는 보존
- `overlays/patch_v036.py`를 v0.3.5 패치 다음에 실행하며 GitHub Actions에서 이미지 2종과 코드 유효성을 검사
