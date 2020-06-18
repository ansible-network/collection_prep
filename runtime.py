"""
Get ready for 1.0.0
"""
import logging
import platform
import os
import sys
import glob

from argparse import ArgumentParser

import ruamel.yaml
from utils import get_removed_at_date, load_py_as_ast, find_assigment_in_ast

logging.basicConfig(format="%(levelname)-10s%(message)s", level=logging.INFO)

COLLECTION_MIN_ANSIBLE_VERSION = ">=2.9.10"
COLLECTION_MAX_ANSIBLE_VERSION = "<2.11"
DEPRECATION_CYCLE_IN_YEAR = 2
REMOVAL_FREQUENCY_IN_MONTHS = 3
REMOVAL_DAY_OF_MONTH = "01"


def get_warning_msg(plugin_name=None):
    depcrecation_msg = "See the plugin documentation for more details"
    return depcrecation_msg


def process_runtime_plugin_routing(collection, path):
    plugin_routing = {}
    plugins_path = f"{path}/{collection}/plugins"
    modules_path = f"{plugins_path}/modules"
    action_path = f"{plugins_path}/action"

    collection = collection.replace("/", ".")
    collection_name = collection.split(".")[-1]
    if not collection_name:
        logging.error(f"failed to get collection name from {collection}")

    for fullpath in sorted(glob.glob(f"{modules_path}/*.py")):

        filename = fullpath.split("/")[-1]
        if not filename.endswith(".py") or filename.endswith("__init__.py"):
            continue

        module_name = filename.split(".")[0]

        logging.info(
            f"-------------------Processing runtime.yml for module {module_name}"
        )

        ast_obj = load_py_as_ast(fullpath)
        documentation = find_assigment_in_ast(ast_file=ast_obj, name="DOCUMENTATION")
        doc_section = ruamel.yaml.load(
            documentation.value.to_python(), ruamel.yaml.RoundTripLoader
        )

        try:
            module_prefix = module_name.split("_")[0]
        except IndexError:
            module_prefix = module_name

        short_name = module_name.split("_", 1)[-1]

        # handle action plugin redirection
        # if module name and action name is same skip the redirection as Ansible
        # by design will invoke action plugin first.
        if not os.path.exists(os.path.join(action_path, f"{module_name}.py")):
            if (
                os.path.exists(os.path.join(action_path, f"{module_prefix}.py"))
                and module_prefix == collection_name
            ):
                fq_action_name = f"{collection}.{module_prefix}"
                if not plugin_routing.get("action"):
                    plugin_routing["action"] = {}
                plugin_routing["action"].update(
                    {module_name: {"redirect": fq_action_name}}
                )
                plugin_routing["action"].update(
                    {short_name: {"redirect": fq_action_name}}
                )

        # handle module short name redirection.
        # Add short redirection if module prefix and collection name is same
        # for example arista.eos.eos_acls will support redirection for arista.eos.acls
        # as the prefix of module name (eos) is same as the collection name
        if module_prefix == collection_name:
            fq_module_name = f"{collection}.{module_name}"
            if not plugin_routing.get("modules"):
                plugin_routing["modules"] = {}
            plugin_routing["modules"].update({short_name: {"redirect": fq_module_name}})

        # handle module deprecation notice
        if "deprecated" in doc_section:
            logging.info("Found to be deprecated")
            if not plugin_routing.get("modules"):
                plugin_routing["modules"] = {}
            plugin_routing["modules"].update(
                {
                    module_name: {
                        "deprecation": {
                            "removal_date": get_removed_at_date(),
                            "warning_text": get_warning_msg(
                                f"{collection}.{module_name}"
                            ),
                        }
                    }
                }
            )
            if module_prefix == collection_name:
                if not plugin_routing["modules"].get(short_name):
                    plugin_routing["modules"][short_name] = {}

                plugin_routing["modules"][short_name].update(
                    {
                        "deprecation": {
                            "removal_date": get_removed_at_date(),
                            "warning_text": get_warning_msg(
                                f"{collection}.{short_name}"
                            ),
                        }
                    }
                )

    return plugin_routing


def process(collection, path):
    rt_obj = {}
    collection_path = os.path.join(path, collection)
    if not os.path.exists(collection_path):
        logging.error(f"{collection_path} does not exit")

    supported_ansible_versions = COLLECTION_MIN_ANSIBLE_VERSION
    if COLLECTION_MAX_ANSIBLE_VERSION:
        supported_ansible_versions += ',' + COLLECTION_MAX_ANSIBLE_VERSION
    rt_obj["requires_ansible"] = supported_ansible_versions
    plugin_routing = process_runtime_plugin_routing(collection, path)
    if plugin_routing:
        rt_obj["plugin_routing"] = plugin_routing

    # create meta/runtime.yml file
    meta_path = os.path.join(collection_path, "meta")
    if not os.path.exists(meta_path):
        os.makedirs(meta_path)

    runtime_path = os.path.join(meta_path, "runtime.yml")

    yaml = ruamel.yaml.YAML()
    yaml.explicit_start = True

    with open(runtime_path, "w") as fp:
        yaml.dump(rt_obj, fp)


def main():
    """
    The entry point
    """
    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--collection", help="The name of the collection", required=True
    )
    parser.add_argument(
        "-p", "--path", help="The path to the collection", required=True
    )
    args = parser.parse_args()
    process(collection=args.collection, path=args.path)


if __name__ == "__main__":
    main()
