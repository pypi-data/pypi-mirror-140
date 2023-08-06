import configparser
import sys
import os


def get_accounts(num_processes: int, accounts_file_path: str, accounts_section: str) -> list:
    """
    Reads the `accounts_sections` in the `accounts_file_path` file and return list of accounts
    :param num_processes:
    :param accounts_file_path:
    :param accounts_section:
    :return:
    """

    # try to read the accounts file and create parser
    data = configparser.ConfigParser()
    accounts_data = None
    if os.path.isfile(accounts_file_path):
        data.read(accounts_file_path)
    else:
        print(f'Cannot find this file: <{accounts_file_path}>\nExiting without running tests!')
        sys.exit(1)

    # get the accounts from the parser
    try:
        accounts_data = data[accounts_section]
    except KeyError:
        print(f'Could not find this section: <{accounts_section}>')
        sys.exit(1)

    # return a list of the accounts, if possible
    if num_processes > len(list(accounts_data.values())):
        print("Not enough accounts; Cannot run tests")
        sys.exit(1)
    else:
        return [acc for acc in list(accounts_data.items())]
