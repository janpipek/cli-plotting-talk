import plotext as plt

l = 1000
frames = 200

plt.title("Streaming Data")
# plt.clc()

for i in range(frames):
    plt.clt() # to clear the terminal
    plt.cld() # to clear the data only

    y = plt.sin(periods = 2, length = l, phase = 2 * i  / frames)
    plt.scatter(y)

    plt.sleep(0.001) # to add 
    plt.show()