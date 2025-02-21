import plotext as plt
import random

l = 7 * 10 ** 4
data1 = [random.gauss(0, 1) for el in range(10 * l)]
data2 = [random.gauss(3, 1) for el in range(6 * l)]
data3 = [random.gauss(6, 1) for el in range(4 * l)]

bins = 60
plt.hist(data1, bins, label = "mean 0")
plt.hist(data2, bins, label = "mean 3")
plt.hist(data3, bins, label = "mean 6")

plt.title("Histogram Plot")
plt.show()
plt.clear_figure()