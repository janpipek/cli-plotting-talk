import pandas as pd # HIDE
import numpy as np  # HIDE
import plotille

df = pd.read_csv("cities.csv", index_col="city")  # HIDE
print(
    plotille.hist(
        np.random.normal(size=10000),
        width=WIDTH // 2,
        bins=HEIGHT // 2,
    )
)