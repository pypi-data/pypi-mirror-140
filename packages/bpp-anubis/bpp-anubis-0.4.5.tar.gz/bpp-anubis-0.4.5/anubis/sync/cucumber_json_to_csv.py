import argparse
import csv
import json
from datetime import datetime


def cucumber_json_to_csv(json_input_file_path: str, csv_output_file_path) -> None:
    # open the json and store as dictionary
    with open(json_input_file_path, 'r') as f:
        results = json.load(f)

    # open and create a csv file
    with open(csv_output_file_path, 'w', newline='') as csvfile:
        test = csv.writer(csvfile)
        test.writerow(['run_time', 'team', 'feature_name', 'scenario_name', 'scenario_tags', 'scenario_status', 'error_message', 'duration', 'location'])

        # get data from the file name
        try:
            time_stamp = datetime.fromisoformat(json_input_file_path.split('__')[2].replace('Z.json', ''))  # todo - make this better
            team = json_input_file_path.split('__')[1]
        except IndexError as e:
            print(f'There was an error getting the time stamp or team\n{e}')
            time_stamp = datetime.now()
            team = None

        # for every scenario, write important data to a row in the csv
        for feature in results:
            feature_name = feature['name']
            for element in feature['elements']:
                if element['type'].lower() == 'scenario':
                    scenario_duration = 0
                    error_message = ''

                    for step in element['steps']:
                        if 'result' in step:
                            scenario_duration += step['result']['duration']
                            if 'error_message' in step['result']:
                                error_message = '\n'.join(step['result']['error_message'])

                    row_data = [time_stamp, team, feature_name, element['name'], ' '.join(element['tags']), element['status'], error_message, scenario_duration, element['location']]
                    test.writerow(row_data)
                    # print(row_data) # debug


def parse_args():
    parser = argparse.ArgumentParser("Creating CSV")
    parser.add_argument('--json_input_file_path', '-j', required=True)
    parser.add_argument('--csv_output_file_path', '-c', required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    cucumber_json_to_csv(args.json_input_file_path, args.csv_output_file_path)


if __name__ == '__main__':
    main()
