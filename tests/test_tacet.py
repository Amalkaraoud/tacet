import os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "firmware"))
import tproto as P, tchannel as C, tbio as B, tconfig as cfg
from tcrypto import hmac_sha256


def mk(**kw):
    keys = P.Keys(cfg.MASTER)
    ex = []
    t = P.Terminal(keys)
    c = P.C2(keys, cfg.OPERATORS, on_execute=lambda *a: ex.append(a), **kw)
    return t, c, ex


def run(t, c, n=1):
    out = []
    for _ in range(n):
        out.append(c.receive(t.next_frame()))
    return out


def test_cover_and_fixed_size():
    t, c, _ = mk()
    fs = [t.next_frame() for _ in range(20)]
    assert {len(f) for f in fs} == {64}
    assert all(c.receive(f)["kind"] == "COVER" for f in fs)


def test_two_person_execute():
    t, c, ex = mk()
    t.submit(1, "482915", 7, 1, 250000)
    t.submit(2, "739206", 7, 1, 250000)
    k = [e["kind"] for e in run(t, c, 2)]
    assert k == ["PENDING", "EXECUTE"] and ex == [(7, 1, 250000)]


def test_single_operator_never_executes():
    t, c, ex = mk()
    t.submit(1, "482915", 7, 1, 1)
    t.submit(1, "482915", 7, 1, 1)
    assert [e["kind"] for e in run(t, c, 2)][-1] == "PENDING" and not ex


def test_duress_pin_silent_decoy():
    t, c, ex = mk()
    t.submit(1, "482915", 8, 1, 9)
    t.submit(2, "739260", 8, 1, 9)        # PIN de contrainte
    k = [e["kind"] for e in run(t, c, 2)]
    assert k == ["PENDING", "DECOY"] and not ex


def test_duress_first_then_normal_still_decoy():
    t, c, ex = mk()
    t.submit(2, "739260", 8, 1, 9)
    t.submit(1, "482915", 8, 1, 9)
    assert [e["kind"] for e in run(t, c, 2)] == ["DECOY", "DECOY"] and not ex


def test_duress_frame_same_size_and_shape():
    t1, _, _ = mk(); t2, _, _ = mk()
    t1.submit(1, "482915", 1, 1, 5); t2.submit(1, "482951", 1, 1, 5)
    assert len(t1.next_frame()) == len(t2.next_frame()) == 64


def test_replay_and_tamper_dropped():
    t, c, ex = mk()
    t.submit(1, "482915", 3, 1, 1)
    f = t.next_frame()
    assert c.receive(f)["kind"] == "PENDING"
    assert c.receive(C.replay(f))["kind"] == "DROP_REPLAY"
    t.submit(2, "739206", 3, 1, 1)
    f2 = t.next_frame()
    assert c.receive(C.tamper(f2))["kind"] == "DROP_TAMPER"


def test_wrong_pin_lockout():
    t, c, _ = mk()
    for _ in range(3):
        t.submit(1, "000000", 4, 1, 1)
    ks = [e["kind"] for e in run(t, c, 3)]
    assert ks == ["FAIL"] * 3 and 1 in c.locked
    t.submit(1, "482915", 4, 1, 1)
    assert run(t, c)[0]["kind"] == "LOCKED"


def test_behavioural_hold():
    t, c, ex = mk()
    t.submit(1, "482915", 5, 1, 1, bio=200)
    t.submit(2, "739206", 5, 1, 1, bio=0)
    assert [e["kind"] for e in run(t, c, 2)] == ["HOLD", "HOLD"] and not ex


def test_window_expiry():
    t, c, ex = mk(window=2)
    t.submit(1, "482915", 6, 1, 1)
    run(t, c, 1); run(t, c, 5)
    t.submit(2, "739206", 6, 1, 1)
    assert run(t, c)[0]["kind"] == "PENDING" and not ex


def test_observer_constant_rate_shape():
    t, c, _ = mk()
    obs = C.Observer(); L = C.Link(t, c, obs)
    t.submit(1, "482915", 9, 1, 1)
    for _ in range(30):
        L.slot()
    s = obs.summary()
    assert s["sizes"] == [64] and s["gaps"] == [1000]


def test_ack_shape_independent_of_outcome():
    t, c, _ = mk()
    assert len(c.ack(1)) == len(c.ack(2)) == 64


def test_bio_profile_separates():
    rnd = random.Random(1)
    def sess(mu, cv):
        t = [0]
        for _ in range(6):
            t.append(t[-1] + max(40, rnd.gauss(mu, mu * cv)))
        return t
    p = B.Profile().enrol([sess(220, .18) for _ in range(8)])
    assert p.score(sess(220, .18)) < 96
    assert p.score(sess(120, .3)) >= 96
