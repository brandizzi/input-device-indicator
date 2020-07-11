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
from gi.repository import GdkPixbuf as gdkpb

from inputdeviceindicator.info import PROGRAM_NAME, VERSION, DESCRIPTION,\
    ICON_PATH, URL, AUTHOR, COPYRIGHT, EMAIL, LICENSE


def get_about_dialog():
    dialog = gtk.AboutDialog()
    dialog.set_program_name(PROGRAM_NAME)
    dialog.set_version(VERSION)
    dialog.set_comments(DESCRIPTION)
    pixbuf = gdkpb.Pixbuf.new_from_file(ICON_PATH)
    dialog.set_logo(pixbuf)
    dialog.set_icon(pixbuf)
    dialog.set_website(URL)
    authors = [
        "{name} <{email}>".format(name=AUTHOR, email=EMAIL)
    ]
    dialog.set_authors(authors)
    dialog.set_copyright(COPYRIGHT)
    dialog.set_license(LICENSE)
    return dialog
