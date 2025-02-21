# Some data
import pandas as pd

df = pd.read_csv("cities.csv", index_col="city").sort_values(
    "population", ascending=False
)
data = df.iloc[:20]["population"].to_dict()

# Some measurements
MAX_BAR_WIDTH = 40
label_width = max(len(label) for label in data)
max_value = max(data.values())

# Draw line of various widths
for label, value in data.items():
    n_chars = int(value / max_value * WIDTH / 2)
    print(f"  {label:{label_width}} {'█' * n_chars} {value}")
