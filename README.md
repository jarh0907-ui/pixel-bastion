# PIXEL BASTION 🏰

**제4 프로젝트 · 2D 도트 그래픽 중앙 성 방어 + 마을 경영**

현재 웹게임 코드 기준: **v0.3.4 (여성 NPC 2 추가 · 이동 전용 모드)**

- 반오픈월드 84×84 타일, 중앙 성 방어, 4종 타워, 사방에서 적 등장
- 하급 초가집 3×3, 최대 3채, 1채당 최대 인구 3명, 점진적 입주
- 남녀 주민: 준무작위 1칸 이동, 동일 칸 중복 점유 금지, 인접 시 5~10초 대화
- 남성1 4방향×3프레임 / 여성 4방향×4프레임 / 남성2 4방향×4프레임, 3.8FPS, 모든 주민 표시 높이 90px
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
