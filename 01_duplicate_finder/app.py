"""Duplicate File Finder and Folder Organizer — DAA Project 1."""
import csv
import hashlib
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import Store, form, heading, note, table, run

store = Store(Path(__file__).with_name("data.json"), {
    "plan": [], "created": [], "last_scan": "", "duplicate_rows": [],
    "summary": {"files": 0, "groups": 0, "waste": 0}, "filters": {}
})


def fingerprint(path):
    """Return a SHA-256 fingerprint, reading large files in chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan(folder, extension="All file types", min_size=0):
    """Scan regular files, group by size and SHA-256, then confirm byte equality."""
    root = Path(folder).expanduser().resolve()
    if not root.is_dir():
        raise ValueError("Enter an existing folder path.")
    if min_size < 0:
        raise ValueError("Minimum size cannot be negative.")
    groups = {}
    scanned = 0
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        try:
            relative = path.relative_to(root)
        except ValueError:
            continue
        if "_organized" in relative.parts:
            continue
        if extension != "All file types" and path.suffix.lower() != extension.lower():
            continue
        size = path.stat().st_size
        if size < min_size:
            continue
        scanned += 1
        key = (size, fingerprint(path))
        groups.setdefault(key, []).append(path)

    duplicates = []
    rows = []
    wasted = 0
    group_number = 0
    for (size, _digest), paths in groups.items():
        # A SHA-256 collision is extraordinarily unlikely; byte comparison confirms equality.
        equal_groups = []
        for path in paths:
            for group in equal_groups:
                if path.read_bytes() == group[0].read_bytes():
                    group.append(path)
                    break
            else:
                equal_groups.append([path])
        for equal in equal_groups:
            if len(equal) > 1:
                group_number += 1
                waste = size * (len(equal) - 1)
                wasted += waste
                duplicates.append({"group": group_number, "size": size, "paths": [str(p) for p in equal]})
                for path in equal:
                    rows.append([group_number, path.name, str(path), size, path.suffix.lower() or "(none)"])
    return root, scanned, duplicates, rows, wasted


def build_plan(root, files):
    plan = []
    for index, source in enumerate(files, 1):
        source_path = Path(source)
        category = source_path.suffix.lower().lstrip(".") or "no_extension"
        target = root / "_organized" / category / f"{index}_{source_path.name}"
        plan.append([str(source_path), str(target)])
    return plan


def view():
    out = note("Start with a practice folder. Scan only examines files; copying is a separate action. Original files are never deleted.")
    out += heading("1. Scan and filter")
    out += form("scan", [
        ("folder", "Full path to practice folder", "text", store.data.get("last_scan", "")),
        ("extension", "File type filter", "select", ["All file types", ".txt", ".pdf", ".jpg", ".jpeg", ".png", ".csv", ".docx", ".py"]),
        ("min_size", "Minimum file size in bytes (0 means no minimum)", "number", "0")
    ], "Scan and preview")
    summary = store.data.get("summary", {})
    out += heading("Latest scan summary")
    out += table(["Files scanned", "Duplicate groups", "Estimated redundant storage (bytes)"],
                 [[summary.get("files", 0), summary.get("groups", 0), summary.get("waste", 0)]])
    out += heading("Duplicate findings")
    out += table(["Group", "Name", "Full path", "Bytes", "Type"], store.data.get("duplicate_rows", []))
    out += form("export", [], "Export findings to CSV")
    out += heading("2. Preview organized copies")
    out += table(["Original file", "Proposed destination"], store.data.get("plan", []))
    out += form("copy", [], "Create organized copies")
    out += form("undo", [], "Undo last copy operation")
    out += note("Safety rule: if an organized copy has been edited after creation, Undo refuses to remove it.")
    return out


def handle(data):
    action = data.get("action")
    if action == "scan":
        if store.data.get("created"):
            raise ValueError("Undo the previous copy operation before scanning again.")
        try:
            minimum = int(data.get("min_size", "0"))
        except ValueError:
            raise ValueError("Minimum size must be a whole number of bytes.")
        extension = data.get("extension", "All file types")
        allowed = ["All file types", ".txt", ".pdf", ".jpg", ".jpeg", ".png", ".csv", ".docx", ".py"]
        if extension not in allowed:
            raise ValueError("Choose a valid file-type filter.")
        root, scanned, duplicates, rows, waste = scan(data.get("folder", ""), extension, minimum)
        all_files = []
        for path in sorted(root.rglob("*")):
            if path.is_symlink() or not path.is_file() or "_organized" in path.relative_to(root).parts:
                continue
            if extension != "All file types" and path.suffix.lower() != extension.lower():
                continue
            if path.stat().st_size < minimum:
                continue
            all_files.append(str(path))
        store.data.update({
            "plan": build_plan(root, all_files), "created": [], "last_scan": str(root),
            "duplicate_rows": rows,
            "summary": {"files": scanned, "groups": len(duplicates), "waste": waste},
            "filters": {"extension": extension, "min_size": minimum}
        })
        store.save()
        return note(f"Scan complete: {scanned} eligible files checked; {len(duplicates)} duplicate groups found.")
    if action == "copy":
        plan = store.data.get("plan", [])
        if not plan or store.data.get("created"):
            raise ValueError("Run a new scan first, or undo the previous copy operation.")
        for source, target in plan:
            if not Path(source).is_file() or Path(target).exists():
                raise ValueError("A source is missing or a destination already exists. Scan again.")
        store.data["created"] = []
        store.save()
        try:
            for source, target in plan:
                Path(target).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                store.data["created"].append({"path": target, "hash": fingerprint(Path(target))})
                store.save()
        except Exception:
            # Keep a truthful record of anything created so far; user can use Undo.
            store.save()
            raise
        return note(f"Created {len(plan)} organized copies. The original files remain unchanged.")
    if action == "undo":
        created = store.data.get("created", [])
        if not created:
            raise ValueError("There is no recorded copy operation to undo.")
        for entry in created:
            target = Path(entry["path"])
            if target.exists() and fingerprint(target) != entry["hash"]:
                raise ValueError("A copied file was edited. Move it elsewhere before undoing.")
        for entry in created:
            Path(entry["path"]).unlink(missing_ok=True)
        store.data["created"] = []
        store.data["plan"] = []
        store.save()
        return note("The tracked copies were removed. Original files remain unchanged; empty folders may remain.")
    if action == "export":
        rows = store.data.get("duplicate_rows", [])
        if not rows:
            raise ValueError("Scan a folder with duplicate findings before exporting.")
        output = Path(__file__).with_name("duplicate_findings.csv")
        with output.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["group", "name", "full_path", "size_bytes", "file_type"])
            writer.writerows(rows)
        return note(f"Exported {len(rows)} finding rows to {output.name} beside app.py.")
    raise ValueError("Unknown action.")


if __name__ == "__main__":
    run("Duplicate File Finder and Folder Organizer", view, handle)
