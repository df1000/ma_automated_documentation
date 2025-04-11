import pathlib
import zipfile

directory_path = pathlib.Path('data/raw_data')

if not directory_path.exists():
    raise FileNotFoundError(f"Directory not found: {directory_path.resolve()}")

archive_path = pathlib.Path("data/raw_data_range_0_300k.zip")
archive_path.parent.mkdir(parents=True, exist_ok=True)

with zipfile.ZipFile(archive_path, mode="w") as archive:
    for file_path in directory_path.iterdir():
        archive.write(file_path, arcname=file_path.name)

