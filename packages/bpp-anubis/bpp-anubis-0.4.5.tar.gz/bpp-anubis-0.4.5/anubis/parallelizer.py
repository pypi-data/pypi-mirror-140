from subprocess import call
from .arg_parser import parse_arguments
import os


def command_generator(account_feature_groups: list) -> str:
    """
    Use args, accounts, and features to construct behave command
    :param account_feature_groups:
    :return:
    """

    # get arguments
    args = parse_arguments()

    # get data for constructing behave command
    process_name = account_feature_groups[0][0]
    acc = account_feature_groups[0][1].split()
    feature_set = account_feature_groups[1]

    # construct the behave command
    results_json = None
    commands = []
    for env in args.env:
        optional_retry = f'-D retry="{args.retry}" ' if args.retry > 1 else ' '
        optional_browser = f'-D browser="{args.browser}" -D headless="{args.headless}" ' if args.browser else ' '
        optional_userdata = f'-D user="{acc[0]}" -D pass="{acc[1]}" ' if args.account_file and args.account_section else ' '
        tags = ' '.join('--tags="@{}" '.format(t) for t in args.itags) + ' '.join('--tags="~@{}" '.format(t) for t in args.etags)
        project_specific_args = (' '.join([f"-D {arg}" for arg in args.arbitrary]) if args.arbitrary else ' ') + ' '
        results_json = os.path.join(args.output_dir, f'{process_name}.json')
        features_string = ' '.join("\"{}\"".format(feature_path) for feature_path in feature_set)

        cmd = (f'behave -D parallel="True" -D env="{env}" ' + optional_retry + optional_browser + optional_userdata +
               tags + ' ' + project_specific_args + f'-f json.pretty -o {results_json} ' + f'-D output="{args.output_dir}" ' +
               features_string)
        commands.append(cmd)

    # run the command(s)
    for command in commands:
        print(command, end='\n')
        r = call(command, shell=True)

    return results_json
