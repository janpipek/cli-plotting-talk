from plottypus.plotting import plot
from plottypus.core import PlotType, Backend
import polars as pl
import numpy as np

df = pl.DataFrame(
    {"a": np.random.normal(size=100), "b": np.random.normal(size=100)}
)
plot(df=df, x="a", y="b", type=PlotType.SCATTER, backend=Backend.KITTY)
