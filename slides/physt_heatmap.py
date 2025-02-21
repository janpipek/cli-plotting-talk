import pandas as pd
import numpy as np
from physt import h2

df = pd.read_csv("examples/worldcities.csv.zip")
h = h2(df["lat"], df["lng"], "fixed_width", bin_width=10, range=((-180, 180), (-60, 60)), weight=df["population"])
print(h)
h.plot(backend="ascii")
 