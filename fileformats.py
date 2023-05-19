# Table of file types and byte sequences known to be at specific file offsets
# Negative offsets are offsets from the end of the file
CRIB_TABLE = {
    "7z": {
        0: b"7z\xbc\xaf\x27\x1c\x00",  # then likely \x04, but not guaranteed
        18: b"\x00\x00",
        26: b"\x00\x00",
        -2: b"\x00\x00"
    },
    "exe": {
        0: b"MZ",
        28: b"\x00" * 12
    },
    "dll": {
        0: b"MZ",
        28: b"\x00" * 12
    },
    "jpg": {
        0: b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01",
        -2: b"\xff\xd9"
    },
    "png": {
        0: b"\x89PNG\x0d\x0a\x1a\x0a\x00\x00\x00\x0dIHDR",
        -12: b"\x00\x00\x00\x00IEND\xae\x42\x60\x82"
    }
}
