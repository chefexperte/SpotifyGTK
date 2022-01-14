import gi

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


def on_activate(appl):
    win = Gtk.ApplicationWindow(application=appl)

    builder = Gtk.Builder()
    builder.add_from_file("spotify.ui")

    win = builder.get_object('window')

    # Configure interface
    win.connect('close-request', lambda x, y: Gtk.main_quit())

    win.set_property("title", "Spotify")
    win.present()


app = Gtk.Application(application_id='de.flxtea.spotify')
app.connect('activate', on_activate)

app.run(None)
