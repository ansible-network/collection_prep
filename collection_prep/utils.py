"""Get ready for 1.0.0."""
import datetime

from redbaron import RedBaron


COLLECTION_MIN_ANSIBLE_VERSION = ">=2.9"
DEPRECATION_CYCLE_IN_YEAR = 2
REMOVAL_FREQUENCY_IN_MONTHS = 3
REMOVAL_DAY_OF_MONTH = "01"


def get_removed_at_date():
    """Generate expected date to remove deprecated content.

    :return: The date deprecated content will be removed after, in YYYY-MM-DD format
    """
    today = datetime.date.today()
    deprecation_year = today.year + DEPRECATION_CYCLE_IN_YEAR
    if today.month % REMOVAL_FREQUENCY_IN_MONTHS:
        deprecation_month = (today.month + REMOVAL_FREQUENCY_IN_MONTHS) - (
            today.month % REMOVAL_FREQUENCY_IN_MONTHS
        )
    else:
        deprecation_month = today.month

    deprecation_date = f"{deprecation_year}-{deprecation_month:02d}-{REMOVAL_DAY_OF_MONTH}"

    return deprecation_date


def load_py_as_ast(path):
    """Load a file as an ast object.

    :param path: The full path to the file
    :return: The ast object
    """
    with open(path, encoding="utf8") as file:
        data = file.read()
        red = RedBaron(data)
    return red


def find_assignment_in_ast(name, ast_file):
    """Find an assignment in an ast object.

    :param name: The name of the assignment to find
    :param ast_file: The ast object
    :return: A list of ast object matching
    """
    res = ast_file.find("assignment", target=lambda x: x.dumps() == name)
    return res
