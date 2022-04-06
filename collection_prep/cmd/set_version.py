#!/usr/bin/env python

"""Update galaxy.yml version to PEP440-compliant string"""
from argparse import ArgumentParser
from pathlib import Path
import subprocess
import sys


def get_version(path: Path) -> str:
    """Get version for repository at path"""
    try:
        version = subprocess.check_output(
            ["git", "describe"], cwd=path, text=True
        )
    except subprocess.CalledProcessError as exc:
        print("git describe failed. Is this a git repository?")
        sys.exit(exc.returncode)

    version, c_hash = version.strip().rsplit("-", 1)
    version = f"{version}+{c_hash}"
    return version


def write_to_galaxy_yml(path: Path, version: str) -> bool:
    """Write version to galaxy.yml at path

    returns: true if file changed else false
    """
    galaxy_path = path / "galaxy.yml"
    version_string = f"version: {version}\n"

    with open(galaxy_path) as galaxy_file:
        galaxy_lines = galaxy_file.readlines()

    changed = False
    for i, line in enumerate(galaxy_lines):
        if line.startswith("version:") and line != version_string:
            galaxy_lines[i] = version_string
            changed = True

    if changed:
        with open(galaxy_path, "w") as galaxy_file:
            galaxy_file.writelines(galaxy_lines)

    return changed


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "-p", "--path", help="The path to the collection", required=True
    )
    args = parser.parse_args()
    path = Path(args.path).absolute()

    version = get_version(path)
    changed = write_to_galaxy_yml(path, version)
    if changed:
        print(f"Updated galaxy version to {version}")
        sys.exit(1)


if __name__ == "__main__":
    main()
