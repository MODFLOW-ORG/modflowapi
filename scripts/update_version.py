import argparse
import subprocess
import textwrap
from datetime import datetime
from os.path import basename
from pathlib import Path

from filelock import FileLock
from packaging.version import InvalidVersion, Version

_project_name = "modflowapi"
_project_root_path = Path(__file__).parent.parent
_version_txt_path = _project_root_path / "version.txt"
_version_py_path = _project_root_path / "modflowapi" / "version.py"
_citation_cff_path = _project_root_path / "CITATION.cff"

_initial_version = Version("0.0.1")
_current_version = Version(_version_txt_path.read_text().strip())


def log_update(path, version: Version):
    print(f"Updated {path} with version {version}")


def latest_release() -> Version:
    """Version of the most recent release tag, or the initial version if there is none."""
    try:
        tags = subprocess.run(
            ["git", "tag", "--list", "--sort=-v:refname"],
            cwd=_project_root_path,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.split()
    except (subprocess.CalledProcessError, FileNotFoundError):
        tags = []
    for tag in tags:
        try:
            return Version(tag)
        except InvalidVersion:
            continue
    return _initial_version


def bump_version(bump: str) -> Version:
    """Next release version, relative to the latest release tag.

    The 'dev' increment releases the current development version as-is,
    with any development segment (e.g. '.dev0') stripped.
    """
    if bump == "dev":
        return Version(_current_version.base_version)
    latest = latest_release()
    if bump == "major":
        return Version(f"{latest.major + 1}.0.0")
    elif bump == "minor":
        return Version(f"{latest.major}.{latest.minor + 1}.0")
    elif bump == "patch":
        return Version(f"{latest.major}.{latest.minor}.{latest.micro + 1}")
    raise ValueError(f"Unsupported version increment: {bump}")


def next_dev_version() -> Version:
    """Next development version, incrementing the minor version number."""
    version = Version(_current_version.base_version)
    return Version(f"{version.major}.{version.minor + 1}.0.dev0")


def update_version_txt(version: Version):
    with open(_version_txt_path, "w") as f:
        f.write(str(version))
    log_update(_version_txt_path, version)


def update_version_py(timestamp: datetime, version: Version):
    with open(_version_py_path, "w") as f:
        f.write(f"# {_project_name} version file automatically created using...{basename(__file__)}\n")
        f.write(f"# created on...{timestamp.strftime('%B %d, %Y %H:%M:%S')}\n")
        f.write(f'__version__ = "{version}"\n')
    log_update(_version_py_path, version)


def update_citation_cff(timestamp: datetime, version: Version):
    lines = open(_citation_cff_path, "r").readlines()
    with open(_citation_cff_path, "w") as f:
        for line in lines:
            if line.startswith("version:"):
                line = f"version: {version}\n"
            elif line.startswith("date-released:"):
                line = f"date-released: '{timestamp.strftime('%Y-%m-%d')}'\n"
            f.write(line)
    log_update(_citation_cff_path, version)


def update_version(timestamp: datetime = datetime.now(), version: Version = None):
    lock_path = Path(_version_py_path.name + ".lock")
    try:
        lock = FileLock(lock_path)
        version = version if version else _current_version

        with lock:
            update_version_txt(version)
            update_version_py(timestamp, version)
            update_citation_cff(timestamp, version)
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
            as well as several other files in the repository. If neither
            --version nor --bump nor --next-dev is provided, the version
            number will not be changed. A file lock is held to synchronize
            file access. The version tag must be standard
            '<major>.<minor>.<patch>' format for semantic versioning.
            """
        ),
    )
    parser.add_argument("-v", "--version", required=False, help="Specify the release version")
    parser.add_argument(
        "-b",
        "--bump",
        required=False,
        choices=["major", "minor", "patch", "dev"],
        help=(
            "Compute the release version by incrementing the latest release tag. "
            "'dev' releases the current development version as-is"
        ),
    )
    parser.add_argument(
        "-n",
        "--next-dev",
        required=False,
        action="store_true",
        help="Compute the next development version, incrementing the minor version number",
    )
    parser.add_argument(
        "-g",
        "--get",
        required=False,
        action="store_true",
        help="Print the version number, no updates (defaults false)",
    )
    args = parser.parse_args()

    if args.next_dev:
        version = next_dev_version()
    elif args.bump:
        version = bump_version(args.bump)
    elif args.version:
        version = Version(args.version)
    else:
        version = _current_version

    if args.get:
        print(version)
    else:
        update_version(timestamp=datetime.now(), version=version)
