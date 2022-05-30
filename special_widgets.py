import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk


class ArtistButton(Gtk.Button):
	data_id: str = ""
