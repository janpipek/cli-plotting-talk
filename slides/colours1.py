print("\033[31m Red text \033[0m")  # Red text
print("\033[1;32m Bold green text \033[0m")  # Bold green text

for high in range(16):
    for low in range(16):
        colour = low + high * 16
        print(f"\033[38;5;{colour}m██\033[0m", end="")
    print()
