import serial
import re


def calculate_checksum(nmea_str):
    """Calculate checksum for the NMEA string (excluding $ and *)."""
    checksum = 0
    for char in nmea_str:
        checksum ^= ord(char)
    return f"*{checksum:02X}"


def format_nmea(input_str):
    # Split the sentence by commas to process each field
    parts = input_str.split(",")
    output_parts = ["$WIXDR"]

    needed_sensors = {
        "C": None,  # Celsius temperature
        "H": None,  # Humidity
        "P": None,  # Pressure
    }

    i = 1  # start after the $WIXDR identifier
    while i < len(parts) - 1:  # ignore the checksum part
        sensor_type = parts[i]
        value = parts[i + 1]
        unit = parts[i + 2]

        if sensor_type == "C" and unit == "C":
            value = value.lstrip("+0") if value.lstrip("+0") else "0"
            needed_sensors["C"] = (value, unit)
        elif sensor_type == "H":
            value = value.lstrip("0") if value.lstrip("0") else "0"
            if value.endswith(".0"):
                value = value[:-2]
            needed_sensors["H"] = (value, unit)
        elif sensor_type == "P" and unit == "H":
            value_in_bar = round(float(value) * 0.001, 3)
            needed_sensors["P"] = (f"{value_in_bar:.3f}", "B")
        i += 4

    if needed_sensors["C"]:
        output_parts.extend(["C", needed_sensors["C"][0], needed_sensors["C"][1], ""])
    if needed_sensors["H"]:
        output_parts.extend(["H", needed_sensors["H"][0], "P", ""])
    if needed_sensors["P"]:
        output_parts.extend(["P", needed_sensors["P"][0], "B", ""])

    nmea_str = ",".join(output_parts)
    checksum = calculate_checksum(nmea_str[1:])
    return f"{nmea_str}{checksum}"


# Open the serial port
with serial.Serial("COM5", 4800, timeout=1) as ser:
    while True:
        # Read a line from the serial port
        line = ser.readline().decode("ascii", errors="replace").strip()

        # Check if the line starts with $WIXDR
        if line.startswith("$WIXDR"):
            # Convert the specific $WIXDR sentence
            formatted_str = format_nmea(line)
            print(formatted_str)
        else:
            # Print other lines as-is
            print(line)
