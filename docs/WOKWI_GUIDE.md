# Running on Wokwi

0. **Quickest:** open the ready-made project, already loaded with all files and the circuit: https://wokwi.com/projects/480877116153590785 — then jump to step 3.
1. Or, to rebuild it manually: https://wokwi.com/projects/new/micropython-esp32 (this link opens a blank project by design).
2. Replace `main.py` and `diagram.json`; add the other files of `wokwi/` (New file…).
3. Play; wait for `TACET boot ; profils op1 mu=218 op2 mu=262`.
4. Type `d` in the serial console (or click D with the mouse held) to run S1…S6; each prints `C2>` events and `RESULT`.
5. The 7th `d` starts a new round and unlocks the C2 (administrator action).

Notes: a mouse click is too short for the polling loop, hence the serial keypad mirror. The simulation runs slowly
when the browser tab is in the background. **Saving** creates a project owned by your Wokwi account; on the free plan it is *public* (*Unlisted* needs a paid plan). For CI, `wokwi-cli` and the VS Code extension need
`wokwi.toml` and a token created by the account owner (never share it).
