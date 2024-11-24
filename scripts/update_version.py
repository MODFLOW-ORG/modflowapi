import argparse
import textwrap
from datetime import datetime
from os.path import basename
from pathlib import Path

from filelock import FileLock
from packaging.version import Version

_project_name = "modflowapi"
_project_root_path = Path(__file__).parent.parent
_version_txt_path = _project_root_path / "version.txt"
_version_py_path = _project_root_path / "modflowapi" / "version.py"
_citation_cff_path = _project_root_path / "CITATION.cff"

_initial_version = Version("0.0.1")
_current_version = Version(_version_txt_path.read_text().strip())


def log_update(path, version: Version):
    print(f"Updated {path} with version {version}")


def update_version_txt(version: Version):
    with open(_version_txt_path, "w") as f:
        f.write(str(version))
    log_update(_version_txt_path, version)


def update_version_py(timestamp: datetime, version: Version):
    with open(_version_py_path, "w") as f:
        f.write(
            f"# {_project_name} version file automatically "
            f"created using...{basename(__file__)}\n"
        )
        f.write(f"# created on...{timestamp.strftime('%B %d, %Y %H:%M:%S')}\n")
        f.write(f'__version__ = "{version}"\n')
    log_update(_version_py_path, version)


def update_citation_cff(version: Version):
    lines = open(_citation_cff_path, "r").readlines()
    with open(_citation_cff_path, "w") as f:
        for line in lines:
            if line.startswith("version:"):
                line = f"version: {version}\n"
            f.write(line)
    log_update(_citation_cff_path, version)


def update_version(timestamp: datetime = datetime.now(), version: Version = None):
    lock_path = Path(_version_py_path.name + ".lock")
    try:
        lock = FileLock(lock_path)
        previous = Version(_version_txt_path.read_text().strip())
        version = (
            version
            if version
            else Version(previous.major, previous.minor, previous.patch)
        )

        with lock:
            update_version_txt(version)
            update_version_py(timestamp, version)
            update_citation_cff(version)
    finally:
        try:
            lock_path.unlink()
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=f"Update {_project_name} version",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Update version information in version.txt in the project root,
            as well as several other files in the repository. If --version
            is not provided, the version number will not be changed. A file
            lock is held to synchronize file access. The version tag must be
            standard '<major>.<minor>.<patch>' format for semantic versioning.
            """
        ),
    )
    parser.add_argument(
        "-v", "--version", required=False, help="Specify the release version"
    )
    parser.add_argument(
        "-g",
        "--get",
        required=False,
        action="store_true",
        help="Get the current version number, no updates (defaults false)",
    )
    args = parser.parse_args()

    if args.get:
        print(_current_version)
    else:
        update_version(
            timestamp=datetime.now(),
            version=(Version(args.version) if args.version else _current_version),
        )
