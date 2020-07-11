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

def noop(*args, **kwargs):
    pass


class MockXInput:

    def __init__(self, devices=None):
        self.devices = devices if devices is not None else []

    def list(self):
        return self.devices

    def enable(self, device):
        print('Device {0} enabled'.format(device.name))

    def disable(self, device):
        print('Device {0} disabled'.format(device.name))


class MockMenuCallbacks:

    def child_device_check_menu_item_toggled(self, check_menu_item):
        print(
            'Device {0} toggled to {1}'.format(
                check_menu_item.device.name, check_menu_item.get_active()
            )
        )

    def refresh_menu_item_activate(self, menu_item, menu):
        print('Refresh menu item activated')

    def about_menu_item_activate(self, menu_item, menu):
        print('about menu item activated')

    def quit_menu_item_activate(self, menu_item):
        print('Quit menu item activated')


class MockAboutDialog:

    def run(self):
        print('about dialog displayed')

    def hide(self):
        pass
