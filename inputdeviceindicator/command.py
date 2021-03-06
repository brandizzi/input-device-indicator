# Copyright © 2020 Adam Brandizzi
#
# This file is part of Input Device Indicator.
#
# Input Device Indicator is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Input Device Indicator is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Input Device Indicator.  If not, see <https://www.gnu.org/licenses/>

import re
import subprocess


class XInput:

    def list(self):
        """
        Lists the devices as a forest of `Device` instances:

        >>> xi = XInput()
        >>> xi.list() # doctest: +ELLIPSIS
        [Device(..., ..., ..., [Device(...)]), Device(..., ..., ...)]
        """
        cp = subprocess.run(
            ['xinput', 'list', '--long'], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return parse(cp.stdout.decode('utf-8'))

    def disable(self, device):
        """
        Given a specific device...

        >>> xi = XInput()
        >>> devices = xi.list()
        >>> device = devices[1].children[-1]
        >>> # For restoring later.
        >>> current_status = device.enabled

        ...`disable()` disables it:

        >>> xi.disable(device)
        >>> device = get_device_from_list_by_id(xi.list(), device.id)
        >>> device.enabled
        False

        To enable it again, you can use `enable()`:

        >>> xi.enable(device)
        >>> device = get_device_from_list_by_id(xi.list(), device.id)
        >>> device.enabled
        True

        >>> # If it was disabled before, let it this way.
        >>> if not current_status:
        ...    xi.disable(device)
        """
        subprocess.run(['xinput', '--disable', str(device.id)])

    def enable(self, device):
        """
        Given a specific device...

        >>> xi = XInput()
        >>> devices = xi.list()
        >>> device = devices[1].children[-1]
        >>> # For restoring later.
        >>> current_status = device.enabled
        >>> xi.disable(device)

        ...`enable()` enables it:

        >>> xi.enable(device)
        >>> device = get_device_from_list_by_id(xi.list(), device.id)
        >>> device.enabled
        True

        >>> # If it was disabled before, let it this way.
        >>> if not current_status:
        ...    xi.disable(device)
        """
        subprocess.run(['xinput', '--enable', str(device.id)])


class Device:
    """
    The `Device` class represents a device listed by `xinput`. Each device
    should have an id, a name and the id of a parent device.

    >>> d = Device(
    ...     id=1, name='abc', level='master', parent_id=4, type='keyboard'
    ... )
    >>> d
    Device(1, 'abc', 4, 'master', 'keyboard', True)

    You can also add a device as a child of another with ``add_child()``:

    >>> d.add_child(Device(2, 'def', 1, 'slave', 'keyboard'))
    >>> d
    Device(1, 'abc', 4, 'master', 'keyboard', True, [Device(2, 'def', 1, \
'slave', 'keyboard', True)])
    """

    def __init__(self, id, name, parent_id, level, type):
        self.id = id
        self.name = name
        self.parent_id = parent_id
        self.level = level
        self.type = type
        self.enabled = True
        self.children = []

    def __repr__(self):
        parameters = [
            self.id, self.name, self.parent_id, self.level, self.type,
            self.enabled
        ]
        if self.children:
            parameters.append(self.children)
        return 'Device({0})'.format(
            ', '.join(repr(p) for p in parameters)
        )

    def add_child(self, device):
        self.children.append(device)


MAIN_LINE_REGEX = re.compile(
    r'''
        [~⎡⎜⎣]?(\s+↳)?                   \s+   # discarded
        (?P<name>.*)                     \s+
        id=(?P<id>\d+)                   \s+
        \[
            (
                (?P<level1>master|slave) \s+
                (?P<type1>\w+)           \s+
                \((?P<parent_id>\d+)\)
            |
                (?P<type2>floating)      \s+
                (?P<level2>master|slave)
            )
        \]
    ''',
    re.VERBOSE
)

SUBORDINATE_LINE_REGEX = re.compile(r'^\s+[^\s↳]')


def parse(string):
    """
    As its name implies, `Parser` does parse `xinput` output.

    >>> parse('''
    ... ⎡ A        id=2    [master pointer  (3)]
    ... ⎜   ↳ A1   id=4    [slave  pointer  (2)]
    ... ⎣ B        id=3    [master keyboard (2)]
    ...     ↳ B1   id=5    [slave  keyboard (3)]
    ... ~ C        id=6    [floating slave]
    ... ''')
    [Device(2, 'A', 3, 'master', 'pointer', True, \
[Device(4, 'A1', 2, 'slave', 'pointer', True)]), \
Device(3, 'B', 2, 'master', 'keyboard', True, \
[Device(5, 'B1', 3, 'slave', 'keyboard', True)]), \
Device(6, 'C', None, 'slave', 'floating', True)]

    `parse()` does deal well with the long output:

    >>> parse('''
    ... ⎡ A        id=2    [master pointer  (3)]
    ...     Reporting 1 classes:
    ...         Class originated from: 7. Type: XIKeyClass
    ...            Keycodes supported: 248
    ... ⎜   ↳ A1   id=4    [slave  pointer  (2)]
    ...         Reporting 1 classes:
    ...             Class originated from: 7. Type: XIKeyClass
    ...                 Keycodes supported: 248
    ... ⎣ B        id=3    [master keyboard (2)]
    ...     Reporting 1 classes:
    ...         Class originated from: 7. Type: XIKeyClass
    ...     ↳ B1   id=5    [slave  keyboard (3)]
    ...         Reporting 1 classes:
    ...             Class originated from: 7. Type: XIKeyClass
    ...                 Keycodes supported: 248
    ... ~ C        id=6    [floating slave]
    ...     Reporting 1 classes:
    ...         Class originated from: 7. Type: XIKeyClass
    ...            Keycodes supported: 248
    ... ''')
    [Device(2, 'A', 3, 'master', 'pointer', True, \
[Device(4, 'A1', 2, 'slave', 'pointer', True)]), \
Device(3, 'B', 2, 'master', 'keyboard', True, \
[Device(5, 'B1', 3, 'slave', 'keyboard', True)]), \
Device(6, 'C', None, 'slave', 'floating', True)]

    If a device is disabled, so should be the object returned by `parse()`:

    >>> parse('''
    ... ⎡ A        id=2    [master pointer  (3)]
    ...     This device is disabled
    ...     Reporting 1 classes:
    ...         Class originated from: 7. Type: XIKeyClass
    ...            Keycodes supported: 248
    ... ⎣ B        id=3    [master keyboard (2)]
    ...     Reporting 1 classes:
    ...         Class originated from: 7. Type: XIKeyClass    ... ''')
    [Device(2, 'A', 3, 'master', 'pointer', False), \
Device(3, 'B', 2, 'master', 'keyboard', True)]
    """
    device_list = []
    device_map = {}
    lines = string.split('\n')
    for line in lines:
        if not line or SUBORDINATE_LINE_REGEX.match(line):
            if 'This device is disabled' in line:
                device.enabled = False
            continue
        device = parse_line(line)
        device_map[device.id] = device
        if device.level == 'slave' and device.type != 'floating':
            device_map[device.parent_id].add_child(device)
        else:
            device_list.append(device)
    return device_list


def parse_line(line):
    """
    `parse_line()` parses one line from the `xinput` output into a `Device`
    object:

    >>> parse_line('⎡ A    id=2    [master pointer  (3)]')
    Device(2, 'A', 3, 'master', 'pointer', True)

    It naturally should also handle floating devices:

    >>> parse_line('~ B1   id=5    [floating slave]')
    Device(5, 'B1', None, 'slave', 'floating', True)
    """
    m = MAIN_LINE_REGEX.search(line)
    if m is None:
        raise ValueError('Could not parse line {0}'.format(repr(line)))
    id = int(m.group('id'))
    name = m.group('name').strip()
    parent_id = int(m.group('parent_id')) if m.group('parent_id') else None
    level = m.group('level1') or m.group('level2')
    type = m.group('type1') or m.group('type2')
    return Device(id, name, parent_id, level, type)


def get_device_from_list_by_id(devices, device_id):
    """
    Given a list/tree returned by `XInput.list()` and a device id, returns the
    device with the given id:

    >>> xi = XInput()
    >>> devices = xi.list()
    >>> devices[0] == get_device_from_list_by_id(devices, devices[0].id)
    True

    It should work even with children devices:

    >>> devices[0].children[-1] == get_device_from_list_by_id(
    ...     devices,
    ...     devices[0].children[-1].id
    ... )
    True

    (This function was made for tests but may work elsewhere.)
    """
    for parent_device in devices:
        if parent_device.id == device_id:
            return parent_device
        for child_device in parent_device.children:
            if child_device.id == device_id:
                return child_device
    return None
