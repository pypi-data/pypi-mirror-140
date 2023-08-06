import argparse
import re

def parse_id_args():
    parser = argparse.ArgumentParser('Updating features and ids')
    parser.add_argument('--feature_path', '-fp', help='path to directory or file to add ids')
    parser.add_argument('--config_path', '-cp', help='path to directory or config')
    return parser.parse_args()


def id_generator(starting_number=0):
    while True:
        yield starting_number
        starting_number += 1


def has_id(file_name):
    pattern = re.compile(r'(?P<fid>[0-9]+).*feature')
    id_matches = re.search(pattern, file_name)
    return id_matches is not None


def is_feature(file_name):
    pattern = re.compile(r'.*(?P<extension>\.feature)')
    ext_matches = re.search(pattern, file_name)
    return ext_matches is not None
