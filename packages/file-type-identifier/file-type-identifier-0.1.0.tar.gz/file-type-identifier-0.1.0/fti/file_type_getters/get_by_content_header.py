from fti.file_types import FileTypes


FILE_HEADERS: dict[FileTypes, set[str]] = {
    FileTypes._3G2: {"66 74 79 70 33 67"},
    FileTypes._3GP: {"66 74 79 70 33 67"},
    FileTypes._7Z: {"37 7A BC AF 27 1C"},
    FileTypes._8SV: {"46 4F 52 4D nn nn nn nn 38 53 56 58"},
    FileTypes._8SVX: {"46 4F 52 4D nn nn nn nn 38 53 56 58"},
    FileTypes.ACBM: {"46 4F 52 4D nn nn nn nn 41 43 42 4D"},
    FileTypes.AIF: {"46 4F 52 4D nn nn nn nn 41 49 46 46"},
    FileTypes.AIFC: {"46 4F 52 4D nn nn nn nn 41 49 46 46"},
    FileTypes.AIFF: {"46 4F 52 4D nn nn nn nn 41 49 46 46"},
    FileTypes.ANBM: {"46 4F 52 4D nn nn nn nn 41 4E 42 4D"},
    FileTypes.ANIM: {"46 4F 52 4D nn nn nn nn 41 4E 49 4D"},
    FileTypes.APK: {"50 4B 03 04", "50 4B 05 06", "50 4B 07 08"},
    FileTypes.ASF: {"30 26 B2 75 8E 66 CF 11 A6 D9 00 AA 00 62 CE 6C"},
    FileTypes.AVI: {"52 49 46 46 nn nn nn nn 41 56 49 20"},
    FileTypes.BAC: {"42 41 43 4B 4D 49 4B 45 44 49 53 4B"},
    FileTypes.BIN: {"53 50 30 31"},
    FileTypes.BMP: {"42 4D"},
    FileTypes.BPG: {"42 50 47 FB"},
    FileTypes.BZ2: {"42 5A 68"},
    FileTypes.CAB: {"4D 53 43 46"},
    FileTypes.CIN: {"80 2A 5F D7"},
    FileTypes.CLASS: {"CA FE BA BE"},
    FileTypes.CMUS: {"46 4F 52 4D nn nn nn nn 43 4D 55 53"},
    FileTypes.CR2: {"49 49 2A 00 10 00 00 00 43 52"},
    FileTypes.CRX: {"43 72 32 34"},
    FileTypes.CWK: {
        "05 07 00 00 42 4F 42 4F 05 07 00 00 00 00 00 00 00 00 00 00 00 01",
        "06 07 E1 00 42 4F 42 4F 06 07 E1 00 00 00 00 00 00 00 00 00 00 01",
    },
    FileTypes.DAT: {"50 4D 4F 43 43 4D 4F 43"},
    FileTypes.DBA: {"00 01 42 44", "BE BA FE CA"},
    FileTypes.DCM: {"44 49 43 4D"},
    FileTypes.DEB: {"21 3C 61 72 63 68 3E"},
    FileTypes.DER: {"30 82"},
    FileTypes.DEX: {"64 65 78 0A 30 33 35 00"},
    FileTypes.DIB: {"42 4D"},
    FileTypes.DJV: {"41 54 26 54 46 4F 52 4D nn nn nn nn 44 4A 56"},
    FileTypes.DJVU: {"41 54 26 54 46 4F 52 4D nn nn nn nn 44 4A 56"},
    FileTypes.DMG: {"78 01 73 0D 62 62 60"},
    FileTypes.DOC: {"D0 CF 11 E0 A1 B1 1A E1"},
    FileTypes.DOCX: {"50 4B 03 04", "50 4B 05 06", "50 4B 07 08"},
    FileTypes.DPX: {"58 50 44 53", "53 44 50 58"},
    FileTypes.EXE: {"4D 5A"},
    FileTypes.EXR: {"76 2F 31 01"},
    FileTypes.FAXX: {"46 4F 52 4D nn nn nn nn 46 41 58 58"},
    FileTypes.FH8: {"41 47 44 33"},
    FileTypes.FITS: {"53 49 4D 50 4C 45 20 20 3D 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 20 54"},
    FileTypes.FLAC: {"66 4C 61 43"},
    FileTypes.FLIF: {"46 4C 49 46"},
    FileTypes.FTXT: {"46 4F 52 4D nn nn nn nn 46 54 58 54"},
    FileTypes.GIF: {"47 49 46 38 37 61", "47 49 46 38 39 61"},
    FileTypes.GZ: {"1F 8B"},
    FileTypes.IBM: {"46 4F 52 4D nn nn nn nn 49 4C 42 4D"},
    FileTypes.ICO: {"00 00 01 00"},
    FileTypes.IDX: {"49 4E 44 58"},
    FileTypes.IFF: {
        "46 4F 52 4D nn nn nn nn 38 53 56 58",
        "46 4F 52 4D nn nn nn nn 41 43 42 4D",
        "46 4F 52 4D nn nn nn nn 41 49 46 46",
        "46 4F 52 4D nn nn nn nn 41 4E 42 4D",
        "46 4F 52 4D nn nn nn nn 41 4E 49 4D",
        "46 4F 52 4D nn nn nn nn 43 4D 55 53",
        "46 4F 52 4D nn nn nn nn 46 41 4E 54",
        "46 4F 52 4D nn nn nn nn 46 41 58 58",
        "46 4F 52 4D nn nn nn nn 46 54 58 54",
        "46 4F 52 4D nn nn nn nn 49 4C 42 4D",
        "46 4F 52 4D nn nn nn nn 53 4D 55 53",
        "46 4F 52 4D nn nn nn nn 59 55 56 4E",
    },
    FileTypes.ILBM: {"46 4F 52 4D nn nn nn nn 49 4C 42 4D"},
    FileTypes.ISO: {"43 44 30 30 31"},
    FileTypes.JAR: {"50 4B 03 04", "50 4B 05 06", "50 4B 07 08"},
    FileTypes.JPEG: {
        "FF D8 FF DB",
        "FF D8 FF E0 nn nn 4A 46 49 46 00 01",
        "FF D8 FF E1 nn nn 45 78 69 66 00 00",
    },
    FileTypes.JPG: {
        "FF D8 FF DB",
        "FF D8 FF E0 nn nn 4A 46 49 46 00 01",
        "FF D8 FF E1 nn nn 45 78 69 66 00 00",
    },
    FileTypes.LBM: {"46 4F 52 4D nn nn nn nn 49 4C 42 4D"},
    FileTypes.LEP: {"cf 84 01"},
    FileTypes.LZ: {"4C 5A 49 50"},
    FileTypes.LZ4: {"04 22 4D 18"},
    FileTypes.MID: {"4D 54 68 64"},
    FileTypes.MIDI: {"4D 54 68 64"},
    FileTypes.MK3D: {"1A 45 DF A3"},
    FileTypes.MKA: {"1A 45 DF A3"},
    FileTypes.MKS: {"1A 45 DF A3"},
    FileTypes.MKV: {"1A 45 DF A3"},
    FileTypes.MLV: {"4D 4C 56 49"},
    FileTypes.MP3: {"FF FB", "49 44 33"},
    FileTypes.MSG: {"D0 CF 11 E0 A1 B1 1A E1"},
    FileTypes.MUS: {
        "46 4F 52 4D nn nn nn nn 43 4D 55 53",
        "46 4F 52 4D nn nn nn nn 53 4D 55 53",
    },
    FileTypes.NES: {"4E 45 53 1A"},
    FileTypes.ODP: {"50 4B 03 04", "50 4B 05 06", "50 4B 07 08"},
    FileTypes.ODS: {"50 4B 03 04", "50 4B 05 06", "50 4B 07 08"},
    FileTypes.ODT: {"50 4B 03 04", "50 4B 05 06", "50 4B 07 08"},
    FileTypes.OGA: {"4F 67 67 53"},
    FileTypes.OGG: {"4F 67 67 53"},
    FileTypes.OGV: {"4F 67 67 53"},
    FileTypes.PDB: {"00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"},
    FileTypes.PDF: {"25 50 44 46"},
    FileTypes.PIC: {"00 nn"},
    FileTypes.PIF: {"00 nn"},
    FileTypes.PNG: {"89 50 4E 47 0D 0A 1A 0A"},
    FileTypes.PPT: {"D0 CF 11 E0 A1 B1 1A E1"},
    FileTypes.PPTX: {"50 4B 03 04", "50 4B 05 06", "50 4B 07 08"},
    FileTypes.PS: {"25 21 50 53"},
    FileTypes.PSD: {"38 42 50 53"},
    FileTypes.RAR: {"52 61 72 21 1A 07 01 00", "52 61 72 21 1A 07 00"},
    FileTypes.RPM: {"ed ab ee db"},
    FileTypes.SEA: {"00 nn"},
    FileTypes.SMU: {"46 4F 52 4D nn nn nn nn 53 4D 55 53"},
    FileTypes.SMUS: {"46 4F 52 4D nn nn nn nn 53 4D 55 53"},
    FileTypes.SND: {
        "46 4F 52 4D nn nn nn nn 38 53 56 58",
        "46 4F 52 4D nn nn nn nn 41 49 46 46",
    },
    FileTypes.STG: {"4D 49 4C 20"},
    FileTypes.SVX: {"46 4F 52 4D nn nn nn nn 38 53 56 58"},
    FileTypes.SWF: {"46 57 53", "43 57 53"},
    FileTypes.TAR: {"75 73 74 61 72 00 30 30 75 73 74 61 72 20 20 00"},
    FileTypes.TAR_GZ: {"1F 8B"},
    FileTypes.TAR_Z: {"1F A0", "1F 9D"},
    FileTypes.TDA: {"00 01 44 54"},
    FileTypes.TIF: {"4D 4D 00 2A", "49 49 2A 00"},
    FileTypes.TIFF: {"4D 4D 00 2A", "49 49 2A 00"},
    FileTypes.TOAST: {"45 52 02 00 00 00 8B 45 52 02 00 00 00"},
    FileTypes.TOX: {"74 6F 78 33"},
    FileTypes.TXT: {"46 4F 52 4D nn nn nn nn 46 54 58 54"},
    FileTypes.VMDK: {"4B 44 4D"},
    FileTypes.VSDX: {"50 4B 03 04", "50 4B 05 06", "50 4B 07 08"},
    FileTypes.WASM: {"6d 73 61 00"},
    FileTypes.WAV: {"52 49 46 46 nn nn nn nn 57 41 56 45"},
    FileTypes.WEBM: {"1A 45 DF A3"},
    FileTypes.WEBP: {"52 49 46 46 nn nn nn nn"},
    FileTypes.WMA: {"30 26 B2 75 8E 66 CF 11 A6 D9 00 AA 00 62 CE 6C"},
    FileTypes.WMV: {"30 26 B2 75 8E 66 CF 11 A6 D9 00 AA 00 62 CE 6C"},
    FileTypes.WOFF: {"77 4F 46 46"},
    FileTypes.WOFF2: {"77 4F 46 32"},
    FileTypes.XAR: {"78 61 72 21"},
    FileTypes.XLS: {"D0 CF 11 E0 A1 B1 1A E1"},
    FileTypes.XLSX: {"50 4B 03 04", "50 4B 05 06", "50 4B 07 08"},
    FileTypes.XML: {"3c 3f 78 6d 6c 20"},
    FileTypes.YTR: {"00 nn"},
    FileTypes.YUV: {"46 4F 52 4D nn nn nn nn 59 55 56 4E"},
    FileTypes.YUVN: {"46 4F 52 4D nn nn nn nn 59 55 56 4E"},
    FileTypes.Z: {"1F A0", "1F 9D"},
    FileTypes.ZIP: {"50 4B 03 04", "50 4B 05 06", "50 4B 07 08"},
}


def _check_template(input_bytes: bytes, template: str) -> bool:
    template_bytes_count = round((len(template) + 1) / 3)

    if len(input_bytes) < template_bytes_count:
        return False

    for loc, part in enumerate(template.split(" ")):
        if part == "nn":
            continue

        if input_bytes[loc] != bytes.fromhex(part)[0]:
            return False

    return True


def _check_content_file_type(input_bytes: bytes, file_type: FileTypes) -> bool:
    for template in FILE_HEADERS[file_type]:
        if _check_template(input_bytes, template):
            return True

    return False


def get_file_types_by_content(input_bytes: bytes) -> set[FileTypes]:
    result = set()

    for file_type in FILE_HEADERS:
        if _check_content_file_type(input_bytes, file_type):
            result.add(file_type)

    return result
