"""
Main script

Functions
---------
app
    Script that launch analysis from a JSON configuration file.
"""
import argparse
from mc2s.cars_data import CARSData
from carsdata.utils import common
from carsdata.utils.files import read_json


def app() -> None:
    """
    Main script that parse the command line arguments,
    if --json is not used, ask to select a configuration file.
    Then, parse the config file and use arguments to create a CARSData application object and run it.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--json', help='config file in json format', type=str)
    args = parser.parse_args()
    if args.json:
        json_file = args.json
    else:
        json_file = common.select_file()
    args = read_json(json_file)
    CARSData(**args).run()


if __name__ == '__main__':
    app()
