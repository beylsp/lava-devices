#!/usr/bin/python3
import argparse
import os
import sys

import common


def generate_device_file(devices_dir, board):
    board_name = board["name"]
    dev_type = board["type"]
    fserial = board["fastboot_serial_number"]
    board_file = os.path.join(devices_dir, "%s.jinja2" % board_name)
    with open(board_file, 'w') as board_jinja:
        print("Processing: %s (%s)" % (board_name, board_file))
        board_jinja.write("{%% extends '%s.jinja2' %%}\n" % dev_type)
        board_jinja.write("{%% set fastboot_serial_number = '%s' %%}\n" % fserial)
        board_jinja.write("{% set adb_serial_number = fastboot_serial_number %}\n")
        board_jinja.write("{% set static_info = [{'board_id': fastboot_serial_number}] %}\n")


def parse_cli():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-b", "--boards-definition-file", dest="definition",
        default="boards.yaml", metavar="yaml",
        help="boards definition file (default: %(default)s)"
    )
    parser.add_argument(
        "-d", "--devices-dir", default="devices",
        help="devices dir (default: %(default)s)"
    )

    return parser.parse_args(sys.argv[1:])


def main():
    cli = parse_cli()
    boards = common.load_boards(cli.definition)
    for board in boards:
        generate_device_file(cli.devices_dir, board)


if __name__ == '__main__':
    main()
