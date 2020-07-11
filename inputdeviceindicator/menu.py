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

import gi
gi.require_version('Gtk', '3.0')  # noqa
gi.require_version('AppIndicator3', '0.1')  # noqa

from gi.repository import Gtk as gtk

from inputdeviceindicator.command import XInput
from inputdeviceindicator.about import get_about_dialog


def get_menu():
    xinput = XInput()
    menu = gtk.Menu()
    about_dialog = get_about_dialog()
    menu_callbacks = MenuCallbacks(xinput, menu, about_dialog)
    build_menu(menu, xinput.list(), menu_callbacks)
    return menu


def build_menu(menu, devices, callbacks):
    """
    Build a menu from a list of devices, connecting them to corresponding
    callbacks from `callbacks`.

    The menu should be created beforehand to be given to the function:

    >>> menu = gtk.Menu()

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
    >>> build_menu(menu, devices, MockMenuCallbacks())
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

    The antepenultimate item from the menu is an option to refresh the device
    items...

    >>> items[-3].get_label()
    'Refresh'

    ...the second to last option opens the "About" dialog...

    >>> items[-2].get_label()
    'About'

    ...and the last item from the menu is an option to quit the application:

    >>> items[-1].get_label()
    'Quit'

    It will be connected to the `quit_menu_item_activate` method from
    `callbacks`:

    >>> items[-1].emit('activate')
    Quit menu item activated
    """
    for c in menu.get_children():
        menu.remove(c)

    for d in devices:
        menu.append(gtk.MenuItem(label=d.name))
        for c in d.children:
            cdcmi = build_device_check_menu_item(
                c, callbacks.child_device_check_menu_item_toggled
            )
            menu.append(cdcmi)

    menu.append(gtk.SeparatorMenuItem())

    refresh_menu_item = gtk.MenuItem(label='Refresh')
    refresh_menu_item.connect(
        'activate', callbacks.refresh_menu_item_activate
    )
    menu.append(refresh_menu_item)

    about_menu_item = gtk.MenuItem(label='About')
    about_menu_item.connect('activate', callbacks.about_menu_item_activate)
    menu.append(about_menu_item)

    quit_menu_item = gtk.MenuItem(label='Quit')
    quit_menu_item.connect('activate', callbacks.quit_menu_item_activate)
    menu.append(quit_menu_item)

    menu.show_all()


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
    menu_item = gtk.CheckMenuItem(label=device.name)
    menu_item.set_active(device.enabled)
    menu_item.device = device
    menu_item.connect('toggled', callback)
    return menu_item


class MenuCallbacks:

    def __init__(self, xinput, menu, about_dialog):
        self.xinput = xinput
        self.menu = menu
        self.about_dialog = about_dialog

    def child_device_check_menu_item_toggled(self, check_menu_item):
        """
        Callback to enable or disable a device when its `gtk.CheckMenuItem` is
        clicked.

        It should receive a `XInput`-like object as argument:

        >>> from inputdeviceindicator.mock import MockXInput, MockAboutDialog
        >>> mcs = MenuCallbacks(
        ...     MockXInput(), gtk.Menu(), MockAboutDialog()
        ... )

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

    def about_menu_item_activate(self, menu_item):
        """
        Open the "About" dialog.

        >>> from inputdeviceindicator.mock import MockXInput, MockAboutDialog
        >>> callbacks = MenuCallbacks(
        ...     MockXInput(), gtk.Menu(), MockAboutDialog()
        ... )

        It should display the dialog given to the constructor:

        >>> from inelegant.module import temp_var
        >>> callbacks.about_menu_item_activate(None)
        about dialog displayed
        """
        self.about_dialog.run()
        self.about_dialog.hide()

    def quit_menu_item_activate(self, menu_item):
        """
        Callback for quitting the application.

        >>> from inputdeviceindicator.mock import MockXInput, MockAboutDialog
        >>> callbacks = MenuCallbacks(
        ...     MockXInput(), gtk.Menu(), MockAboutDialog()
        ... )

        It should do it by calling `gtk.main_quit()`:

        >>> from inelegant.module import temp_var
        >>> with temp_var(gtk, 'main_quit', lambda: print('quit called')):
        ...     callbacks.quit_menu_item_activate(None)
        quit called
        """
        gtk.main_quit()

    def refresh_menu_item_activate(self, menu_item):
        """
        Refresh the menu by calling `xinput` again and regenerating all device
        items in the menu.

        Consider the following menu...

        >>> from inputdeviceindicator.command import parse
        >>> old_devices = parse('''
        ... ⎡ A        id=2    [master pointer  (3)]
        ... ⎜   ↳ A1   id=4    [slave  pointer  (2)]
        ... ⎣ B        id=3    [master keyboard (2)]
        ...     ↳ B1   id=5    [slave  keyboard (3)]
        ...         This device is disabled
        ... ''')
        >>> from inputdeviceindicator.mock import MockMenuCallbacks
        >>> callbacks = MockMenuCallbacks()
        >>> menu = gtk.Menu()
        >>> build_menu(menu, old_devices, callbacks)

        ...and the following `XInput`:

        >>> from inputdeviceindicator import mock
        >>> new_devices = parse('''
        ... ⎡ X        id=10    [master pointer  (9)]
        ... ⎜   ↳ X1   id=11    [slave  pointer  (10)]
        ... ⎣ Y        id=12    [master keyboard (8)]
        ...     ↳ Y1   id=13    [slave  keyboard (12)]
        ...         This device is disabled
        ... ''')
        >>> xinput = mock.MockXInput(new_devices)

        The menu will of course have the old options listed:

        >>> items = menu.get_children()
        >>> items[0].get_label()
        'A'
        >>> items[1].get_label()
        'A1'
        >>> items[2].get_label()
        'B'
        >>> items[3].get_label()
        'B1'

        Also, the antepenultimante item should be a "Refresh" option:

        >>> menu_item = items[-3]
        >>> menu_item.get_label()
        'Refresh'

        Now, if we call `MenuCallbacks.refresh_menu_item_activate()` giving the
        menu item (and the xinput to `MenuCallback` constructor)...

        >>> from inputdeviceindicator.mock import MockXInput, MockAboutDialog
        >>> callbacks = MenuCallbacks(xinput, menu, MockAboutDialog())
        >>> callbacks.refresh_menu_item_activate(menu_item)

        ...the device menu items should be updated:

        >>> items = menu.get_children()
        >>> items[0].get_label()
        'X'
        >>> items[1].get_label()
        'X1'
        >>> items[2].get_label()
        'Y'
        >>> items[3].get_label()
        'Y1'
        >>> items[3].get_active()
        False
        """
        build_menu(self.menu, self.xinput.list(), self)
