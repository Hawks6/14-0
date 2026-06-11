import numpy as np

for max_pct in [50, 60, 70, 80, 90, 99]:
    cost = 4.0 + (max_pct / 99.0) ** 1.8 * 11.0
    print(f"Old: max_pct {max_pct} -> cost {cost:.1f}")

# Proposed new formula:
# We want min ~ 5.0, max ~ 13.0
# Say: 5.0 + (max_pct / 99.0) ** 2.0 * 8.0
# At 50: 5.0 + (50/99)**2 * 8.0 = 5.0 + 0.255 * 8.0 = 7.0
# At 99: 5.0 + 1 * 8.0 = 13.0
for max_pct in [50, 60, 70, 80, 90, 99]:
    cost = 5.0 + (max_pct / 99.0) ** 2.5 * 8.0
    print(f"New1: max_pct {max_pct} -> cost {cost:.1f}")

# Or even lower to average ~8.0:
# base 5.0, range 7.0 => max 12.0
# cost = 4.5 + (max_pct / 99.0) ** 2.0 * 7.5
for max_pct in [50, 60, 70, 80, 90, 99]:
    cost = 4.5 + (max_pct / 99.0) ** 2.5 * 7.5
    print(f"New2: max_pct {max_pct} -> cost {cost:.1f}")

