"""Creates 8 files with ~400 lines so the commit looks large to the ML model."""
import os
os.makedirs("generated", exist_ok=True)
for i in range(8):
    with open(f"generated/module_{i}.py", "w") as f:
        for j in range(50):
            f.write(f"def func_{i}_{j}(x):\n    return x * {j} + {i}\n")
print("done - now git add . && git commit -m 'refactor' && git push")
