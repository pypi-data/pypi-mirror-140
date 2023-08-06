import requests
import json
import argparse
import os
from datetime import datetime


def __parse_arguments():
    current_date_time = datetime.now().strftime('[%y/%m/%d][%H:%M %p]')
    parser = argparse.ArgumentParser('Creating run')

    # header args
    parser.add_argument('--content-type',    '-ct', default="application/json; charset=utf-8")
    parser.add_argument('--accept',          '-a', default="application/vnd.api+json; version=1")
    parser.add_argument('--access_token',    '-at', required=True)
    parser.add_argument('--client_id',       '-ci', required=True)
    parser.add_argument('--unique_id',       '-ui', required=True)

    # data args
    parser.add_argument('--run_name',        '-rn', default=current_date_time)
    parser.add_argument('--run_description', '-rd', default=f'Run created on {current_date_time}')
    parser.add_argument('--project_id',      '-pi', required=True)

    return parser.parse_args()


def create_test_run(project_id, access_token, client_id, uid, name, description):

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/vnd.api+json; version=1",
        "access-token": access_token,
        "client": client_id,
        "uid": uid,
    }

    data = json.dumps({
        "data": {
            "attributes": {
                "name": name,
                "description": description,
            }
        }
    })

    return requests.post(
        f"https://studio.cucumber.io/api/projects/{project_id}/test_runs",
        headers=headers,
        data=data
    )


def main():
    args = __parse_arguments()

    res = create_test_run(
        project_id=args.project_id,
        access_token=args.access_token,
        client_id=args.client_id,
        uid=args.unique_id,
        name=args.run_name,
        description=args.run_description
    )

    print(res.json()["data"]["id"])


if __name__ == '__main__':
    main()
