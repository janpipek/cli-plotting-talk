import pandas as pd # HIDE
import plotille

df = pd.read_csv("cities.csv", index_col="city")  # HIDE

fig = plotille.Figure()
fig.width = 58  # WIDTH - 5   # HIDE
fig.height = 15  # HEIGHT     # HIDE
fig.scatter(df["longitude"], df["latitude"], label="Cities")
trip_df = df.loc[["Praha", "Pardubice", "Česká Třebová", "Brno"]]
fig.plot(
    trip_df["longitude"],
    trip_df["latitude"],
    lc="blue",
    marker="⌂",
    label="Train trip",
)
print(fig.show(legend=True))
