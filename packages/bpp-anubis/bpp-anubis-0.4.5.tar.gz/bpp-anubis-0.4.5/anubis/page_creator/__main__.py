import os.path
import sys
from . import parse_page_creator_args


def main():
    # parse arguments
    args = parse_page_creator_args.parse_arguments()

    # cancel if the page exists
    if os.path.isfile(os.path.join(args.page_object_directory, args.object_directory, f'{args.object_name}.py')):
        sys.exit('That file already exists')
    else:
        object_path = os.path.join(args.page_object_directory, args.object_directory, f'{args.object_name}.py')
        locator_path = os.path.join(args.page_object_directory, f'{args.locator_directory}', f'{args.object_name}.py')

        # create the locator file
        with open(locator_path, 'w+') as lf:
            lf.write(
                (
                    f'from {args.page_object_directory}.{args.base_locator_path.replace("/", ".")} import LocatorParent\n'
                    'from selenium.webdriver.common.by import By\n\n\n'
                    'class Locators(LocatorParent):\n'
                    '\tdef __init__(self):\n'
                    '\t\tsuper().__init__()\n'
                    '\n'
                )
            )

        # create the object file
        with open(object_path, 'w+') as of:
            of.write((
                f'from {args.page_object_directory}.{args.base_object_path.replace("/", ".")} import BasePage\n'
                f'from {args.page_object_directory}.{args.locator_directory.replace("/", ".")} import {args.object_name}\n\n\n'
                f'class Locators(BasePage):\n'
                '\tdef __init__(self, context):\n'
                '\t\tsuper().__init__(context)\n'
                f'\t\tself.locators = {args.object_name}.Locators()\n'
                '\n'
            ))


if __name__ == '__main__':
    # run everything
    main()
    sys.exit(0)
