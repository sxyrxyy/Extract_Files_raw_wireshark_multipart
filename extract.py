import os
import re

# Directory where the script runs
current_dir = os.getcwd()

# Output directory for extracted files
output_dir = os.path.join(current_dir, "extracted_files")
os.makedirs(output_dir, exist_ok=True)

# Define patterns for boundary and filename
boundary_pattern = rb"--[A-Za-z0-9]+"
filename_pattern = rb'Content-Disposition: form-data; name="file"; filename="(.+?)"'

# Function to generate a unique filename
def generate_unique_filename(base_name):
    base, ext = os.path.splitext(base_name)
    counter = 1
    unique_name = base_name
    while os.path.exists(os.path.join(output_dir, unique_name)):
        unique_name = f"{base}_{counter}{ext}"
        counter += 1
    return unique_name

# Function to extract files from a .raw file
def extract_from_raw(file_path):
    print(f"Processing: {file_path}")

    with open(file_path, "rb") as f:
        data = f.read()

    # Find boundary
    boundary_match = re.search(boundary_pattern, data)
    if not boundary_match:
        print(f"Boundary not found in {file_path}! Skipping.")
        return

    boundary = boundary_match.group(0)

    # Split the data by boundary
    parts = data.split(boundary)

    # Extract file parts
    for i, part in enumerate(parts):
        if b"Content-Disposition: form-data; name=\"file\"" in part:
            # Get filename
            filename_match = re.search(filename_pattern, part)
            filename = filename_match.group(1).decode() if filename_match else f"file_{i}.bin"

            # Ensure unique filename
            filename = generate_unique_filename(filename)

            # Extract file content (after Content-Type header)
            file_data = part.split(b"\r\n\r\n", 1)[-1].rstrip(b"--")

            # Save the file
            output_path = os.path.join(output_dir, filename)
            with open(output_path, "wb") as out_file:
                out_file.write(file_data)

            print(f"Extracted: {output_path}")

# Look for all .raw files in the current directory
raw_files = [f for f in os.listdir(current_dir) if f.endswith(".raw")]

if not raw_files:
    print("No .raw files found in the current directory.")
else:
    print(f"Found {len(raw_files)} .raw files. Starting extraction...")
    for raw_file in raw_files:
        extract_from_raw(os.path.join(current_dir, raw_file))

print("Extraction process completed.")
