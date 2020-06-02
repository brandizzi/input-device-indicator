#!/usr/bin/env python
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

class Device:
    """
    The `Device` class represents a device listed by `xinput`. Each device 
    should have an id, a name and the id of a parent device.

    >>> d = Device(id=1, name='abc', level='master', parent_id=4, type='keyboard')
    >>> d
    Device(1, 'abc', 4, 'master', 'keyboard')

    You can also add a device as a child of another with ``add_child()``:

    >>> d.add_child(Device(2, 'def', 1, 'slave', 'keyboard'))
    >>> d
    Device(1, 'abc', 4, 'master', 'keyboard', [Device(2, 'def', 1, 'slave', 'keyboard')])
    """

    def __init__(self, id, name, parent_id, level, type):
        self.id = id
        self.name = name
        self.parent_id = parent_id
        self.level = level
        self.type = type
        self.children = []

    def __repr__(self):
        parameters = [
            self.id, self.name, self.parent_id, self.level, self.type
        ]
        if self.children:
            parameters.append(self.children)
        return 'Device({0})'.format(
            ', '.join(repr(p) for p in parameters)
        )


    def add_child(self, device):
        self.children.append(device)

LINE_REGEX = re.compile(
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
    [Device(2, 'A', 3, 'master', 'pointer', [Device(4, 'A1', 2, 'slave', 'pointer')]), Device(3, 'B', 2, 'master', 'keyboard', [Device(5, 'B1', 3, 'slave', 'keyboard')]), Device(6, 'C', None, 'slave', 'floating')]
    """

    device_list = []
    device_map = {}
    lines = string.split('\n')
    for l in lines:
        if not l:
            continue
        device = parse_line(l)
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
    Device(2, 'A', 3, 'master', 'pointer')

    It naturally should also handle floating devices:

    >>> parse_line('~ B1   id=5    [floating slave]')
    Device(5, 'B1', None, 'slave', 'floating')
    """

    m = LINE_REGEX.search(line)
    if m is None:
        raise ValueError('Could not parse line {0}'.format(repr(line)))
    id = int(m.group('id'))
    name = m.group('name').strip()
    parent_id = int(m.group('parent_id')) if m.group('parent_id') else None
    level = m.group('level1') or m.group('level2')
    type = m.group('type1') or m.group('type2')
    return Device(id, name, parent_id, level, type)
