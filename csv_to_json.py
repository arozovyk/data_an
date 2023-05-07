import os
import pandas as pd

input_folder = "."
output_folder = "json"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for filename in os.listdir(input_folder):
    if filename.endswith(".csv"):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(
            output_folder, f"{os.path.splitext(filename)[0]}.json")

        df = pd.read_csv(input_path)
        df.to_json(output_path, orient="records", date_format="iso")

        print(f"Converted {filename} to JSON")
