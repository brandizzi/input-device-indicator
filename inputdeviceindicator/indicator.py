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
from gi.repository import AppIndicator3 as appindicator

from inputdeviceindicator.menu import get_menu
from inputdeviceindicator.info import get_icon_path


def get_indicator():
    return build_indicator(get_menu())


def build_indicator(menu):
    indicator = appindicator.Indicator.new(
        'input-device-indicator', get_icon_path(),
        appindicator.IndicatorCategory.SYSTEM_SERVICES
    )
    indicator.set_menu(menu)
    return indicator
