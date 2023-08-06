import zipfile
from pathlib import Path

import requests

from data_quality_check.utils.paths import get_data_path


def download_file(file_name: str, url: str) -> Path:
    data_path = get_data_path()
    data_path.mkdir(exist_ok=True)

    file_path = data_path / file_name

    if not file_path.exists():
        response = requests.get(url)
        file_path.write_bytes(response.content)

    return file_path


def download_zipped_file(file_name: str, url: str) -> Path:
    data_path = get_data_path()
    data_path.mkdir(exist_ok=True)

    file_path = data_path / file_name

    if not file_path.exists():
        response = requests.get(url)
        if response.status_code != 200:
            raise FileNotFoundError("Could not download resource")

        tmp_path = data_path / "tmp.zip"
        tmp_path.write_bytes(response.content)

        with zipfile.ZipFile(tmp_path, "r") as zip_file:
            zip_file.extract(file_path.name, data_path)

        tmp_path.unlink()

    return file_path.as_uri().__str__()
