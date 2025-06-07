import pathlib
import zipfile
import os

directory_path = pathlib.Path('../data/input_data')

if not directory_path.exists():
    raise FileNotFoundError(f"Directory not found: {directory_path.resolve()}")

archive_path = pathlib.Path("../data/20250430_input_data.zip")
archive_path.parent.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(archive_path, mode="w") as archive:
    for file_path in directory_path.iterdir():
        archive.write(file_path, arcname=file_path.name)


directory = directory_path

# Iterate through the files and delete them
for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    if os.path.isfile(file_path):  # Check if it's a file
        os.remove(file_path)  # Delete the file

# lisa-linux@LAPTOP-VLI78DI6:~/stuff/ma_automated_documentation/github_api$ python3 zip_files.py