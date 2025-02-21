import plotille
import pandas as pd  # HIDE

# HIDE
data = pd.read_csv("spurious_correlations.csv")  # HIDE

fig = plotille.Figure()
try:  # HIDE
    fig.width = WIDTH - 10  # HIDE
    fig.height = HEIGHT - 5  # HIDE
except:  # HIDE
    None  # HIDE
fig.plot(
    data["Year"],
    data["Everest Climbs"],
    lc=200,
    label="Total Number of Successful Mount Everest Climbs",
)
fig.plot(
    data["Year"],
    data["Fuel Used"],
    lc=200,
    label="Jet fuel used in Czechia",
)
print(fig.show(legend=True))
