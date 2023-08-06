import requests
import argparse


def __parse_arguments():
    parser = argparse.ArgumentParser('Sending results to cucumber studio run')

    # params args
    parser.add_argument('--environment', '-e')
    parser.add_argument('--file_path', '-fp')

    # url args
    parser.add_argument('--cc_upload', '-cu')
    parser.add_argument('--run_id', '-ri')
    parser.add_argument('--result_format', '-rf', default='cucumber-json')

    return parser.parse_args()


def __send_results_to_test_run(environment, file_path, run_id, cc_upload_id, result_format):
    params = (('execution_environment', environment),)
    files = {'file': (file_path, open(file_path, 'rb')), }

    response = requests.post(
        f'https://studio.cucumber.io/import_test_reports/{cc_upload_id}/{run_id}/{result_format}',
        params=params,
        files=files
    )

    print(response.json())


def main():
    args = __parse_arguments()
    __send_results_to_test_run(
        environment=args.environment,
        file_path=args.file_path,
        run_id=args.run_id,
        cc_upload_id=args.cc_upload,
        result_format=args.result_format
    )


if __name__ == '__main__':
    main()
