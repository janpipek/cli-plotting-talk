from plottypus.plotting import plot
from plottypus.core import PlotType, Backend
import polars as pl

df = pl.DataFrame(
    {"a": [1, 2, 3], "b": [4, 5, 6]}
)
plot(df=df, x="a", y="b", type=PlotType.SCATTER, backend=Backend.PLOTEXT)
