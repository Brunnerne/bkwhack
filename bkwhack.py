#!/usr/bin/env python3

import argparse
import subprocess
import sys

from zipfile import ZipFile
from fileformats import CRIB_TABLE
from logger import log


def load(filename: str) -> ZipFile:
    return ZipFile(filename, mode="r")


def run_cmd(cmd: str) -> str:
    return subprocess.check_output(cmd.split()).decode().strip()


def get_crackable(zip_file: ZipFile) -> dict:
    """
    Find all ZipCrypto encrypted files with supported filetypes.
    Currently, only non-compressed (Store) files are supported.
    """
    crackable = {}
    zip_entries = run_cmd(f"bkcrack -L {zip_file.filename}").split("\n")
    for entry in zip_entries[2:]:
        print(entry)
        info = entry.split()
        if info[1] != "ZipCrypto" or info[2] != "Store":
            continue

        filename = info[6]
        ext = filename.split(".")[-1]
        if ext not in CRIB_TABLE:
            continue

        # Compute absolute crib offsets based on uncompressed file size
        size = int(info[4])
        cribs = CRIB_TABLE[ext]
        offset_cribs = {offset % size: crib for offset, crib in cribs.items()}

        # Index by length of longest crib, then size for easy sorting
        index = (-max(len(c) for c in offset_cribs.values()), size)
        crackable[index] = (filename, offset_cribs)
    print()

    # Sort by fastest crackable
    return dict(sorted(crackable.items())).values()


def recover_keys(zip_file: ZipFile, filename: str, cribs: dict) -> str | None:
    # Build command based on known bytes at specific offsets
    cmd = f"bkcrack -C {zip_file.filename} -c {filename}"
    for offset, crib in cribs.items():
        cmd += f" -x {offset} {crib.hex()}"

    print(f"{cmd}\n")

    p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    for _ in range(4):
        p.stdout.readline()

    # Display bkwhack's internal progress
    for c in iter(lambda: p.stdout.read(1).decode(), ""):
        sys.stdout.write(c)
        if c == ")":
            sys.stdout.flush()
        elif c == "\n":
            break
    print()

    status = p.stdout.readline()
    if b"Could not find the keys" in status:
        return

    for _ in range(3):
        p.stdout.readline()
    keys = p.stdout.readline().decode().strip()

    return keys


def crack(zip_file: ZipFile, output: str) -> bool:
    print()
    log.info(f"Analyzing files in {zip_file.filename}...\n")
    crackable = get_crackable(zip_file)
    if len(crackable) == 0:
        log.error("No supported auto-crackable files found :(")
        return

    log.success(f"Found {len(crackable)} potentially crackable files:")
    for filename, cribs in crackable:
        print(f"  - {filename}")
    print()

    for filename, cribs in crackable:
        log.info(f"Attempting key recovery for '{filename}':\n")
        keys = recover_keys(zip_file, filename, cribs)
        if keys is None:
            log.warning(f"Key recovery failed for file '{filename}'\n")
            continue

        log.success(f"Keys successfully recovered: {keys}\n")

        log.info(f"Generating unencrypted output archive '{output}'...")
        cmd = f"bkcrack -C {zip_file.filename} -k {keys} -D {output}"
        print(f"\n{cmd}\n")
        run_cmd(cmd)
        log.success("Unencrypted archive successfully generated!")

        return True

    log.error("Auto-cracking unsuccessful :(")

    return False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="BKWHACK: bkcrack automation tool"
    )

    parser.add_argument(
        "filename",
        nargs="?",
        metavar="zipfile",
        type=argparse.FileType("rb"),
        help="encrypted ZIP file"
    )

    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="list supported file types"
    )

    parser.add_argument(
        "-o", "--out",
        default="decrypted.zip",
        help="filename for unlocked ZIP file (default: %(default)s)"
    )
    
    args = parser.parse_args()

    if not args.list and args.filename is None:
        parser.error("A filename or --list is required")

    return args


def print_supported_filetypes() -> None:
    print("========================")
    print("  SUPPORTED FILE TYPES")
    print("========================")

    alphabetical = sorted(CRIB_TABLE)
    for i in range(0, len(alphabetical), 5):
        print(*alphabetical[i:i + 5], sep=", ", end=",\n")

    return


def main():
    args = parse_args()
    if args.list:
        print_supported_filetypes()
        return

    zip_file = load(args.filename)
    crack(zip_file, args.out)


if __name__ == "__main__":
    main()
