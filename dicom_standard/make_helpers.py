import argparse
from pathlib import Path
import shutil
import sys
from urllib.request import urlopen


STANDARD_PARTS = (
    "part03.html",
    "part04.html",
    "part06.html",
    "part10.html",
    "part15.html",
    "part16.html",
    "part17.html",
    "part18.html",
)
STANDARD_URL = "http://dicom.nema.org/medical/dicom/{version}/output/html/{part}"


def normalize_html(filepath):
    content = Path(filepath).read_bytes()
    content = content.replace(b"&nbps;", b" ").replace(b"\xe2\x80\x8b", b"")
    sys.stdout.buffer.write(content)


def update_standard(version):
    standard_dir = Path("standard")
    backup_dir = Path("old_standard")
    backup_dir.mkdir(exist_ok=True)

    for filepath in standard_dir.glob("*.html"):
        shutil.move(str(filepath), str(backup_dir / filepath.name))

    for part in STANDARD_PARTS:
        url = STANDARD_URL.format(version=version, part=part)
        with urlopen(url) as response, (standard_dir / part).open("wb") as output:
            shutil.copyfileobj(response, output)


def clean_generated():
    root = Path(".")
    for pattern in ("*.pyc", "*.pyo"):
        for filepath in root.rglob(pattern):
            filepath.unlink()

    cache_dirs = sorted(root.rglob("__pycache__"), key=lambda path: len(path.parts), reverse=True)
    for cache_dir in cache_dirs:
        shutil.rmtree(cache_dir)


def check_python():
    if sys.version_info < (3, 12):
        version = ".".join(str(part) for part in sys.version_info[:3])
        raise SystemExit("Need Python 3.12 or newer; found Python {}".format(version))


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    normalize_parser = subparsers.add_parser("normalize-html")
    normalize_parser.add_argument("filepath")

    update_parser = subparsers.add_parser("update-standard")
    update_parser.add_argument("version")

    subparsers.add_parser("clean-generated")
    subparsers.add_parser("check-python")
    args = parser.parse_args()

    if args.command == "normalize-html":
        normalize_html(args.filepath)
    elif args.command == "update-standard":
        update_standard(args.version)
    elif args.command == "clean-generated":
        clean_generated()
    elif args.command == "check-python":
        check_python()


if __name__ == "__main__":
    main()
