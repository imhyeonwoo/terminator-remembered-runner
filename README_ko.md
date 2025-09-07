# Terminator Remembered Runner

몇 초 만에 작업 환경을 다시 만들어 줍니다. 이 스크립트는 저장해 둔 명령 개수만큼 tmux 창을 자동으로 분할하고, 각 명령을 해당 패널에 주입합니다. 한 번에 `.sh` 배치를 실행하는 대신, Terminator 안에서 각 패널을 인터랙티브하게 제어하고 싶을 때 특히 유용합니다.

## 시연 / 실행 방법 영상

[![Demo Video](https://img.youtube.com/vi/EYaPXOi2hYo/0.jpg)](https://youtu.be/EYaPXOi2hYo)

- YouTube: https://youtu.be/EYaPXOi2hYo
- 시연 / 실행 방법 영상입니다.

## 요구 사항
- Python 3.8+
- tmux (`sudo apt install -y tmux`)
- (선택) 터미널 앱으로 Terminator

## 설치 및 실행
1. 다음 위치에 설정 파일을 만드세요(깃에 커밋하지 마세요):
   - `~/.config/terminator/commands.json`
   - 예시는 저장소의 `commands.example.json`을 참고하세요.

2. 실행:
```bash
python3 remembered_runner.py
```

### `~/.config/terminator/commands.json` 예시
```json
{
  "auto_execute": true,
  "confirm_each": false,
  "commands": [
    "htop",
    "ping -c 3 8.8.8.8",
    "tail -f /var/log/syslog",
    "python3 -m http.server 8000"
  ]
}
```

- `"auto_execute": false`로 설정하면 Enter를 자동으로 누르지 않고 명령만 미리 채웁니다.
- `"confirm_each": true`로 설정하면 각 명령 뒤에 짧은 확인 힌트를 출력해 안전하게 실행할 수 있습니다.

## 특징
- 명령 개수에 맞춰 패널을 자동 분할
- 정돈된 `tiled` 레이아웃 유지
- **tmux 마우스 모드 자동 활성화**(클릭으로 포커스/크기 조절/스크롤)
- 실행마다 고유한 창을 만들어 이름 충돌 방지(`remembered` 세션)

## 유용한 tmux 키
- 패널 전환: `Ctrl-b` + 방향키, 또는 `Ctrl-b` `o`
- 현재 패널 닫기: `Ctrl-b` `x` (확인 `y`)
- 현재 창 닫기: `Ctrl-b` `&`
- 세션 분리: `Ctrl-b` `d`, 이후 `tmux attach -t remembered`로 재접속

## 주의 사항
- 실제 `commands.json`은 커밋하지 마세요(비밀 값이 포함될 수 있음). 저장소의 `commands.example.json`을 사용하세요.
- Terminator 밖에서도 잘 동작합니다. `tmux`를 실행할 수 있는 어떤 터미널이든 OK.

## 라이선스
MIT

