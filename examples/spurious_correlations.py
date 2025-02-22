import polars as pl  # HIDE
import plotext as plt

plt.clear_figure()   # HIDE
data = pl.read_csv("spurious_correlations.csv")
plt.plot(
    data["Year"], data["Fuel Used"], label="Jet fuel used in Czechia", yside="left"
)
plt.plot_size(50, 15)
plt.plot(
    data["Year"],
    data["Everest Climbs"],
    label="Total Number of Successful Mount Everest Climbs",
    yside="right",
)
plt.xticks([1995, 2000, 2005, 2010])
plt.yticks([3, 4, 5, 6, 7, 8], yside="left")
plt.yticks([100, 200, 300, 400, 500, 600], yside="right")
plt.xlabel("Year")
plt.ylabel("Million Barrels/day", yside="left")
plt.ylabel("Climbers", yside="right")
plt.canvas_color("default")
plt.axes_color("default")
plt.show()
