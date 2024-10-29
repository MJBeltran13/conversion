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

    # Start creating the output with the header
    output_parts = ["$WIXDR"]

    # Mapping for extracting needed sensor values
    needed_sensors = {
        "C": None,  # Celsius temperature
        "H": None,  # Humidity
        "P": None,  # Pressure
    }

    # Loop through the parts, identifying the relevant sensor data
    i = 1  # start after the $WIXDR identifier
    while i < len(parts) - 1:  # ignore the checksum part
        sensor_type = parts[i]
        value = parts[i + 1]
        unit = parts[i + 2]

        # Check for Celsius temperature and remove leading '+0' if needed
        if sensor_type == "C" and unit == "C":
            value = value.lstrip("+0") if value.lstrip("+0") else "0"
            needed_sensors["C"] = (value, unit)
        # Check for humidity, remove leading '0' and trailing '.0' if needed
        elif sensor_type == "H":
            value = value.lstrip("0") if value.lstrip("0") else "0"
            if value.endswith(".0"):
                value = value[:-2]  # Remove the .0
            needed_sensors["H"] = (value, unit)
        # Check for pressure and convert from hPa to bars if needed
        elif sensor_type == "P" and unit == "H":
            # Convert hPa to bars and round to three decimal places
            value_in_bar = round(float(value) * 0.001, 3)  # hPa to Bar conversion
            needed_sensors["P"] = (
                f"{value_in_bar:.3f}",
                "B",
            )  # Format to 3 decimal places
        i += 4  # Move to the next data segment

    # Populate output parts with the required data in the specified format
    if needed_sensors["C"]:
        output_parts.extend(["C", needed_sensors["C"][0], needed_sensors["C"][1], ""])
    if needed_sensors["H"]:
        output_parts.extend(["H", needed_sensors["H"][0], "P", ""])
    if needed_sensors["P"]:
        output_parts.extend(
            ["P", needed_sensors["P"][0], "B", ""]
        )  # Added the additional comma and B

    # Join the output parts and calculate the checksum
    nmea_str = ",".join(output_parts)
    checksum = calculate_checksum(nmea_str[1:])  # exclude '$' for checksum calculation

    return f"{nmea_str}{checksum}"


# Example usage
input_str = "$WIXDR,C,+034.3,C,TEMP,C,+062.6,F,DEWP,P,1008.3,H,PRESS,H,048.0,P,RH*32"
output_str = format_nmea(input_str)
print(output_str)
