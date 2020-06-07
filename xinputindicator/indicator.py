import gi
gi.require_version('Gtk', '3.0')  # noqa
gi.require_version('AppIndicator3', '0.1')  # noqa

from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator

import os.path

from xinputindicator.command import XInput


class Application:

    def __init__(self):
        self.xinput = XInput()
        self.menu = build_menu(self.xinput.list())
        self.indicator = build_indicator(self.menu)

    def main(self):
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        gtk.main()


def build_indicator(menu):
    indicator = appindicator.Indicator.new(
        'xinput-indicator', os.path.abspath('resources/icon.png'),
        appindicator.IndicatorCategory.SYSTEM_SERVICES
    )
    indicator.set_menu(menu)
    return indicator


def build_menu(devices):
    """ Build a menu from a list of devices. Let's suppose we have the
    following devices, for example:

    >>> from xinputindicator.command import parse
    >>> devices = parse('''
    ... ⎡ A        id=2    [master pointer  (3)]
    ... ⎜   ↳ A1   id=4    [slave  pointer  (2)]
    ... ⎣ B        id=3    [master keyboard (2)]
    ...     ↳ B1   id=5    [slave  keyboard (3)]
    ... ''')
    >>> devices
    [Device(2, 'A', 3, 'master', 'pointer', True, \
[Device(4, 'A1', 2, 'slave', 'pointer', True)]), \
Device(3, 'B', 2, 'master', 'keyboard', True, \
[Device(5, 'B1', 3, 'slave', 'keyboard', True)])]

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
    """

    menu = gtk.Menu()
    for d in devices:
        menu.append(gtk.MenuItem(d.name))
        for c in d.children:
            menu.append(gtk.MenuItem(c.name))
    menu.show_all()
    return menu


if __name__ == "__main__":
    application = Application()
    application.main()
