"""Get ready for 1.0.0."""
import logging
import os
import platform
import re
import subprocess
import sys

from argparse import ArgumentParser

import ruamel.yaml

from collection_prep.utils import find_assignment_in_ast
from collection_prep.utils import get_removed_at_date
from collection_prep.utils import load_py_as_ast


logging.basicConfig(format="%(levelname)-10s%(message)s", level=logging.INFO)

SUBDIRS = (
    "modules",
    "action",
    "become",
    "cliconf",
    "connection",
    "filter",
    "httpapi",
    "netconf",
    "terminal",
    "inventory",
)
SPECIALS = {"ospfv2": "OSPFv2", "interfaces": "Interfaces", "static": "Static"}


def remove_assignment_in_ast(name, ast_file):
    """Remove an assignment in an ast object.

    :param name: The name of the assignment to remove
    :param ast_file: The ast object
    """
    res = ast_file.find("assignment", target=lambda x: x.dumps() == name)
    if res:
        ast_file.remove(res)


def retrieve_plugin_name(plugin_type, body_part):
    """Retrieve the module name from a docstring.

    :param plugin_type: The plugin's type
    :param body_part: The docstring extracted from the ast body
    :return: The module name
    """
    if not body_part:
        logging.warning("Failed to find DOCUMENTATION assignment")
        return ""
    documentation = ruamel.yaml.load(body_part.value.to_python(), ruamel.yaml.RoundTripLoader)

    if plugin_type == "modules":
        plugin_type = "module"
    name = documentation[plugin_type]
    return name


def update_deprecation_notice(documentation):
    """Update deprecation notices to use removed_at_date instead of removed_in.

    :param documentation: The DOCUMENTATION section of the module
    """
    if "deprecated" in documentation:
        logging.info("Updating deprecation notice")
        documentation["deprecated"].update({"removed_at_date": get_removed_at_date()})
        documentation["deprecated"].pop("removed_in", None)


def update_documentation(body_part):
    """Update the documentation of the module.

    :param body_part: The DOCUMENTATION section of the module
    """
    if not body_part:
        logging.warning("Failed to find DOCUMENTATION assignment")
        return
    documentation = ruamel.yaml.load(body_part.value.to_python(), ruamel.yaml.RoundTripLoader)

    # update deprecation to removed_at_date
    update_deprecation_notice(documentation)

    # remove version added
    documentation.pop("version_added", None)
    desc_idx = [idx for idx, key in enumerate(documentation.keys()) if key == "description"]
    # insert version_added after the description
    documentation.insert(desc_idx[0] + 1, key="version_added", value="1.0.0")
    repl = ruamel.yaml.dump(documentation, None, ruamel.yaml.RoundTripDumper)

    # remove version added from anywhere else in the docstring if preceded by 1+ spaces
    example_lines = repl.splitlines()
    regex = re.compile(r"^\s+version_added\:\s.*$")
    example_lines = [line for line in example_lines if not re.match(regex, line)]
    body_part.value.replace('"""\n' + "\n".join(example_lines) + '\n"""')


def update_examples(body_part, module_name, collection):
    """Update the example.

    :param body_part: The EXAMPLE section of the module
    :param module_name: The name of the module
    :param collection: The name of the collection
    """
    if not body_part:
        logging.warning("Failed to find EXAMPLES assignment")
        return
    full_module_name = f"{collection}.{module_name}"
    example = ruamel.yaml.load(body_part.value.to_python(), ruamel.yaml.RoundTripLoader)
    # check each task and update to fqcn
    for idx, task in enumerate(example):
        example[idx] = ruamel.yaml.comments.CommentedMap(
            [(full_module_name, v) if k == module_name else (k, v) for k, v in task.items()]
        )

    repl = ruamel.yaml.dump(example, None, ruamel.yaml.RoundTripDumper)

    # look in yaml comments for the module name as well and replace
    example_lines = repl.splitlines()
    for idx, line in enumerate(example_lines):
        if (
            line.startswith("#")
            and module_name in line
            and module_name
            and full_module_name not in line
        ):
            example_lines[idx] = line.replace(module_name, full_module_name)
    body_part.value.replace('"""\n' + "\n".join(example_lines) + '\n"""')


