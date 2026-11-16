# Related work and originality (checked by web search, 16 Nov 2026 — not an exhaustive survey)

| Ingredient | Where it already exists | Status for TACET |
|---|---|---|
| Duress / panic PIN with silent alarm | ATM patent US 6,679,422 (similar-format duress PIN); "Panic passwords: authenticating under duress"; duress-resistant admin authentication (passwordresearch.com paper 469); hardware wallets with duress PIN | **Known** |
| Duress tokens derived from an HMAC counter | CANARY protocol (coercion-resistant spoken verification, HOTP/TOTP style) | **Known** |
| Silent alarm channels in OTP tokens | patent family on "Silent Alarm Channels Using One-Time Passcode" (cited in a patent PDF hosted at people.csail.mit.edu/rivest) | **Known** |
| Two-person integrity, secret sharing | military TPI doctrine; vendor "dual control" products | **Known** |
| Constant-rate padding against traffic analysis | independent link padding (arXiv 1708.05044), Katzenpost mixnet padding, Xuan et al. link padding | **Known** |
| Keystroke dynamics | long literature | **Known** (used as weak signal) |
| **Terminal holding neither PIN nor verifier; both PIN classes only checkable at the C2, in a fixed-size encrypted constant-rate frame** | not found in this search | **Combination — our design choice** |
| **Command-level poisoning independent of operator order, with identical terminal/wire/ack behaviour** | not found in this search | **Combination — our design choice** |
| Device-identical verification (PC vs ESP32 simulation) of the whole chain | — | engineering contribution |

We do **not** claim a world first: patents and papers cover each ingredient, and our search could miss prior
combinations. The contribution is the integration, its small MicroPython realisation, and measured limits.
