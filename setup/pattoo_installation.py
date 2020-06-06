import argparse
import os
import sys
import getpass

from installation_lib.install import install
from installation_lib.configure import configure_installation
# from installation_lib.db import configure_database
from shared import _run_script, _log


EXEC_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(EXEC_DIR, os.pardir))
_EXPECTED = '{0}pattoo{0}setup'.format(os.sep)
if EXEC_DIR.endswith(_EXPECTED) is True:
    sys.path.append(ROOT_DIR)
else:
    print('''\
This script is not installed in the "{}" directory. Please fix.\
'''.format(_EXPECTED))
    sys.exit(2)


def prompt_args():
    """
    Get CLI arguments for enabling the verbose mode of the installation.
    
    Args:
        None

    Returns:
        NamedTuple of arugument values
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", help="increase output verbosity",
                        action="store_true")
    args = parser.parse_args()
    return args


def install_pattoo():
    if getpass.getuser() != 'root':
        _log('You are currently not running the script as root.\
Run as root to continue')
    args = prompt_args()
    configure_installation(args.prompt)
    # configure_database()
    install(args.prompt)


if __name__ == '__main__':
    install_pattoo()
