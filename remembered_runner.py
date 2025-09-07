#!/usr/bin/env python3
"""
Terminator Remembered Runner
- Splits a tmux window into N panes (N = number of commands)
- Injects each saved command into its own pane
- Enables tmux mouse mode automatically (click to focus/resize/scroll)

Usage:
  python3 remembered_runner.py

Config file:
  ~/.config/terminator/commands.json   (not committed to the repo)
  See commands.example.json for the format.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

CONFIG = Path.home() / ".config/terminator/commands.json"
SESSION_NAME = "remembered"
WINDOW_BASE = "run"

WINDOW_ID = None  # e.g. "@3" (tmux window_id)

def _check_tmux():
    if shutil.which("tmux") is None:
        print("tmux is not installed. Run `sudo apt install -y tmux` and try again.")
        sys.exit(1)

def _run(cmd, check=True, capture=False, text=True):
    if capture:
        return subprocess.run(cmd, check=check, stdout=subprocess.PIPE, text=text).stdout
    return subprocess.run(cmd, check=check)

def _tmux(*args, capture=False):
    return _run(["tmux", *args], capture=capture)

def _session_exists():
    res = subprocess.run(
        ["tmux", "has-session", "-t", SESSION_NAME],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return (res.returncode == 0)

def _new_session_get_window_id(win_name: str):
    """Create a new session and return the first window's id."""
    try:
        out = _tmux(
            "new-session", "-d", "-s", SESSION_NAME, "-n", win_name,
            "-P", "-F", "#{window_id}", capture=True
        ).strip()
        if out.startswith("@"):
            return out
    except subprocess.CalledProcessError:
        pass
    _tmux("new-session", "-d", "-s", SESSION_NAME, "-n", win_name)
    time.sleep(0.05)
    return _find_window_id_by_name(win_name)

def _new_window_get_window_id(win_name: str):
    """Create a new window in an existing session and return its id."""
    try:
        out = _tmux(
            "new-window", "-t", SESSION_NAME, "-n", win_name,
            "-P", "-F", "#{window_id}", capture=True
        ).strip()
        if out.startswith("@"):
            return out
    except subprocess.CalledProcessError:
        pass
    _tmux("new-window", "-t", SESSION_NAME, "-n", win_name)
    time.sleep(0.05)
    return _find_window_id_by_name(win_name)

def _find_window_id_by_name(win_name: str):
    """Find a window_id by its name (first match)."""
    out = _tmux("list-windows", "-t", SESSION_NAME, "-F", "#{window_id} #{window_name}", capture=True)
    for line in out.splitlines():
        wid, name = line.strip().split(" ", 1)
        if name == win_name:
            return wid
    return None

def _ensure_session_and_window():
    """If no session: create one. Otherwise: create a new window.
    Sets global WINDOW_ID."""
    global WINDOW_ID
    uniq_name = f"{WINDOW_BASE}-{os.getpid()}"  # avoid name collisions
    if not _session_exists():
        WINDOW_ID = _new_session_get_window_id(uniq_name)
    else:
        WINDOW_ID = _new_window_get_window_id(uniq_name)
    if not WINDOW_ID:
        print("Failed to create or identify tmux window.")
        sys.exit(1)

def _enable_mouse():
    """Enable tmux mouse (click to focus/resize/scroll)."""
    try:
        _tmux("set-option", "-g", "mouse", "on")
    except subprocess.CalledProcessError:
        # fallback for very old versions
        try:
            _tmux("set", "-g", "mouse", "on")
        except subprocess.CalledProcessError:
            pass

def _list_panes():
    out = _tmux("list-panes", "-t", WINDOW_ID, "-F", "#{pane_id}", capture=True).strip()
    return [] if not out else out.splitlines()

def _split_to_count(n: int):
    """Ensure there are exactly n panes in the window (tile layout)."""
    panes = _list_panes()
    if not panes:
        _tmux("split-window", "-h", "-t", WINDOW_ID)
        _tmux("select-layout", "-t", WINDOW_ID, "tiled")
        panes = _list_panes()

    cur = len(panes)
    for i in range(max(0, n - cur)):
        flag = "-h" if (i % 2 == 0) else "-v"
        _tmux("split-window", flag, "-t", WINDOW_ID)
        _tmux("select-layout", "-t", WINDOW_ID, "tiled")

    panes = _list_panes()
    while len(panes) > n:
        _tmux("kill-pane", "-t", panes[-1])
        panes = _list_panes()
        _tmux("select-layout", "-t", WINDOW_ID, "tiled")

    _tmux("select-layout", "-t", WINDOW_ID, "tiled")
    return _list_panes()

def _send_to_pane(pane_id: str, command: str, auto_execute=True, confirm_each=False):
    _tmux("send-keys", "-t", pane_id, command)
    if auto_execute and not confirm_each:
        _tmux("send-keys", "-t", pane_id, "C-m")
    elif confirm_each:
        _tmux("send-keys", "-t", pane_id, " # <- review then press Enter", "C-m")

def main():
    _check_tmux()

    if not CONFIG.exists():
        print(f"Config file not found: {CONFIG}")
        sys.exit(1)

    try:
        data = json.loads(CONFIG.read_text())
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        sys.exit(1)

    commands = data.get("commands", [])
    if not commands:
        print("No commands in config. Please populate the 'commands' array.")
        sys.exit(0)

    auto_execute = bool(data.get("auto_execute", True))
    confirm_each = bool(data.get("confirm_each", False))

    _ensure_session_and_window()
    _enable_mouse()

    panes = _split_to_count(len(commands))
    for pane_id, cmd in zip(panes, commands):
        _send_to_pane(pane_id, cmd, auto_execute=auto_execute, confirm_each=confirm_each)

    _tmux("select-window", "-t", WINDOW_ID)
    os.execvp("tmux", ["tmux", "attach-session", "-t", SESSION_NAME])

if __name__ == "__main__":
    main()
