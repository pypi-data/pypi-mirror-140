import os
from urllib.parse import urlparse

from fti.file_types import FileTypes


def get_file_types_by_url(url: str) -> set[FileTypes]:
    parsed_path = urlparse(url.lower())
    filename = os.path.basename(parsed_path.path)

    if "." not in filename:
        return set()

    file_format = filename.split(".")[-1]

    try:
        return {FileTypes(file_format)}
    except ValueError:
        return set()
