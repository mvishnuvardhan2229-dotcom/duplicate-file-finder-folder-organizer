# Duplicate File Finder and Folder Organizer

A small local browser application that detects duplicate file contents, estimates redundant storage, and helps create an organized copy of a folder without moving or deleting original files.

## Features

- Recursive scanning of a selected folder and its subfolders
- Chunked SHA-256 fingerprints and byte-level comparison for duplicate verification
- Duplicate-group summary and redundant-storage estimate
- Optional file-type and minimum-size filters
- Preview of extension-based organization before any copy is made
- Numbered destination filenames to avoid name collisions
- Copy operation that preserves original files
- Guarded undo that refuses to remove modified tracked copies
- CSV export of duplicate findings
- Local browser interface using Python's built-in `http.server`

## Requirements

- Python 3.10 or newer
- A modern browser
- No third-party Python packages
- No account, API key, paid tool, or internet connection required for local use

## Clone the repository

Replace `YOUR-USERNAME/YOUR-REPOSITORY` with the actual GitHub repository path:

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY
```

If you downloaded a ZIP instead, extract it and open a terminal in the extracted project root—the folder containing `common.py`.

## Run on Ubuntu or other Linux distributions

```bash
python3 --version
python3 -m py_compile common.py 01_duplicate_finder/app.py
python3 -m unittest discover -s tests -v
python3 01_duplicate_finder/app.py
```

Open the local address printed in the terminal, normally `http://127.0.0.1:8000`. Keep the terminal running while you use the app. Press `Ctrl+C` to stop it.

If port 8000 is already in use:

```bash
PORT=8001 python3 01_duplicate_finder/app.py
```

Then open `http://127.0.0.1:8001`.

## Run on Windows

Install Python 3.10 or newer from [python.org](https://www.python.org/downloads/) and ensure Python is available from Command Prompt or PowerShell. Extract or clone the repository, then change directory into the project root.

```powershell
py --version
py -m py_compile common.py 01_duplicate_finder/app.py
py -m unittest discover -s tests -v
py 01_duplicate_finder/app.py
```

If the `py` launcher is unavailable, try `python` in place of `py`. Open the local URL printed by the program. Stop the server with `Ctrl+C`.

## Run on macOS

Install Python 3.10 or newer, then open Terminal in the project root:

```bash
python3 --version
python3 -m py_compile common.py 01_duplicate_finder/app.py
python3 -m unittest discover -s tests -v
python3 01_duplicate_finder/app.py
```

Open the printed local URL in Safari, Chrome, Firefox, or another modern browser. Stop the server with `Ctrl+C`.

## Try the included sample data

1. Start the app using the instructions above.
2. Get the full sample-folder path. On Linux/macOS, from the project root run:

   ```bash
   realpath samples/practice_files
   ```

   On Windows, use the absolute path shown by File Explorer or PowerShell.
3. Paste the full path into the application.
4. Leave the file-type filter at **All file types** and set minimum size to `0`.
5. Scan and review the duplicate group, estimated redundant storage, and planned destination paths.
6. Create organized copies only after reviewing the preview.
7. Confirm that original files remain present.
8. Use Undo to remove unchanged copies created by the latest tracked operation.

Use a disposable practice folder first. Do not experiment on important personal files.

## How it works

### 1. Scanning and filtering
The app walks the chosen directory recursively. Symbolic links and its own `_organized` output are excluded. Optional filters can limit the scan by extension or minimum file size.

### 2. Fingerprinting
Each file is read in chunks of 65,536 bytes and passed through SHA-256. This produces a fingerprint without reading the entire file into memory at once.

### 3. Duplicate verification
Files are grouped by size and fingerprint. A byte-level comparison checks the candidate contents before a duplicate group is reported.

### 4. Redundant storage
For a group of identical files, the estimate is:

`redundant bytes = file size × (number of files − 1)`

For example, three identical five-byte files occupy 15 bytes in total; keeping one copy would leave 10 bytes of repeated content.

### 5. Safe organization
The app previews destinations under `_organized/<extension>/`. It prefixes copied filenames with a sequence number so two files with the same name from different subfolders do not overwrite each other. Copying is a separate action, and original files are retained.

### 6. Undo safety
The app saves the path and fingerprint of each copy. Before undoing, it checks that the tracked copies have not changed. If a tracked copy is edited or missing, undo is refused rather than deleting potentially valuable changes.

### 7. CSV export
Duplicate findings can be exported to a CSV file for review in spreadsheet software.

## Project structure

```text
.
├── common.py
├── 01_duplicate_finder/
│   ├── app.py
│   ├── data.json                 # created automatically
│   └── duplicate_findings.csv    # created after CSV export
├── samples/
│   └── practice_files/
├── tests/
├── docs/
└── README.md
```

## Tests

Run the automated suite with:

```bash
python3 -m unittest discover -s tests -v
```

Use `py` instead of `python3` on Windows if that is how Python is installed. Keep a record of the actual test output when making changes.

## What I learned

- How to traverse nested directories safely with `pathlib`
- How chunked file reading avoids loading large files into memory
- How cryptographic hashes can identify likely duplicate content
- Why hashes are useful for grouping candidates and why final byte comparison is still valuable
- How to estimate redundant storage using a simple formula
- How to separate a preview from an operation that changes files
- How to copy files while preserving metadata with `shutil.copy2`
- How to make undo operations safer by checking saved fingerprints
- How to build a small local browser interface with Python's standard-library `http.server`
- How to write and inspect CSV exports and automated tests

## Limitations and safety notes

- Intended for local, single-user use and small-to-medium practice folders.
- Scanning may take time because file contents must be read.
- A file could change between scan and copy; review the plan and use test data.
- Undo applies to tracked copies from the latest operation and intentionally refuses if a tracked copy is modified.
- Empty category folders may remain after undo.
- The app binds to `127.0.0.1`; it is not designed as a public internet service.
- The app has no database, user accounts, cloud storage, or multi-user coordination.

## Acknowledgements

This project was developed through hands-on experimentation, reference documentation, and AI-assisted learning. Review the source before adapting it, and make sure you understand the scanning, verification, copy, and undo logic.

## License

Add a license file if you intend to publish or redistribute this project. Do not imply a license has been selected until you add one.
