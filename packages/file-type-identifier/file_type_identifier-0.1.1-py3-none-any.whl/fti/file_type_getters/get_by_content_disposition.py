from fti.file_types import FileTypes


def get_file_types_by_content_disposition(content_disposition: str) -> set[FileTypes]:
    filename = None

    for part in content_disposition.split(" "):
        if part.lower().startswith("filename="):
            filename = part.lower().replace("filename=", "").replace('"', "").replace(";", "")
            break

    if filename is None:
        return set()

    if "." not in filename:
        return set()

    file_format = filename.split(".")[-1]

    try:
        return {FileTypes(file_format)}
    except ValueError:
        return set()
