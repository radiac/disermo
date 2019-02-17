#!/usr/bin/env python3.7
"""
Example Disermo script
"""
from __future__ import annotations

import click

from disermo import Node, Check, checks, notifiers, storage


# Define storage
store = storage.CSV('example.csv')
email = notifiers.Email(
    from_addr='user@example.com',
    to_addr='user@example.com',
    after=3,
)


MyServer = Node('My server').add(
    Check('Storage').add(
        checks.storage.FreeSpace(drive='/dev/sd0'),
    ),
    Check('CPU').add(
        checks.sensors.CPUTemperature(),
        checks.system.Load(),
    ),
).notify(email)


@click.command()
def disermo(config_path: str):
    MyServer.check(storage=store)


if __name__ == '__main__':
    disermo()
