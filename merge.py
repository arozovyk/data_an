import os
import json
import pandas as pd

input_folder = "."
output_folder = "json"
output_file = "merged_output.json"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Convert CSV files to JSON
for filename in os.listdir(input_folder):
    if filename.endswith(".csv"):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(
            output_folder, f"{os.path.splitext(filename)[0]}.json")

        df = pd.read_csv(input_path)
        df.to_json(output_path, orient="records", date_format="iso")

        print(f"Converted {filename} to JSON")

# Merge JSON files
merged_data = {}
for filename in os.listdir(output_folder):
    if filename.endswith(".json"):
        filepath = os.path.join(output_folder, filename)

        with open(filepath, "r") as file:
            data = json.load(file)
            for entry in data:
                symbol = entry["Symbol"]
                if symbol not in merged_data:
                    merged_data[symbol] = []
                merged_data[symbol].append({
                    "Date": entry["Date"],
                    "High": entry["High"],
                    "Low": entry["Low"],
                    "Open": entry["Open"],
                    "Close": entry["Close"],
                    "Volume": entry["Volume"],
                    "Marketcap": entry["Marketcap"],
                })

# Save merged data to a single JSON file
with open(os.path.join(output_folder, output_file), "w") as outfile:
    json.dump(merged_data, outfile, indent=2)

print(f"Merged JSON data saved to {output_file}")
