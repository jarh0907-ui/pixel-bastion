# PIXEL BASTION 🏰

**제4 프로젝트 · 2D 도트 그래픽 중앙 성 방어 + 마을 경영**

현재 웹게임 코드 기준: **v0.3.3 (NPC 이미지 이관 중)**

- 반오픈월드 84×84 타일, 중앙 성 방어, 4종 타워, 사방에서 적 등장
- 하급 초가집 3×3, 최대 3채, 1채당 최대 인구 3명, 점진적 입주
- 남녀 주민: 준무작위 1칸 이동, 동일 칸 중복 점유 금지, 인접 시 5~10초 대화
- 남성 4방향×3프레임 / 여성 4방향×4프레임, 3.8FPS, 동일 표시 높이
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

> 분할 ZIP 업로드 및 README만으로는 아직 게임을 실행할 수 없습니다. GitHub Actions 배포가 완료되었는지 확인하세요.


## v0.3.3 GitHub 직접 업데이트
- `overlays/patch_v033.py`가 배포 시 v0.3.2 게임 코드에 자동 적용됩니다.
- 기존 60px 주민 표시 높이 → 90px, 기존 3.8 FPS 유지.
- NPC 1(남성), NPC 2(남성), NPC(여성) 세 종류로 분화하고, 감정 표현 시 몸 높이를 고정합니다.
- 첨부된 남자2 신규 도트 원본은 GitHub의 텍스트 전용 연결에서 바이너리 업로드 경로가 확보되지 않았으므로 현재는 **임시로 남성1 그림**을 사용합니다.
- 그림 리소스는 `overlays/npc-assets/male2_walk_4dir_4frames.webp.b64` 및 `male2_emotes_6poses.webp.b64`를 저장소에 넣으면 배포 때 자동으로 복원되도록 연결했습니다.
