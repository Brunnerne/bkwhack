#!/usr/bin/env python3

import argparse
import subprocess
import sys

from zipfile import ZipFile
from fileformats import CRIB_TABLE


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
        info = entry.split()
        if info[1] != "ZipCrypto" or info[2] != "Store":
            continue

        filename = info[6]
        ext = filename.split(".")[-1]
        if ext not in CRIB_TABLE:
            continue

        # Compute actual offsets based on file size
        size = int(info[4])
        cribs = CRIB_TABLE[ext]
        offset_cribs = {offset % size: crib for offset, crib in cribs.items()}
        crackable[filename] = offset_cribs

    return crackable


def recover_keys(zip_file: ZipFile, filename: str, cribs: dict) -> str:
    # Build command based on known bytes at specific offsets
    cmd = f"bkcrack -C {zip_file.filename} -c {filename}"
    for offset, crib in cribs.items():
        cmd += f" -x {offset} {crib.hex()}"

    print(cmd + "\n")

    p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    for _ in range(4):
        p.stdout.readline()

    for c in iter(lambda: p.stdout.read(1).decode(), ""):
        sys.stdout.write(c)
        if c == ")":
            sys.stdout.flush()
        elif c == "\n":
            break

    p.stdout.readline()
    p.stdout.readline()

    keys = p.stdout.readline().decode().strip()
    return keys


def crack(zip_file: ZipFile, output: str = "out.zip", password: str = "password"):
    crackable = get_crackable(zip_file)
    if len(crackable) == 0:
        print("No auto-crackable files found :(")
        return

    for filename, cribs in crackable.items():
        print(f"[+] Found potentially crackable file '{filename}'")
        print("[+] Attempting key recovery, this might take a while...\n")
        keys = recover_keys(zip_file, filename, cribs)
        if keys is None:
            continue

        print(f"\n[+] Keys successfully recovered: {keys}")

        run_cmd(f"bkcrack -C {zip_file.filename} -k {keys} -U {output} {password}")
        print("[+] Wrote unlocked archive, extract with:")
        print(f"$ unzip -P {password} {output}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="BKWHACK: bkcrack automation tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "filename",
        metavar="zipfile",
        type=argparse.FileType("rb"),
        help="Encrypted ZIP file"
    )

    parser.add_argument(
        "-o", "--output",
        default="out.zip",
        help="Filename for unlocked ZIP file"
    )

    parser.add_argument(
        "-p", "--password",
        default="hunter2",
        help="New password for unlocked ZIP file"
    )

    return parser.parse_args()


def main():
    args = parse_args()
    zip_file = load(args.filename)
    crack(zip_file, args.output, args.password)


if __name__ == "__main__":
    main()
