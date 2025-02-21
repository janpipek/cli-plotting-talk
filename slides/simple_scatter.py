# Some data
import pandas as pd; import numpy as np
df = pd.read_csv("cities.csv", index_col="city")

# Prepare the plotting area
WIDTH=80; HEIGHT=20
min_lat, max_lat = int(df["latitude"].min()), int(df["latitude"].max()) + 1
min_lon, max_lon = int(df["longitude"].min()), int(df["longitude"].max()) + 1
plotting_area = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]

for name, data in df.iterrows():
    lat, lon = data[["latitude", "longitude"]]
    x = int((lon - min_lon) / (max_lon - min_lon) * WIDTH)
    y = int((max_lat - lat) / (max_lat - min_lat) * HEIGHT)
    frac = np.clip(data["population"] / 450_000, 0.1, 1) 
    b = int(255 * frac); g = 255 - b; r = 255 - b
    pop_color = f"\033[38;2;{r};{g};{255}m"
    plotting_area[y][x] = pop_color + name[0]

for row in plotting_area:
    print("".join(row))
