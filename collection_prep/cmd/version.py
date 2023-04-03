import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

import ruamel.yaml

yaml = ruamel.yaml.YAML()
# Preserve document layout
yaml.block_seq_indent = 2
yaml.explicit_start = True
yaml.preserve_quotes = True

try:
    import argcomplete
except ImportError:
    argcomplete = None


logging.basicConfig(format="%(levelname)-10s%(message)s", level=logging.INFO)


# What level of version to apply for a given change type
RULES = {
    "major": [
        "major_changes",
        "breaking_changes",
        "removed_features",
    ],
    "minor": [
        "minor_changes",
        "deprecated_features",
    ],
    "patch": [
        "bugfixes",
        "security_fixes",
        "trivial",
    ],
}


def get_last_version(path) -> str:
    changelog_path = path / "changelogs" / "changelog.yaml"
    if not changelog_path.exists():
        # Collection has not been released?
        return "0.0.0"
    changelog = yaml.load(changelog_path)
    return max(changelog["releases"].keys())


def update_version(path: Path, version: str) -> str:
    version_parts = [int(v) for v in version.split(".")]
    fragment_path = path / "changelogs" / "fragments"

    types = {key: False for key in RULES}
    if fragment_path.exists() and fragment_path.is_dir():
        for file in fragment_path.iterdir():
            fragment = yaml.load(file)
            if fragment:
                for level, headings in RULES.items():
                    for heading in headings:
                        if heading in fragment:
                            types[level] = True

    # Bump version accordingly
    if types["major"]:
        version_parts = version_parts[0] + 1, 0, 0
    elif types["minor"]:
        version_parts[1:] = version_parts[1] + 1, 0
    elif types["patch"]:
        version_parts[2] += 1
    new_version = ".".join(str(v) for v in version_parts)

    if new_version != version:
        new_version += "-dev"

    return new_version


def update_galaxy(path: Path, new_version: str) -> bool:
    galaxy_path = path / "galaxy.yml"
    if galaxy_path.exists():
        galaxy = yaml.load(galaxy_path)
    else:
        logging.error("Unable to find galaxy.yml in %s", path)
        sys.exit(2)

    logging.info("Current version in galaxy.yml is %s", galaxy["version"])
    if galaxy["version"] != new_version:
        logging.info("Updating version string in galaxy.yml")
        galaxy["version"] = new_version
        yaml.dump(galaxy, galaxy_path)
        return True
    return False


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "-p",
        "--path",
        help="The path to the collection (ie ./ansible.netcommon",
        required=True,
    )

    if argcomplete:
        argcomplete.autocomplete(parser)

    args = parser.parse_args()
    path = Path(args.path).absolute()

    version = get_last_version(path)
    logging.info("Detected collection version is %s", version)

    new_version = update_version(path, version)
    logging.info("Updated collection version is %s", new_version)

    changed = update_galaxy(path, new_version)
    sys.exit(int(changed))


if __name__ == "__main__":
    main()
