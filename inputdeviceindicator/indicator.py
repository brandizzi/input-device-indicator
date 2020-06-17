import gi
gi.require_version('Gtk', '3.0')  # noqa
gi.require_version('AppIndicator3', '0.1')  # noqa

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator

import os.path

from inputdeviceindicator.command import XInput


def get_indicator():
    xinput = XInput()
    menu_callbacks = MenuCallbacks(xinput)
    menu = build_menu(xinput.list(), menu_callbacks)
    return build_indicator(menu)


def build_indicator(menu):
    indicator = appindicator.Indicator.new(
        'input-device-indicator', 'keyboard',
        appindicator.IndicatorCategory.SYSTEM_SERVICES
    )
    indicator.set_menu(menu)
    return indicator


def build_menu(devices, callbacks):
    """
    Build a menu from a list of devices, connecting them to corresponding
    callbacks from `callbacks`.

    Let's suppose we have the following devices, for example:

    >>> from inputdeviceindicator.command import parse
    >>> devices = parse('''
    ... ⎡ A        id=2    [master pointer  (3)]
    ... ⎜   ↳ A1   id=4    [slave  pointer  (2)]
    ... ⎣ B        id=3    [master keyboard (2)]
    ...     ↳ B1   id=5    [slave  keyboard (3)]
    ...         This device is disabled
    ... ''')

    ...then the menu should have an option for every one:

    >>> from inputdeviceindicator.mock import MockMenuCallbacks
    >>> menu = build_menu(devices, MockMenuCallbacks())
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

    The child devices check menu items should have their `toggled` event
    connected to the method `child_device_check_menu_item_toggled` from
    `callbacks`:

    >>> items[3].set_active(True)
    Device B1 toggled to True

    The last item from the menu is an option to quit the application:

    >>> items[-1].get_label()
    'Quit'

    It will be connected to the `quit_menu_item_activate` method from
    `callbacks`:

    >>> items[-1].emit('activate')
    Quit menu item activated
    """
    menu = gtk.Menu()
    for d in devices:
        menu.append(gtk.MenuItem(d.name))
        for c in d.children:
            cdcmi = build_device_check_menu_item(
                c, callbacks.child_device_check_menu_item_toggled
            )
            menu.append(cdcmi)
    menu.append(gtk.SeparatorMenuItem())
    quit_menu_item = gtk.MenuItem('Quit')
    quit_menu_item.connect('activate', callbacks.quit_menu_item_activate)
    menu.append(quit_menu_item)
    menu.show_all()
    return menu


def build_device_check_menu_item(device, callback):
    """
    Returns a `gtk.CheckMenuItem` representing the given child device, with the
    given callback connected to its `toggled` event..

    >>> from inputdeviceindicator.command import Device
    >>> from inputdeviceindicator.mock import noop
    >>> d = Device(1, 'abc', 4, 'slave', 'keyboard')
    >>> mi = build_device_check_menu_item(d, noop)
    >>> isinstance(mi, gtk.CheckMenuItem)
    True

    It should have the device's name as its title:

    >>> mi.get_label()
    'abc'

    Also, the original device instance should be attached to the menu item:

    >>> mi.device == d
    True

    If the device is enabled, the item is active:

    >>> mi.get_active()
    True

    Otherwise, the item is inactive (unchecked):

    >>> d.enabled = False
    >>> mi = build_device_check_menu_item(d, noop)
    >>> mi.get_active()
    False

    The menu item should executed the given callback when the `toggled` event
    is called:

    >>> def callback(mi):
    ...    print("menu item toggled to " + str(mi.get_active()))
    >>> mi = build_device_check_menu_item(d, callback)
    >>> mi.set_active(True)
    menu item toggled to True
    >>> mi.set_active(False)
    menu item toggled to False
    >>> mi.emit('toggled')
    menu item toggled to False

    If the function receives a parent device, it should fail:

    >>> build_device_check_menu_item(
    ...     Device(1, 'abc', 4, 'master', 'keyboard'), noop
    ... )
    Traceback (most recent call last):
      ...
    AssertionError: build_device_check_menu_item() only accepts child devices.

    """
    assert device.level == \
        'slave', "build_device_check_menu_item() only accepts child devices."
    menu_item = gtk.CheckMenuItem(device.name)
    menu_item.set_active(device.enabled)
    menu_item.device = device
    menu_item.connect('toggled', callback)
    return menu_item


class MenuCallbacks:

    def __init__(self, xinput):
        self.xinput = xinput

    def child_device_check_menu_item_toggled(self, check_menu_item):
        """
        Callback to enable or disable a device when its `gtk.CheckMenuItem` is
        clicked.

        It should receive a `XInput`-like object as argument:

        >>> from inputdeviceindicator import mock
        >>> mcs = MenuCallbacks(mock.MockXInput())

        When called with a menu item, it should try to toggle its state:

        >>> from inputdeviceindicator.command import Device
        >>> mi = build_device_check_menu_item(
        ...    Device(1, 'abc', 4, 'slave', 'keyboard'), lambda _: None
        ... )
        >>> mi.set_active(False)
        >>> mcs.child_device_check_menu_item_toggled(mi)
        Device abc disabled
        >>> mi.set_active(True)
        >>> mcs.child_device_check_menu_item_toggled(mi)
        Device abc enabled
        """
        if check_menu_item.get_active():
            self.xinput.enable(check_menu_item.device)
        else:
            self.xinput.disable(check_menu_item.device)

    def quit_menu_item_activate(self, menu_item):
        """
        Callback for quitting the application.

        >>> from inputdeviceindicator.mock import MockXInput
        >>> callbacks = MenuCallbacks(MockXInput())

        It should do it by calling `gtk.main_quit()`:

        >>> real_main_quit = gtk.main_quit
        >>> gtk.main_quit = lambda: print("gtk.main_quit() called")
        >>> MenuCallbacks(MockXInput()).quit_menu_item_activate(None)
        gtk.main_quit() called
        >>> gtk.main_quit = real_main_quit
        """
        gtk.main_quit()
