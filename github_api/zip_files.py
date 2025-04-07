import os
import zipfile

# Specify the directory containing the files
directory_path = "/path/to/directory"
zip_file_name = "raw_data.zip"

# Create a zip file
with zipfile.ZipFile(zip_file_name, 'w') as zipf:
    # Iterate through all files in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        # Check if it's a file (skip directories)
        if os.path.isfile(file_path):
            # Add the file to the zip archive
            zipf.write(file_path, arcname=filename)

print(f"All files in '{directory_path}' have been zipped into '{zip_file_name}'.")
