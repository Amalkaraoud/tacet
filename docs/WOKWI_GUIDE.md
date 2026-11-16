# Running on Wokwi

1. https://wokwi.com/projects/new/micropython-esp32 .
2. Replace `main.py` and `diagram.json`; add the other files of `wokwi/` (New file…).
3. Play; wait for `TACET boot ; profils op1 mu=218 op2 mu=262`.
4. Type `d` in the serial console (or click D with the mouse held) to run S1…S6; each prints `C2>` events and `RESULT`.
5. The 7th `d` starts a new round and unlocks the C2 (administrator action).

Notes: a mouse click is too short for the polling loop, hence the serial keypad mirror. The simulation runs slowly
when the browser tab is in the background. **Saving** from an anonymous session creates a *public* project; sign in
with the Wokwi account linked to GitHub first and choose *Unlisted*. For CI, `wokwi-cli` and the VS Code extension need
`wokwi.toml` and a token created by the account owner (never share it).
