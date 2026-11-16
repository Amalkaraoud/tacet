"""TACET - terminal d'autorisation sous contrainte (ESP32 + MicroPython).

Clavier 4x4 : A/B = operateur 1/2, 6 chiffres + '#' = envoyer, '*' = annuler,
D = scenario de demonstration suivant (S1..S6).
LED verte = ce que voit l'agresseur. LED rouge = verdict C2 (DEMO UNIQUEMENT :
absente d'un vrai terminal).
"""
import sys
import select
import time
from machine import Pin, I2C
import tconfig as cfg
import tproto as P
import tchannel as C
import tscen as S
from ssd1306 import SSD1306_I2C

i2c = I2C(0, scl=Pin(cfg.SCL), sda=Pin(cfg.SDA), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)
led_t = Pin(cfg.LED_TERMINAL, Pin.OUT)
led_a = Pin(cfg.LED_ALARM, Pin.OUT)
rows = [Pin(p, Pin.OUT, value=0) for p in cfg.KP_ROWS]
cols = [Pin(p, Pin.IN, Pin.PULL_DOWN) for p in cfg.KP_COLS]
MAP = ("123A", "456B", "789C", "*0#D")

keys = P.Keys(cfg.MASTER)
term = P.Terminal(keys)
c2 = P.C2(keys, cfg.OPERATORS, bio_thr=cfg.BIO_THRESHOLD)
obs = C.Observer()
link = C.Link(term, c2, obs, slot_ms=cfg.SLOT_MS)
ctx = S.Ctx(link, term, c2)
poll = select.poll()
poll.register(sys.stdin, select.POLLIN)
ALARM = ("DECOY", "HOLD", "DROP_TAMPER", "DROP_REPLAY", "FAIL", "LOCKED")


def scan():
    for r in range(4):
        rows[r].value(1)
        for c in range(4):
            if cols[c].value():
                rows[r].value(0)
                return MAP[r][c]
        rows[r].value(0)
    return None


def show(*lines):
    oled.fill(0)
    for i, l in enumerate(lines[:6]):
        oled.text(l[:16], 0, i * 10)
    oled.show()


def on_event(e):
    k = e["kind"]
    print("C2>", k, {x: e[x] for x in e if x not in ("kind",)})
    led_a.value(1 if k in ALARM else 0)


def summarize(out):
    s, last, n = [], None, 0
    for k in out + [None]:
        if k == last:
            n += 1
            continue
        if last is not None:
            s.append(last + ("x%d" % n if n > 1 else ""))
        last, n = k, 1
    return ">".join(s)


def scenario(i):
    print("=== %s ===" % S.NAMES[i])
    if i == 0:                      # nouveau tour : deverrouillage administrateur
        c2.locked.clear()
        c2.fails.clear()
    led_t.value(0); led_a.value(0)
    show("TACET T-01", S.NAMES[i][:16], "Operateur: saisie", "puis envoi...")
    time.sleep_ms(800)
    out = S.run(i, ctx, on_event)
    led_t.value(1)                         # l'agresseur voit toujours la meme chose
    show("TERMINAL:", "ORDRE TRANSMIS", "[jury] C2:", summarize(out)[:16],
         "trames %d x 64 o" % len(obs.seen), "debit constant")
    print("RESULT", i + 1, out)
    time.sleep_ms(1500)


def idle_screen(msg=""):
    show("TACET T-01", "A/B=operateur", "6 chiffres + #", "D=scenario", msg,
         "tx #%d" % term.ctr)


def main():
    print("TACET boot ; profils op1 mu=%d op2 mu=%d" % (ctx.prof[1].mu_m, ctx.prof[2].mu_m))
    idle_screen()
    nxt = time.ticks_add(time.ticks_ms(), cfg.SLOT_MS)
    op, buf, ts, scen, cmd = None, "", [], 0, 1
    while True:
        k = scan()
        if k is None and poll.poll(0):
            ch = sys.stdin.read(1).upper()
            k = ch if ch in "0123456789ABCD*#" else None
        now = time.ticks_ms()
        if k:
            if k == "D":
                scenario(scen % 6); scen += 1; idle_screen()
            elif k in "AB":
                op, buf, ts = (1 if k == "A" else 2), "", []
                show("Operateur %d" % op, "PIN: ")
            elif k == "*":
                op, buf, ts = None, "", []; idle_screen("annule")
            elif k == "#" and op and len(buf) == cfg.PIN_LEN:
                term.submit(op, buf, cmd, 1, 250000, 0)
                show("TERMINAL:", "ORDRE TRANSMIS"); led_t.value(1)
                op, buf, ts = None, "", []
            elif k.isdigit() and op and len(buf) < cfg.PIN_LEN:
                buf += k; ts.append(now)
                show("Operateur %d" % op, "PIN: " + "*" * len(buf))
            while scan():                  # anti-rebond
                time.sleep_ms(10)
        if time.ticks_diff(now, nxt) >= 0:
            nxt = time.ticks_add(nxt, cfg.SLOT_MS)
            f, ev = link.slot()
            if ev and ev["kind"] != "COVER":
                on_event(ev)
                if ev["kind"] in ("EXECUTE", "DECOY", "HOLD"):
                    cmd += 1
        time.sleep_ms(20)


main()
