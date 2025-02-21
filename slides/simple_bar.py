# Some data
data = {"Praha": 1.3, "Brno": 0.4, "Ostrava": 0.3, "Plzeň": 0.2, "Liberec": 0.1}

label_width = max(len(label) for label in data)
max_value = max(data.values())

for label, value in data.items():
    n_chars = int(value / max_value * 25)
    print(f"  {label:{label_width}} {'#' * n_chars} {value}")