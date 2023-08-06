from fti.file_types import FileTypes


FILE_MIMES: dict[FileTypes, set[str]] = {
    FileTypes._3G2: {"video/3gpp2"},
    FileTypes._3GP: {"video/3gpp"},
    FileTypes._7Z: {"application/x-7z-compressed"},
    FileTypes.AIF: {"audio/x-aiff"},
    FileTypes.AIFC: {"audio/x-aiff"},
    FileTypes.AIFF: {"audio/x-aiff"},
    FileTypes.APK: {"application/vnd.android.package-archive"},
    FileTypes.ASF: {"video/x-ms-asf"},
    FileTypes.AVI: {"video/x-msvideo"},
    FileTypes.BIN: {"application/octet-stream"},
    FileTypes.BMP: {"image/bmp"},
    FileTypes.BZ2: {"application/x-bzip2"},
    FileTypes.CAB: {"application/vnd.ms-cab-compressed"},
    FileTypes.CLASS: {"application/java-vm"},
    FileTypes.CSS: {"text/css"},
    FileTypes.DEB: {"application/x-debian-package"},
    FileTypes.DER: {"application/x-x509-ca-cert"},
    FileTypes.DJV: {"image/vnd.djvu"},
    FileTypes.DJVU: {"image/vnd.djvu"},
    FileTypes.DMG: {"application/x-apple-diskimage"},
    FileTypes.DOC: {"application/msword"},
    FileTypes.DOCX: {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
    FileTypes.EXE: {"application/x-msdownload"},
    FileTypes.FLAC: {"audio/x-flac"},
    FileTypes.GIF: {"image/gif"},
    FileTypes.ICO: {"image/x-icon"},
    FileTypes.ISO: {"application/x-iso9660-image"},
    FileTypes.JAR: {"application/java-archive"},
    FileTypes.JPEG: {"image/jpeg"},
    FileTypes.JPG: {"image/jpeg"},
    FileTypes.MID: {"audio/midi"},
    FileTypes.MIDI: {"audio/midi"},
    FileTypes.MK3D: {"video/x-matroska"},
    FileTypes.MKA: {"audio/x-matroska"},
    FileTypes.MKS: {"video/x-matroska"},
    FileTypes.MKV: {"video/x-matroska"},
    FileTypes.MP3: {"audio/mpeg"},
    FileTypes.MUS: {"application/vnd.musician"},
    FileTypes.ODP: {"application/vnd.oasis.opendocument.presentation"},
    FileTypes.ODS: {"application/vnd.oasis.opendocument.spreadsheet"},
    FileTypes.ODT: {"application/vnd.oasis.opendocument.text"},
    FileTypes.OGA: {"audio/ogg"},
    FileTypes.OGG: {"audio/ogg"},
    FileTypes.OGV: {"video/ogg"},
    FileTypes.PDB: {"application/vnd.palm"},
    FileTypes.PDF: {"application/pdf"},
    FileTypes.PIC: {"image/x-pict"},
    FileTypes.PNG: {"image/png"},
    FileTypes.PPT: {"application/vnd.ms-powerpoint"},
    FileTypes.PPTX: {"application/vnd.openxmlformats-officedocument.presentationml.presentation"},
    FileTypes.PS: {"application/postscript"},
    FileTypes.PSD: {"image/vnd.adobe.photoshop"},
    FileTypes.RAR: {"application/x-rar-compressed"},
    FileTypes.SND: {"audio/basic"},
    FileTypes.SWF: {"application/x-shockwave-flash"},
    FileTypes.TAR: {"application/x-tar"},
    FileTypes.TIF: {"image/tiff"},
    FileTypes.TIFF: {"image/tiff"},
    FileTypes.TXT: {"text/plain"},
    FileTypes.WAV: {"audio/x-wav"},
    FileTypes.WEBM: {"video/webm"},
    FileTypes.WEBP: {"image/webp"},
    FileTypes.WMA: {"audio/x-ms-wma"},
    FileTypes.WMV: {"video/x-ms-wmv"},
    FileTypes.WOFF: {"application/font-woff"},
    FileTypes.XAR: {"application/vnd.xara"},
    FileTypes.XLS: {"application/vnd.ms-excel"},
    FileTypes.XLSX: {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    FileTypes.XML: {"application/xml"},
    FileTypes.ZIP: {"application/zip"},
}


def _check_mime_file_type(mime: str, file_type: FileTypes) -> bool:
    mimes = FILE_MIMES.get(file_type)

    assert mimes

    return mime in mimes


def get_file_types_by_mime(mime: str) -> set[FileTypes]:
    result = set()

    for part in mime.split(" "):
        t_part = part.replace(";", "")
        for file_type in FILE_MIMES:
            if _check_mime_file_type(t_part, file_type):
                result.add(file_type)

    return result
