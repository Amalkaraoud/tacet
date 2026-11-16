# Threat model

**Assets**: the irreversible order (amount, action), the operators' PINs, the secrecy of *who is under duress*.

| # | Adversary | Capability | Defence | Residual |
|---|---|---|---|---|
| A1 | Passive eavesdropper | sees (time, size) of every frame | constant rate, fixed size, encrypted type byte | E1 51.0 % |
| A2 | Active on the link | replay, bit-flip, drop | 12-byte link tag, strict counter | drops are indistinguishable from loss |
| A3 | Coercer at the terminal | forces PIN entry, watches screen | duress PIN accepted silently; screen identical | operator must remember/dare; see A5 |
| A4 | Thief of the terminal, no frame | reads flash (keys) | no PIN or verifier stored on the terminal | none beyond key reuse |
| A5 | Thief with key + one captured frame | offline guessing | none built | **E5: 6-digit PIN recovered offline in ~1.9 s** |
| A6 | Single insider | one operator alone | two distinct operators required for EXECUTE | collusion of two |
| A7 | Brute force at the terminal | online PIN guessing | C2 lockout after 3 failures | denial of service by locking |

**Out of scope**: physical radio (jamming, direction finding), side channels, secure boot, real key
management, human factors of duress (hesitation is itself a tell), certification.

**Honest assessments**: (i) duress PIN secrecy is only as good as the operator's ability to enter it
unnoticed; (ii) typing rhythm is a weak signal (E2) and only escalates; (iii) constant-rate cover trades
bandwidth for secrecy (E3: 512 bit/s at a 1 s slot).
