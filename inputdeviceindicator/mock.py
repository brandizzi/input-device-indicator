#!/usr/bin/env python

def noop(*args, **kwargs):
    pass


class MockXInput:

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