def update_short_description(return_, documentation, module_name):
    """Update the short description of the module.

    :param return_: The RETURN section of the module
    :param documentation: The DOCUMENTATION section of the module
    :param module_name: The module name
    """
    if not return_:
        logging.warning("Failed to find RETURN assignment")
        return
    ret_section = ruamel.yaml.load(return_.value.to_python(), ruamel.yaml.RoundTripLoader)
    if not documentation:
        logging.warning("Failed to find DOCUMENTATION assignment")
        return
    doc_section = ruamel.yaml.load(documentation.value.to_python(), ruamel.yaml.RoundTripLoader)
    short_description = doc_section["short_description"]

    rm_rets = ["after", "before", "commands"]
    if ret_section:
        match = [x for x in rm_rets if x in list(ret_section.keys())]
        if len(match) == len(rm_rets):
            logging.info("Found a resource module")
            parts = module_name.split("_")
            # things like 'interfaces'
            resource = parts[1].lower()
            resource = SPECIALS.get(resource, resource.upper())
            if resource.lower()[-1].endswith("s"):
                chars = list(resource)
                chars[-1] = chars[-1].lower()
                resource = "".join(chars)
            if len(parts) > 2 and parts[2] != "global":
                resource += f" {parts[2]}"
            short_description = f"{resource} resource module"
    # Check for deprecated modules
    if "deprecated" in doc_section and not short_description.startswith("(deprecated,"):
        logging.info("Found to be deprecated")
        short_description = short_description.replace("(deprecated) ", "")
        short_description = (
            f"(deprecated, removed after {get_removed_at_date()}) {short_description}"
        )
    # Change short if necessary
    if short_description != doc_section["short_description"]:
        logging.info("Setting short description to '%s'", short_description)
        doc_section["short_description"] = short_description
        repl = ruamel.yaml.dump(doc_section, None, ruamel.yaml.RoundTripDumper)
        documentation.value.replace('"""\n' + repl + '\n"""')


def black(filename):
    """Run black against the file.

    :param filename: The full path to the file
    """
    logging.info("Running black against %s", filename)
    subprocess.check_output(["black", "-q", filename])


def process(collection, path):
    """Process the files in each subdirectory.

    :param collection: The name of the collection
    :param path: The collections path
    """
    for subdir in SUBDIRS:
        dirpath = f"{path}{collection}/plugins/{subdir}"
        try:
            plugin_files = os.listdir(dirpath)
        except FileNotFoundError:
            # Looks like we don't have any of that type of plugin here
            continue

        for filename in plugin_files:
            if filename.endswith(".py"):
                filename = f"{dirpath}/{filename}"
                logging.info("-------------------Processing %s", filename)
                ast_obj = load_py_as_ast(filename)

                # Get the module name from the docstring
                module_name = retrieve_plugin_name(
                    subdir,
                    find_assignment_in_ast(ast_file=ast_obj, name="DOCUMENTATION"),
                )
                if not module_name:
                    logging.warning("Skipped %s: No module name found", filename)
                    continue

                # Remove the metadata
                remove_assignment_in_ast(ast_file=ast_obj, name="ANSIBLE_METADATA")
                logging.info("Removed metadata in %s", filename)

                # Update the documentation
                update_documentation(
                    body_part=find_assignment_in_ast(ast_file=ast_obj, name="DOCUMENTATION")
                )
                logging.info("Updated documentation in %s", filename)

                if subdir == "modules":
                    # Update the short description
                    update_short_description(
                        return_=find_assignment_in_ast(ast_file=ast_obj, name="RETURN"),
                        documentation=find_assignment_in_ast(
                            ast_file=ast_obj, name="DOCUMENTATION"
                        ),
                        module_name=module_name,
                    )

                    # Update the examples
                    update_examples(
                        body_part=find_assignment_in_ast(ast_file=ast_obj, name="EXAMPLES"),
                        module_name=module_name,
                        collection=collection,
                    )
                    logging.info("Updated examples in %s", filename)

                # Write out the file and black
                file_contents = ast_obj.dumps()
                with open(filename, "w", encoding="utf8") as file_obj:
                    file_obj.write(file_contents)
                    logging.info("Wrote %s", filename)
                black(filename)


def main():
    """Run the script."""
    if not platform.python_version().startswith("3.8"):
        sys.exit("Python 3.8+ required")
    parser = ArgumentParser()
    parser.add_argument("-c", "--collection", help="The name of the collection", required=True)
    parser.add_argument("-p", "--path", help="The path to the collection", required=True)
    args = parser.parse_args()
    process(collection=args.collection, path=args.path)


if __name__ == "__main__":
    main()
