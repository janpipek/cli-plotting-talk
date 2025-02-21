for high in range(16):
    for low in range(16):
        colour = low + high * 16
        print(f"\033[38;5;{colour}m██\033[0m", end="")
    print()