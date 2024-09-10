XLSX_FILE_SIGNATURE = [0x50, 0x4B, 0x03, 0x04]
XLS_FILE_SIGNATURE = [0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1]


def is_xlsx_file(file: bytes) -> bool:
    return all(file[i] == byte for i, byte in enumerate(XLSX_FILE_SIGNATURE))


def is_xls_file(file: bytes) -> bool:
    return all(file[i] == byte for i, byte in enumerate(XLS_FILE_SIGNATURE))


def is_excel_file(file: bytes) -> bool:
    return is_xlsx_file(file) or is_xls_file(file)
