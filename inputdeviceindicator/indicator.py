import gi
gi.require_version('Gtk', '3.0')  # noqa
gi.require_version('AppIndicator3', '0.1')  # noqa

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator

import os.path

from inputdeviceindicator.command import XInput


class Application:

    def __init__(self):
        self.xinput = XInput()
        self.menu = build_menu(self.xinput.list())
        connect_device_check_menu_item_toggle_callback(self.menu, self.xinput)
        self.indicator = build_indicator(self.menu)

    def main(self):
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        gtk.main()


def build_indicator(menu):
    indicator = appindicator.Indicator.new(
        'input-device-indicator', 'keyboard',
        appindicator.IndicatorCategory.SYSTEM_SERVICES
    )
    indicator.set_menu(menu)
    return indicator


def build_menu(devices):
    """ Build a menu from a list of devices. Let's suppose we have the
    following devices, for example:

    >>> from inputdeviceindicator.command import parse
    >>> devices = parse('''
    ... ⎡ A        id=2    [master pointer  (3)]
    ... ⎜   ↳ A1   id=4    [slave  pointer  (2)]
    ... ⎣ B        id=3    [master keyboard (2)]
    ...     ↳ B1   id=5    [slave  keyboard (3)]
    ...         This device is disabled
    ... ''')
    >>> devices
    [Device(2, 'A', 3, 'master', 'pointer', True, \
[Device(4, 'A1', 2, 'slave', 'pointer', True)]), \
Device(3, 'B', 2, 'master', 'keyboard', True, \
[Device(5, 'B1', 3, 'slave', 'keyboard', False)])]

    >>> menu = build_menu(devices)

    ... then the menu should have an option for every one:

    >>> items = menu.get_children()
    >>> items[0].get_label()
    'A'
    >>> items[1].get_label()
    'A1'
    >>> items[2].get_label()
    'B'
    >>> items[3].get_label()
    'B1'

    An enabled device should be an active (checked) `gtk.CheckMenuItem`:

    >>> items[1].get_active()
    True

    A disabled device should then be an inactive (unchecked)
    `gtk.CheckMenuItem`:

    >>> items[3].get_active()
    False
    """

    menu = gtk.Menu()
    for d in devices:
        menu.append(build_menu_item(d))
        for c in d.children:
            menu.append(build_menu_item(c))
    menu.show_all()
    return menu


def build_menu_item(device):
    """
    Returns a `gtk.MenuItem` representing the device.


    It should have the device's name as its title:

    >>> from command import Device
    >>> d = Device(1, 'abc', 4, 'master', 'keyboard')
    >>> mi = build_menu_item(d)
    >>> mi.get_label()
    'abc'

    Also, the original device instance should be attached to the menu item:

    >>> mi.device == d
    True

    If it is a parent device, it should be a "plain" `gtk.MenuItem` (i. e., not
    a `gtk.CheckMenuItem`):

    >>> isinstance(mi, gtk.MenuItem)
    True
    >>> isinstance(mi, gtk.CheckMenuItem)
    False

    If it is a child device, it should be a `gtk.CheckMenuItem`:

    >>> d = Device(1, 'abc', 4, 'slave', 'keyboard')
    >>> mi = build_menu_item(d)
    >>> isinstance(mi, gtk.CheckMenuItem)
    True

    The reason for the difference is that we want the parent devices to be
    inert. As far as we know, the parent device cannot be disabled so there is
    no reason to have state in it.

    If the child device is enabled, the item is active:

    >>> mi.get_active()
    True

    Otherwise, the item is inactive (unchecked):

    >>> d.enabled = False
    >>> mi = build_menu_item(d)
    >>> mi.get_active()
    False
    """
    if device.level == 'master':
        menu_item = gtk.MenuItem(device.name)
    else:
        menu_item = gtk.CheckMenuItem(device.name)
        menu_item.set_active(device.enabled)
    menu_item.device = device
    return menu_item


def device_check_menu_item_toggle_callback(check_menu_item, xinput):
    """
    Callback to enable or disable a device when its `gtk.CheckMenuItem` is
    clicked.

    It should receive a `XInput`-like object as argument:

    >>> from inputdeviceindicator import mock
    >>> xinput = mock.MockXInput()

    When called with a menu item, it should try to toggle its state:

    >>> from command import Device
    >>> mi = build_menu_item(Device(1, 'abc', 4, 'slave', 'keyboard'))
    >>> mi.set_active(False)
    >>> device_check_menu_item_toggle_callback(mi, xinput)
    Device abc disabled
    >>> mi.set_active(True)
    >>> device_check_menu_item_toggle_callback(mi, xinput)
    Device abc enabled
    """
    if check_menu_item.get_active():
        xinput.enable(check_menu_item.device)
    else:
        xinput.disable(check_menu_item.device)


def connect_device_check_menu_item_toggle_callback(menu, xinput):
    for mi in menu.get_children():
        if isinstance(mi, gtk.CheckMenuItem) and hasattr(mi, 'device'):
            mi.connect(
                'toggled', device_check_menu_item_toggle_callback, xinput
            )


if __name__ == "__main__":
    application = Application()
    application.main()