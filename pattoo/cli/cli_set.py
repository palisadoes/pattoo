#!/usr/bin/env python3
"""Process CLI arguments."""

import sys

# Import project libraries
from pattoo_shared import log
from pattoo.db import language, agent_group


def process(args):
    """Process cli arguments.

    Args:
        args: CLI argparse parser arguments

    Returns:
        None

    """
    # Do modfications
    if args.qualifier == 'language':
        _process_language(args)
        sys.exit(0)
    elif args.qualifier == 'agent_program':
        _process_agent_group(args)
        sys.exit(0)


def _process_language(args):
    """Process language cli arguments.

    Args:
        None

    Returns:
        None

    """
    # Initialize key variables
    if bool(language.exists(args.code)) is True:
        language.update_description(args.code, args.description)
    else:
        log_message = 'Language code "{}" not found.'.format(args.code)
        log.log2die(20005, log_message)


def _process_agent_group(args):
    """Process agent_group cli arguments.

    Args:
        None

    Returns:
        None

    """
    # Initialize key variables
    if bool(agent_group.exists(args.name)) is True:
        agent_group.update_description(args.name, args.description)
    else:
        log_message = 'Agent program  "{}" not found.'.format(args.name)
        log.log2die(20038, log_message)
