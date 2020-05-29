#!/usr/bin/env python3
"""Install pattoo."""

# Main python libraries
import sys
import os
from pathlib import Path
import getpass
import subprocess

try:
    import yaml
except:
    print('Install the Python3 "pyyaml" package, then run this script again')
    sys.exit(2)


# Try to create a working PYTHONPATH
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

def already_written(file_path,env_export):
    with open(file_path,'r') as file:
        for line in file:
            if line == env_export:
                return True
        return False
def set_configdir():
    """
    Automatically sets the configuration directory
    Args:
        None
    Returns:
        None
    """
    path = os.path.join(os.path.join(os.path.expanduser('~')), '.bash_profile')
    config_path = '/opt/Calico/config'
    env_export = 'export PATTOO_CONFIGDIR={}'.format(config_path)
    with open(path,'a') as file:
        if not (already_written(path,env_export)):
            file.write(env_export)
    os.environ['PATTOO_CONFIGDIR'] = config_path

def pattoo_config(config_directory):
    """Create pattoo.yaml file.

    Args:
        config_directory: Configuration directory

    Returns:
        None

    """
    # Initialize key variables
    home_directory = str(Path.home())
    opt_directory = '{0}opt{0}pattoo'.format(os.sep)
    filepath = '{}{}pattoo.yaml'.format(config_directory, os.sep)
    run_dir = (
        '/var/run/pattoo' if getpass.getuser() == 'root' else opt_directory)
    default_config = {
        'pattoo': {
            'language': 'en',
            'log_directory': (
                '{1}{0}pattoo{0}log'.format(os.sep, opt_directory)),
            'log_level': 'debug',
            'cache_directory': (
                '{1}{0}pattoo{0}cache'.format(os.sep, opt_directory)),
            'daemon_directory': (
                '{1}{0}pattoo{0}daemon'.format(os.sep, opt_directory)),
            'system_daemon_directory': ('''\
/var/run/pattoo''' if getpass.getuser() == 'root' else (
    '{1}{0}pattoo{0}daemon'.format(os.sep, run_dir)))
        },
        'pattoo_agent_api': {
            'ip_address': '127.0.0.1',
            'ip_bind_port': 20201
        },
        'pattoo_web_api': {
            'ip_address': '127.0.0.1',
            'ip_bind_port': 20202,
        }
    }

    # Say what we are doing
    print('\nConfiguring {} file.\n'.format(filepath))

    # Get configuration
    config = read_config(filepath, default_config)
    for section, item in sorted(config.items()):
        for key, value in sorted(item.items()):
            new_value = prompt(section, key, value)
            config[section][key] = new_value

    # Check validity of directories
    for key, value in sorted(config['pattoo'].items()):
        if 'directory' in key:
            if os.sep not in value:
                _log('''\
Provide full directory path for "{}" in section "pattoo: {}". \
Please try again.\
'''.format(value, key))

            # Attempt to create directory
            full_directory = os.path.expanduser(value)
            if os.path.isdir(full_directory) is False:
                _mkdir(full_directory)

    # Write file
    with open(filepath, 'w') as f_handle:
        yaml.dump(config, f_handle, default_flow_style=False)


def pattoo_server_config(config_directory):
    """Create pattoo_server.yaml file.

    Args:
        config_directory: Configuration directory

    Returns:
        None

    """
    # Initialize key variables
    filepath = '{}{}pattoo_server.yaml'.format(config_directory, os.sep)
    default_config = {
        'pattoo_db': {
            'db_pool_size': 10,
            'db_max_overflow': 20,
            'db_hostname': 'localhost',
            'db_username': 'pattoo',
            'db_password': 'password',
            'db_name': 'pattoo'
        },
        'pattoo_api_agentd': {
            'ip_listen_address': '0.0.0.0',
            'ip_bind_port': 20201,
        },
        'pattoo_apid': {
            'ip_listen_address': '0.0.0.0',
            'ip_bind_port': 20202,
        },
        'pattoo_ingesterd': {
            'ingester_interval': 3600,
            'batch_size': 500
        }
    }

    # Say what we are doing
    print('\nConfiguring {} file.\n'.format(filepath))

    # Get configuration
    config = read_config(filepath, default_config)
    for section, item in sorted(config.items()):
        for key, value in sorted(item.items()):
            new_value = prompt(section, key, value)
            config[section][key] = new_value

    # Write file
    with open(filepath, 'w') as f_handle:
        yaml.dump(config, f_handle, default_flow_style=False)


def read_config(filepath, default_config):
    """Read configuration file and replace default values.

    Args:
        filepath: Name of configuration file
        default_config: Default configuration dict

    Returns:
        config: Dict of configuration

    """
    # Convert config to yaml
    default_config_string = yaml.dump(default_config)

    # Read config
    if os.path.isfile(filepath) is True:
        with open(filepath, 'r') as f_handle:
            yaml_string = (
                '{}\n{}'.format(default_config_string, f_handle.read()))
            config = yaml.safe_load(yaml_string)
    else:
        config = default_config
    return config


def prompt(section, key, default_value):
    """Log messages and exit abnormally.

    Args:
        key: Configuration key
        default_value: Default value for key

    Returns:
        result: Desired value from user

    """
    # Get input from user
    result = input('''Enter "{}: {}" value (Hit <enter> for: "{}"): \
'''.format(section, key, default_value))
    if bool(result) is False:
        result = default_value

        # Try to create necessary directories
        if 'directory' in key:
            try:
                os.makedirs(result, mode=0o750, exist_ok=True)
            except:
                _log('''\
Cannot create directory {} in configuration file. Check parent directory \
permissions and typos'''.format(result))

    return result


def _log(message):
    """Log messages and exit abnormally.

    Args:
        message: Message to print

    Returns:
        None

    """
    # exit
    print('\nPATTOO Error: {}'.format(message))
    sys.exit(3)


def _mkdir(directory):
    """Recursively creates directory and its parents.

    Args:
        directory: Directory to create

    Returns:
        None

    """
    if os.path.isdir(directory) is False:
        try:
            Path(directory).mkdir(parents=True, mode=0o750, exist_ok=True)
        except OSError:
            _log('''Cannot create directory {}. Please try again.\
'''.format(directory))


def main():
    """Start configuration process.

    Args:
        None

    Returns:
        None

    """
    # Initialize key variables
    if os.environ.get('PATTOO_CONFIGDIR') == None:
        set_configdir()
    config_directory = os.environ.get('PATTOO_CONFIGDIR')

    # Make sure the PATTOO_CONFIGDIR environment variable is set
    if bool(config_directory) is False:
        log_message = ('''\
Set your PATTOO_CONFIGDIR to point to your configuration directory like this:

$ export PATTOO_CONFIGDIR=/path/to/configuration/directory

Then run this command again.
''')
        _log(log_message)

    # Prompt for configuration directory
    print('\nPattoo configuration utility.')

    # Attempt to create configuration directory
    _mkdir(config_directory)

    # Create configuration
    pattoo_config(config_directory)
    pattoo_server_config(config_directory)

    # All done
    output = '''
Successfully created configuration files:

    {0}{1}pattoo.yaml
    {0}{1}pattoo_server.yaml

Next Steps
==========

1) Run the installation script.
'''.format(config_directory, os.sep)
    print(output)


if __name__ == '__main__':
    # Run setup
    main()
