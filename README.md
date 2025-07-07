# Kestrel-1 rover

Firmware (C) and checks (Python) for the Kestrel-1 rover.

| Folder | What is in it |
|---|---|
| src/ | C firmware: motion commands and the ultrasonic range reader |
| tests/ | Checks for the rover's limits |

## Team rule

`main` receives work only by merge, one branch at a time, and every merge is checked
before it is pushed.

## Quick check

    python3 tests/check_limits.py
