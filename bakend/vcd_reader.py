import os

def parse_vcd(file_path):
    signals = {}
    current_time = 0

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"VCD file not found: {file_path}")

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Define signals from $var lines
            if line.startswith("$var"):
                parts = line.split()
                if len(parts) >= 5:
                    symbol = parts[3]
                    name = parts[4]
                    signals[symbol] = {"name": name, "values": []}

            # Update current simulation time
            elif line.startswith("#"):
                try:
                    current_time = int(line[1:])
                except ValueError:
                    continue

            # Capture value changes
            elif not line.startswith("$"):
                value = line[0]
                symbol = line[1:]
                if symbol in signals:
                    signals[symbol]["values"].append({
                        "time": current_time,
                        "value": value
                    })

    return signals
