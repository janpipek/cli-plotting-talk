# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "plotille",
#     "numpy",
# ]
# ///

import numpy as np
from plotille import Figure

fig = Figure()
fig.width=40
fig.height=20

alpha = np.linspace(0, 2 * np.pi, 100)
fig.plot(np.cos(alpha) + 2, np.sin(alpha) + 2, lc='red')

lines = fig.show().split('\n')
