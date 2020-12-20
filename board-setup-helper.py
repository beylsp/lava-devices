#!/usr/bin/python3
import argparse
import os
import sys
import xmlrpc.client

import common


class LavaXmlRpc(object):
    def __init__(self, host, user, token):
        self.host = host
        self.user = user
        self.token = token

    def __enter__(self):
        uri = 'http://%s:%s@%s/RPC2' % (self.user, self.token, self.host)
        self.xmlrpc = xmlrpc.client.ServerProxy(uri, allow_none=True)
        return self.xmlrpc

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def add_lava_device_types(self, device_types):
        print("Adding device types")
        for device_type in device_types:
            name = device_type["name"]
            description = device_type["description"]
            print("- %s" %  name)
            self.xmlrpc.scheduler.device_types.add(name, description, display=True)

    def add_lava_devices(self, devices):
        print("Adding lava devices")
        for device in devices:
            hostname = device["name"]
            type_name = device["type"]
            worker_hostname = device["worker"]
            description = device["description"]
            print("- %s (%s) on %s" % (hostname, type_name, worker_hostname))
            self.xmlrpc.scheduler.devices.add(hostname, type_name, worker_hostname, description)
            tags = device["tags"]
            for name in tags:
                self.xmlrpc.scheduler.devices.tags.add(hostname, name)


def parse_cli():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-b", "--boards-definition-file", dest="definition",
        default="boards.yaml", metavar="yaml",
        help="boards definition file (default: %(default)s)"
    )
    parser.add_argument(
        "-H", "--lava-host", dest="host", required=True,
        help="lava hostname"
    )
    parser.add_argument(
        "-t", "--lava-token", dest="token", required=True,
        help="lava token"
    )
    parser.add_argument(
        "-u", "--lava-user", dest="user", required=True,
        help="lava user name"
    )

    return parser.parse_args(sys.argv[1:])


def main():
    cli = parse_cli()
    try:
        with LavaXmlRpc(cli.host, cli.user, cli.token) as xmlrpc:
            devices = common.load_boards(cli.definition)
            xmlrpc.add_lava_devices(devices)
    except Exception as err:
        print("XMLRPC: %s" % err)
        sys.exit(1)


if __name__ == '__main__':
    main()
