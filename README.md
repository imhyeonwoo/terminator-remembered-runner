# Terminator Remembered Runner

Recreate your working environment in seconds: this script splits a tmux window into as many panes as you have saved commands and injects each command into its own pane. Perfect to use inside Terminator when you want interactive, per-pane control rather than a one-shot `.sh` batch.

## Demo / How-To Video

[![Demo Video](https://img.youtube.com/vi/EYaPXOi2hYo/0.jpg)](https://youtu.be/EYaPXOi2hYo)

- YouTube: https://youtu.be/EYaPXOi2hYo
- This is a demo/how-to video.

## Requirements
- Python 3.8+
- tmux (`sudo apt install -y tmux`)
- (Optional) Terminator as your terminal app

## Install & Run
1. Create your config here (do not commit it to Git):
   - `~/.config/terminator/commands.json`
   - Use `commands.example.json` as a template.

2. Run:
```bash
python3 remembered_runner.py
```

### Example `~/.config/terminator/commands.json`
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

- Set `"auto_execute": false` to prefill commands without pressing Enter automatically.
- Set `"confirm_each": true` to print a small hint after each command for safety.

## Features
- Auto-splits panes to match the number of commands
- Keeps a tidy `tiled` layout
- **Automatically enables tmux mouse mode** (click to focus/resize/scroll)
- Avoids name collisions by creating a unique window per run (`remembered` session)

## Handy tmux keys
- Switch panes: `Ctrl-b` + Arrow keys, or `Ctrl-b` `o`
- Close current pane: `Ctrl-b` `x` (confirm with `y`)
- Close current window: `Ctrl-b` `&`
- Detach from session: `Ctrl-b` `d`, then reattach with `tmux attach -t remembered`

## Notes
- Do **not** commit your real `commands.json` (it may contain secrets). Use `commands.example.json` in the repo.
- Works fine even outside Terminator—any terminal that runs `tmux` is OK.

## License
MIT
