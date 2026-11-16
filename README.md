# TACET — Coercion-aware authorisation over a covert, constant-rate link

**Wokwi simulation:** https://wokwi.com/projects/480877116153590785

> *tacet* (Latin): "it is silent". A MicroPython terminal that lets two operators authorise an
> irreversible order (a wire transfer, a command release) **even when one of them is being forced**,
> without the coercer — or a network eavesdropper — being able to tell.

Academic project — MicroPython course MPI1, Faculté des Sciences de Sfax, 2026-2027.
Author: **Amal Karaoud** · Supervisor: **Roua Torjmen**. Defensive security only.

## Why

Military command-and-control and banking share one hard problem: a high-value, irreversible action
must be authorised by a human at an embedded terminal, over a link an adversary can watch, while the
human may be under duress. Existing pieces are well known (duress PIN, two-person rule, constant-rate
padding, keystroke dynamics). TACET's question is narrower: *can they be combined in a terminal so
that nothing observable — on the device, on the wire, on the screen — separates a coerced order from a
genuine one, while the control centre still reacts correctly?*

## What it does

| Property | Mechanism | Evidence |
|---|---|---|
| Wire looks identical whether or not an order is sent | one 64-byte encrypted frame per slot, real or cover | E1: eavesdropper accuracy 51.0 % (vs 100 % for event-driven) |
| A captured terminal reveals no duress semantics | terminal never verifies a PIN; normal and duress PIN are known only to the C2 | tests, Wokwi S2 |
| Coerced order is silently neutralised | C2 returns `DECOY`; terminal still shows "ORDER SENT" | Wokwi S2 |
| One coerced operator poisons the two-person order, in any order | command-level poisoning | `test_duress_first_then_normal_still_decoy` |
| Implicit stress signal | typing-rhythm score fused at the C2 → `HOLD` | E2 (synthetic) — weak alone, see limits |
| Replay / tamper / brute force | link tag + counter, 3-strikes lockout | Wokwi S4–S6 |

## Quick start

```bash
python -m pytest -q tests          # 13 tests, CPython
python tools/run_scenarios.py      # reference output for the six scenarios
python experiments/run_experiments.py && python experiments/e2_bio.py
```

On Wokwi: create a *MicroPython ESP32* project, copy the files of `wokwi/` (including
`diagram.json`), press Play, then type `d` in the serial console (or press D on the keypad) to step
through scenarios S1–S6. See `docs/WOKWI_GUIDE.md`.

## Layout

```
firmware/   MicroPython sources (tcrypto, tproto, tbio, tchannel, tscen, main, ssd1306, tconfig)
wokwi/      flat copy for Wokwi + diagram.json
tests/      13 property tests        experiments/  E1 E2 E3 E5        results/  measured JSON
tools/      scenario runner, figures docs/        architecture, threat model, related work, defence guide
```

## Honest limits

* The **radio is modelled, not simulated**. `tchannel.py` models a constant-rate link, loss and an
  observer. Real hardware would be ESP32 + LoRa module; Wokwi has no such part.
* The C2 runs **on the same MCU** in the Wokwi demo (it is a pure-Python module that also runs on a PC).
* The operator in scenarios is **scripted** (deterministic integer LCG), not human.
* Typing-rhythm results are **synthetic** (assumptions in `experiments/e2_bio.py`): at z = 3 the false
  positive rate is 2.0 % and detection 52 %. It is therefore a risk escalator (`HOLD`), never a lock.
* **E5**: if the terminal key *and* one captured auth frame are stolen, a 6-digit PIN falls offline
  in about two seconds. Mitigations (slow KDF, hardware secure element, longer PIN) are listed, not built.
* Demo keys in `tconfig.py` are public. Do not reuse them.

## Licence

MIT — see `LICENSE`.
