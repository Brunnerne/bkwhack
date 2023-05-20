# bkwhack

Automated helper tool for `bkcrack`.

`bkwhack` searches a ZIP archive for any ZipCrypto encrypted, non-compressed files and checks for auto-crackable file types.

Supported file types are attempted cracked with `bkcrack` using known bytes (mostly header/footer) in order of fastest crackable.

## Usage

Clone the repo and simply run

```
$ python3 bkwhack.py <zipfile>
```

on the ZIP archive you want to crack with `bkcrack` and let `bkwhack` handle the rest.

Full usage:

```
usage: bkwhack.py [-h] [-l] [-o OUTPUT] [-p PASSWORD] [zipfile]

BKWHACK: bkcrack automation tool

positional arguments:
  zipfile               Encrypted ZIP file

options:
  -h, --help            show this help message and exit
  -l, --list            List supported file types
  -o OUTPUT, --output OUTPUT
                        Filename for unlocked ZIP file (default: out.zip)
  -p PASSWORD, --password PASSWORD
                        New password for unlocked ZIP file (default: hunter2)
```

## Development

Feel free to post an issue or pull request in case of bugs or new features / file types.

To add support for a new file format, please create a new entry in `fileformats.py` with the file extension and any known bytes. Offsets can be negative to count form the end of the file in case of footers.

Please make sure to fill in at least

- one contiguous sequence of length 8+
- 12 total bytes across all sequences

Please make sure the known bytes are *certain* by downloading many sample files and ensuring they *all* have these bytes at the provided offsets. The offsets can be negative to count from the end of the file in case of footers.

For any new file types added, please add a *small* sample file in [/examples/files](/examples/files), then zip it with

```
zip -e -P password -Z Store <ext> <filename>
```

and place the ZIP archive in [/examples](/examples). Make sure to run `bkwhack` on this file as a sanity check before submitting the pull request.
