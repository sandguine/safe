import json
from pathlib import Path

import matplotlib.pyplot as plt

RESULTS_FILE = "results/best_of_n_hhh.json"
PLOT_FILE = "results/best_of_n_hhh.png"

with open(RESULTS_FILE, "r") as f:
    results = json.load(f)

plt.figure(figsize=(10, 6))
for model_id, model_data in results.items():
    model_name = model_data["model_name"]
    sample_sizes = []
    avg_best_scores = []
    for n_key, n_data in model_data["sample_sizes"].items():
        n = int(n_key.split("_")[1])
        sample_sizes.append(n)
        avg_best_scores.append(n_data["avg_best_hhh_score"])
    plt.plot(sample_sizes, avg_best_scores, marker="o", label=model_name)

plt.xlabel("Sample size (n)")
plt.ylabel("Average Best HHH Score")
plt.title("Best-of-n HHH Alignment Curves by Model")
plt.legend()
plt.grid(True)
plt.tight_layout()
Path(PLOT_FILE).parent.mkdir(parents=True, exist_ok=True)
plt.savefig(PLOT_FILE)
plt.show()
print(f"Saved plot to {PLOT_FILE}")
