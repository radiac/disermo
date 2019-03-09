#!/usr/bin/env python3.7
"""
Example Disermo script
"""
from __future__ import annotations
import sys

from disermo import Node, Check, checks, notifiers, storage


# Define storage
store = storage.CSV('example.csv')
email = notifiers.Email(
    from_addr='user@example.com',
    to_addr='user@example.com',
    after=3,
)
cli = notifiers.Stream(sys.stdout)


MyServer = Node('My server').add(
    Check('Storage').add(
        checks.storage.FreeSpace(drive='/dev/sda1'),
    ),
    Check('CPU').add(
        checks.sensors.CPUTemperature(),
        checks.system.Load(),
    ),
    Check('Remote').add(
        checks.remote.Web('http://example.com'),
    ),
).notify(cli)


def disermo():
    MyServer.check(storage=store)


if __name__ == '__main__':
    disermo()
