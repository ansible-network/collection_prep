"""Utilities for jinja2."""


from ansible.module_utils._text import to_text
from ansible.module_utils.six import string_types
from antsibull_docs_parser import dom
from antsibull_docs_parser.html import to_html_plain
from antsibull_docs_parser.parser import Context
from antsibull_docs_parser.parser import parse
from antsibull_docs_parser.rst import to_rst_plain
from jinja2.runtime import Undefined
from jinja2.utils import pass_context


NS_MAP = {}


def to_kludge_ns(key, value):
    """Save a value for later use.

    :param key: The key to store under
    :param value: The value to store
    :return: An empty string to not confuse jinja
    """
    NS_MAP[key] = value
    return ""


def from_kludge_ns(key):
    """Recall a value stored with to_kludge_ns.

    :param key: The key to look for
    :return: The value stored under that key
    """
    return NS_MAP[key]


def get_context(j2_context):
    """Create parser context from Jinja2 context.

    :param j2_context: The Jinja2 context
    :return: A parser context
    """
    params = {}
    plugin_fqcn = j2_context.get("module")
    plugin_type = j2_context.get("plugin_type")
    if plugin_fqcn is not None and plugin_type is not None:
        params["current_plugin"] = dom.PluginIdentifier(fqcn=plugin_fqcn, type=plugin_type)
    return Context(**params)


@pass_context
def html_ify(j2_context, text):
    """Convert symbols like I(this is in italics) to valid HTML.

    :param j2_context: The Jinja2 context
    :param text: The text to transform
    :return: An HTML string of the formatted text
    """
    if not isinstance(text, string_types):
        text = to_text(text)

    paragraphs = parse(text, get_context(j2_context))
    text = to_html_plain(paragraphs, par_start="", par_end="")

    return text.strip()


@pass_context
def rst_ify(j2_context, text):
    """Convert symbols like I(this is in italics) to valid restructured text.

    :param j2_context: The Jinja2 context
    :param text: The text to transform
    :return: An RST string of the formatted text
    """
    if not isinstance(text, string_types):
        text = to_text(text)

    paragraphs = parse(text, get_context(j2_context))
    text = to_rst_plain(paragraphs)

    return text


def documented_type(text):
    """Convert any python type to a type for documentation.

    :param text: A python type
    :return: The associated documentation form of that type
    """
    if isinstance(text, Undefined):
        return "-"
    if text == "str":
        return "string"
    if text == "bool":
        return "boolean"
    if text == "int":
        return "integer"
    if text == "dict":
        return "dictionary"
    return text
