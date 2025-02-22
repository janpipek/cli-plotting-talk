import pandas as pd # HIDE
import numpy as np  # HIDE
# HIDE
df = pd.read_csv("cities.csv", index_col="city")  # HIDE
# Prepare the plotting area
min_lat, max_lat = int(df["latitude"].min()), int(df["latitude"].max()) + 1
min_lon, max_lon = int(df["longitude"].min()), int(df["longitude"].max()) + 1
plotting_area = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]

for name, data in df.iloc[::-1].iterrows():
    lat, lon = data[["latitude", "longitude"]]
    x = int((lon - min_lon) / (max_lon - min_lon) * WIDTH)
    y = int((max_lat - lat) / (max_lat - min_lat) * HEIGHT)
    frac = np.clip(data["population"] / 450_000, 0.1, 1)
    r = int(255 * frac); g = 255 - r // 2; b = 255 - r // 2
    color_ansi = f"\033[38;2;{r};{g};{b}m"
    plotting_area[y][x] = color_ansi + name[0]

for row in plotting_area:
    print("".join(row))
