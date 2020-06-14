#!/usr/bin/env python

def noop(*args, **kwargs):
    pass

class MockXInput:

    def enable(self, device):
        print('Device {0} enabled'.format(device.name))

    def disable(self, device):
        print('Device {0} disabled'.format(device.name))
