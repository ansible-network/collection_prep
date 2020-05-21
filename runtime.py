"""
Get ready for 1.0.0
"""
import datetime
import logging
import platform
import os
import re
import sys
import subprocess
import glob
import yaml

from argparse import ArgumentParser
from collections import OrderedDict
from redbaron import RedBaron
import ruamel.yaml
from update import load_py_as_ast, find_assigment_in_ast


logging.basicConfig(format="%(levelname)-10s%(message)s", level=logging.INFO)

COLLECTION_MIN_ANSIBLE_VERSION = ">=2.9"
DEPRECATION_CYCLE_IN_DAYS = 365


def get_warning_msg(plugin_name):
    depcrecation_date = datetime.date.today() + datetime.timedelta(
        days=DEPRECATION_CYCLE_IN_DAYS
    )
    depcrecation_msg = f"{plugin_name} has been deprecated and will be removed in a release after {depcrecation_date}. See the plugin documentation for more details"
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

        module_prefix = module_name.split("_")[0]
        short_name = module_name.split("_", 1)[1]

        # handle action plugin redirection
        if (
            os.path.exists(os.path.join(action_path, f"{module_prefix}.py"))
            and module_prefix == collection_name
        ):
            fq_action_name = f"{collection}.{module_prefix}"
            if not plugin_routing.get("action"):
                plugin_routing["action"] = {}
            plugin_routing["action"].update({module_name: {"redirect": fq_action_name}})
            plugin_routing["action"].update({short_name: {"redirect": fq_action_name}})

        # handle module short name redirection
        if module_prefix == collection_name:
            fq_module_name = f"{collection}.{module_name}"
            if not plugin_routing.get("modules"):
                plugin_routing["modules"] = {}
            plugin_routing["modules"].update({short_name: {"redirect": fq_module_name}})

        # handle module (incl short name) deprecation
        if "deprecated" in doc_section:
            logging.info("Found to be deprecated")
            plugin_routing["modules"].update(
                {
                    module_name: {
                        "deprecation": {
                            "warning_text": get_warning_msg(
                                f"{collection}.{module_name}"
                            )
                        }
                    }
                }
            )
            plugin_routing["modules"][short_name].update(
                {
                    "deprecation": {
                        "warning_text": get_warning_msg(f"{collection}.{short_name}")
                    }
                }
            )

    return plugin_routing


def process(collection, path):
    rt_obj = {}
    rt_obj["requires_ansible"] = COLLECTION_MIN_ANSIBLE_VERSION
    plugin_routing = process_runtime_plugin_routing(collection, path)
    if plugin_routing:
        rt_obj["plugin_routing"] = process_runtime_plugin_routing(collection, path)

    meta_path = os.path.join(os.path.join(path, collection), "meta")

    if not os.path.exists(meta_path):
        os.makedirs(meta_path)

    runtime_path = os.path.join(meta_path, "runtime.yml")

    with open(runtime_path, "w") as fp:
        fp.write(yaml.dump(rt_obj))


def main():
    """
    The entry point
    """
    if not platform.python_version().startswith("3.8"):
        sys.exit("Python 3.8+ required")
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
