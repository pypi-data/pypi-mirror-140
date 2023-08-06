import configparser
import os
import re
from anubis.id_generator.helpers import *


def main():
    # get args
    args = parse_id_args()

    all_features = []

    # get the last id used and increment it
    cp = configparser.ConfigParser()
    cp.read(args.config_path)
    data = cp['feature_id']
    starting_number = int(data['max'])

    id_gen = id_generator(starting_number)
    for directory in os.walk(args.feature_path):

        for file in directory[2]:
            if is_feature(file) and not has_id(file):
                file_name = os.path.join(directory[0], file)
                path = os.path.join(directory[0], file)

                with open(path) as feature_file:
                    feature_id = next(id_gen)

                    lines = feature_file.readlines()

                    lines[0] = f'@section.{feature_id} ' + int(lines[0].lstrip().startswith('Feature')) * '\n' + lines[0]

                    # feature_file.writelines(lines)
                with open(path, 'w+') as feature_file:
                    feature_file.writelines(lines)

                cp.set('feature_id', 'max', str(feature_id+1))
                cp.write(open(args.config_path, 'w'))

                new_file_name = os.path.join(directory[0], f'{feature_id} {file}')
                # print(f'os.rename({file_name}, {new_file_name})')
                os.rename(file_name, new_file_name)
            else:
                print(f'Skipping: <{file}>')

if __name__ == '__main__':
    main()
