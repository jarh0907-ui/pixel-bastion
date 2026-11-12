# PIXEL BASTION 🏰

**제4 프로젝트 · 2D 도트 그래픽 중앙 성 방어 + 마을 경영**

- 현재 기준: **v0.3.2**
- 반오픈월드 84×84 타일, 중앙 성 방어, 4종 타워, 사방에서 적 등장
- 하급 초가집 3×3, 최대 3채, 1채당 최대 인구 3명, 점진적 입주
- 남녀 주민: 준무작위 1칸 이동, 동일 칸 중복 점유 금지, 인접 시 5~10초 대화
- 남성 4방향×3프레임 / 여성 4방향×4프레임, 3.8FPS, 동일 표시 높이
- 식량·민심·진화 시스템은 아직 미구현 또는 잠금

## 최초 등록: 게임 ZIP 단 한 번 업로드

GitHub에 연결된 ChatGPT 도구는 텍스트 파일은 수정할 수 있지만 **로컬 ZIP/PNG 원본을 직접 전송하는 기능은 제공하지 않습니다.** 최초 한 번만 다음 파일을 저장소 최상위에 업로드하면 됩니다.

**파일 이름:** `PIXEL_BASTION_v0.3.2_FEMALE_NPC_GITHUB.zip`

1. ChatGPT 대화의 v0.3.2 ZIP을 한 번 내려받습니다. **압축 해제하지 마세요.**
2. [GitHub 파일 업로드](https://github.com/jarh0907-ui/pixel-bastion/upload/main)에 접속하여 **ZIP 한 개만** 드래그하고 `Commit changes`를 누릅니다.
3. [Settings → Pages](https://github.com/jarh0907-ui/pixel-bastion/settings/pages)에서 **Source: GitHub Actions**를 선택합니다.
4. [Actions](https://github.com/jarh0907-ui/pixel-bastion/actions)에서 배포 작업이 성공하는지 확인합니다.

성공하면 게임 주소는 다음과 같습니다.

**https://jarh0907-ui.github.io/pixel-bastion/**

> 현재 ZIP 업로드 전에는 배포 작업이 실패하도록 설계되어 있습니다. 게임 리소스 없는 빈 페이지를 성공으로 표시하지 않기 위해서입니다.

## 이후 수정은 ZIP을 다시 받을 필요 없음

`overlays/` 안에 동일한 상대경로로 올린 텍스트 파일이 배포 시 원본 ZIP 내용 위에 덮어씌워집니다.

- `overlays/game.js` → 게임 로직 교체
- `overlays/style.css` → UI 변경
- `overlays/index.html` → 화면 구성 변경
- `overlays/assets/config.js` → 이미지 경로 설정 변경
- `overlays/assets/sprites/...` 또는 `overlays/assets/npc/...` → 새 리소스로 교체 (새 PNG 파일은 GitHub 업로드 필요)

따라서 **최초 한 번만 ZIP을 GitHub에 저장하면** 게임 코드 업데이트는 이 저장소에서 직접 진행하고 GitHub Pages가 자동 반영할 수 있습니다.

## 구조

```text
.github/workflows/deploy.yml  ← GitHub Pages 자동 배포
PIXEL_BASTION_v0.3.2_FEMALE_NPC_GITHUB.zip ← 원본 게임 전체 (최초 업로드 필요)
overlays/                    ← 이후 수정 파일 덮어쓰기
README.md
```

원본 ZIP에는 `index.html`, `game.js`, `style.css`, `assets/` 및 원본 도트 리소스가 포함되어 있습니다. 배포 과정에서 자동으로 압축을 풉니다.

---
PIXEL BASTION · GitHub Pages 기반 정적 웹게임 · v0.3.2
