"""TACET - configuration de DEMONSTRATION. Ne jamais reutiliser ces secrets."""
MASTER = b"TACET-DEMO-MASTER-KEY-0001-NOT-SECRET"
OPERATORS = {1: ("482915", "482951"),   # op -> (PIN normal, PIN contrainte)
             2: ("739206", "739260")}
BIO_THRESHOLD = 96
SLOT_MS = 1000
PIN_LEN = 6
# Broches ESP32 (voir docs/WIRING.md)
KP_ROWS = (32, 33, 25, 26)
KP_COLS = (27, 23, 19, 18)
SDA, SCL = 21, 22
LED_TERMINAL, LED_ALARM = 4, 16
