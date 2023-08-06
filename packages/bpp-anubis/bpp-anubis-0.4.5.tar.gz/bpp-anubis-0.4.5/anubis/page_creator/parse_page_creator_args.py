import argparse


def parse_arguments():
    parser = argparse.ArgumentParser('Creating Object')

    parser.add_argument('--page_object_directory', '-pd', default='page_objects',  help='The directory with all the page/component objects')
    parser.add_argument('--base_object_path',      '-bo', default='_base_page',    help='The file name of the page parent')
    parser.add_argument('--base_locator_path',     '-bl', default='_base_locator', help='The file name of the locator parent')
    parser.add_argument('--object_name',           '-n',  required=True,           help='Name of the new object file (no extension)')
    parser.add_argument('--object_directory',      '-o',  required=True,           help='Directory to save new object file')
    parser.add_argument('--locator_directory',     '-l',  required=True,           help='Directory to save locator for new object')

    return parser.parse_args()
