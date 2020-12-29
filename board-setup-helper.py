#!/usr/bin/python3
import argparse
import datetime as dt
import os
import socket
import sys
import time
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
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def worker_ready(self, worker_hostname):
        try:
            workers = self.xmlrpc.scheduler.workers.list()
            return worker_hostname in workers
        except socket.gaierror as err:
            return False

    def wait_for_worker(self, worker_hostname, timeout):
        start = dt.datetime.now()
        if timeout == 0:
            wait_until = 0
        else:
            wait_until = start + dt.timedelta(seconds=timeout)
        ready = False
        timed_out = True
        current = start
        while current < wait_until:
            if worker_ready(worker_hostname):
                ready = True
                timed_out = False
                break
            current = dt.datetime.now()
        if timed_out:
            print("timeout occurred after waiting %s seconds for worker '%s'" % (timeout, worker_hostname))
        return ready

    def add_lava_device_types(self, device_types, retries=1):
        print("Adding device types")
        for device_type in device_types:
            name = device_type["name"]
            description = device_type["description"]
            print("- %s" %  name)
            retry_count = 0
            failed = True
            while retry_count <= retries:
                try:
                    self.xmlrpc.scheduler.device_types.add(name, description, True, False, 0, "jobs")
                except socket.gaierror as err:
                    errm = "%s (after %s retries)" % (err, retry_count)
                    retry_count += 1
                    time.sleep(5)
                else:
                    failed = False
                    break
            if failed:
                raise Exception(errm)

    def add_lava_devices(self, devices, retries=1, timeout=60, strict=True):
        print("Adding lava devices")
        for device in devices:
            hostname = device["name"]
            type_name = device["type"]
            worker_hostname = device["worker"]

            print("- %s (%s) on %s" % (hostname, type_name, worker_hostname))
            running = self.wait_for_worker(worker_hostname, timeout)
            if strict and not running:
                print("strict mode, abort")
                sys.exit(1)
            else:
                continue

            description = device["description"]
            retry_count = 0
            failed = True
            while retry_count <= retries:
                try:
                    self.xmlrpc.scheduler.devices.add(hostname, type_name, worker_hostname, description)
                    tags = device["tags"]
                    for name in tags:
                        self.xmlrpc.scheduler.devices.tags.add(hostname, name)
                except socket.gaierror as err:
                    errm = "%s (after %s retries)" % (err, retry_count)
                    retry_count += 1
                    time.sleep(5)
                else:
                    failed = False
                    break
            if failed:
                raise Exception(errm)


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
    parser.add_argument(
        "--retries", type=int, default=5,
        help="XMLRPC connection retries"
    )
    parser.add_argument(
        "--worker-timeout", type=int, default=120,
        help="time in seconds to wait for worker, zero for no timeout"
    )
    parser.add_argument(
        "-s", "--strict", action="store_true",
        help="fail if worker is not running"
    )

    return parser.parse_args(sys.argv[1:])


def main():
    cli = parse_cli()
    try:
        with LavaXmlRpc(cli.host, cli.user, cli.token) as xmlrpc:
            device_types = common.load_types(cli.definition)
            xmlrpc.add_lava_device_types(device_types, cli.retries)
            devices = common.load_boards(cli.definition)
            xmlrpc.add_lava_devices(devices, cli.retries, cli.worker_timeout, cli.strict)
    except Exception as err:
        print("XMLRPC: %s" % err)
        sys.exit(1)


if __name__ == '__main__':
    main()
