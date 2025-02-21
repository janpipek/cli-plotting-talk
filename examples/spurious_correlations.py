#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "plotext",
#     "polars",
#     "rich",
# ]
# ///
import polars as pl
import plotext as plt

plt.clear_figure()

#rich.print("[bold]Spurious correlations by Tyler Vigen[/bold]")
#rich.print("[blue]https://tylervigen.com/spurious/correlation/10357_jet-fuel-used-in-czechia_correlates-with_total-number-of-successful-mount-everest-climbs[/blue]")

data = pl.DataFrame({
    "Year": range(1993, 2012),
    "Jet fuel used in Czechia": [2.89315,3.61096,3.88493,2.92896,3.40822,4.03562,3.80274,4.13388,4.42192,4.21096,5.41644,6.93169,7.23288,7.32055,7.94247,8.3306,7.72603,7.12055,7.38356,],
    "Total Number of Successful Mount Everest Climbs": [129,51,83,95,85,121,118,145,182,159,267,337,307,493,633,423,457,543,542,],
})

# plt.title("Spurious correlations")
plt.plot(
    data["Year"],
    data["Jet fuel used in Czechia"],
    label="Jet fuel used in Czechia",
    yside = "left"
)
plt.plot_size(50, 15)
plt.plot(
    data["Year"],
    data["Total Number of Successful Mount Everest Climbs"],
    label="Total Number of Successful Mount Everest Climbs",
    yside = "right"
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
