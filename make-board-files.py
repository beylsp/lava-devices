#!/usr/bin/python3
import argparse
import os
import sys

import common


def get_dev_type_info(types, name):
    for t in types:
        if name == t["name"]:
            return t
    return None


def generate_device_file(devices_dir, board, types):
    board_name = board["name"]
    dev_type = board["type"]
    fbserial = board["fastboot_serial_number"]
    dev_type_info = get_dev_type_info(types, dev_type)
    vendor = dev_type_info["vendor_id"]
    fbvendor = dev_type_info["fastboot_vendor_id"]
    product = dev_type_info["product_id"]
    fbproduct = dev_type_info["fastboot_product_id"]
    board_file = os.path.join(devices_dir, "%s.jinja2" % board_name)
    with open(board_file, 'w') as board_jinja:
        print("Processing: %s (%s)" % (board_name, board_file))
        board_jinja.write("{%% extends '%s.jinja2' %%}\n" % dev_type)
        board_jinja.write("{%% set fastboot_serial_number = '%s' %%}\n" % fbserial)
        board_jinja.write("{% set adb_serial_number = fastboot_serial_number %}\n")
        board_jinja.write("{%% set device_info = [{'board_id': fastboot_serial_number, 'usb_vendor_id': '%s', 'usb_product_id': '%s'}, {'board_id': fastboot_serial_number, 'usb_vendor_id': '%s', 'usb_product_id': '%s'}] %%}\n" % (vendor, product, fbvendor, fbproduct))
        board_jinja.write("{%% set static_info = [{'board_id': fastboot_serial_number, 'usb_vendor_id': '%s', 'usb_product_id': '%s'}] %%}\n" % (vendor, product))


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
    types = common.load_types(cli.definition)
    boards = common.load_boards(cli.definition)
    for board in boards:
        generate_device_file(cli.devices_dir, board, types)


if __name__ == '__main__':
    main()
