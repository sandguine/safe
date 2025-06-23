#!/usr/bin/env python3

import math

print("Testing OLD scaling factor calculations:")
print("=" * 40)

for n in [1, 4, 16, 32, 64]:
    scaling_factor = min(1.0, 0.5 + (n**0.3) * 0.5)
    print(f"n={n}: {scaling_factor:.3f}")

print("\nTesting NEW scaling factor calculations:")
print("=" * 40)

for n in [1, 4, 16, 32, 64]:
    scaling_factor = min(1.0, 0.3 + (n**0.3) * 0.4)
    print(f"n={n}: {scaling_factor:.3f}")

print("\nDetailed NEW calculation:")
for n in [1, 4, 16, 32, 64]:
    n_power = n**0.3
    term = n_power * 0.4
    result = 0.3 + term
    final = min(1.0, result)
    print(f"n={n}: {n_power:.3f} -> {term:.3f} -> {result:.3f} -> {final:.3f}")
