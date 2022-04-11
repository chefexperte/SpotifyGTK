
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw


class SpotifyGTK:
    def __init__(self):
        app = Adw.Application(application_id='de.flxtea.spotify')
        man = Adw.StyleManager.get_default()
        man.set_color_scheme(Adw.ColorScheme.PREFER_DARK)
        app.connect('activate', on_activate)
        try:
            app.run(None)
        except KeyboardInterrupt:
            pass


def fade_in(container, button, slider):
    pass
    # container.remove(button)
    # container.put(slider, 0, 0)


def fade_out(container, button, slider):
    pass
    # container.remove(slider)
    # container.put(button, 0, 0)


css_provider = None


def on_activate(appl):
    global css_provider
    css_provider = Gtk.CssProvider()
    data = b"""
    .fish {
        color: white;
    }
    fadeout:hover {
        color: green;
        background-color: green;
    }
    .fadeout:hover {
        color: green;
        background-color: green;
    }
    #fadeout:hover {
        color: green;
        background-color: green;
    }
    """
    # css_provider.load_from_data(data)
    css_provider.load_from_path("style.css")
    win = Adw.ApplicationWindow(application=appl)
    win.css_provider = css_provider
    # context = win.get_style_context()
    # context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
    main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    # main_box.add_css_class("osd")
    headerbar = Gtk.HeaderBar()
    # win.set_titlebar(headerbar)
    # headerbar.add_css_class("osd")
    # main_box.set_valign(Gtk.Align.CENTER)
    upper_box = Gtk.Box()
    upper_box.append(Gtk.Label(label="UPPER"))
    player_box = Gtk.Box()
    player_box.add_css_class("toolbar")
    player_box.add_css_class("osd")
    player_box.set_vexpand(True)
    player_box.set_valign(Gtk.Align.END)
    player_box.set_margin_bottom(15)
    player_box.set_margin_start(15)
    player_box.set_margin_end(15)
    player_box.set_margin_top(15)
    player_box.set_size_request(500, 0)
    # player_box.append(Gtk.Label(label="PLAYER"))
    player_controls = Gtk.Box()
    player_controls.add_css_class("linked")
    previous_button = Gtk.Button(icon_name="media-skip-backward-symbolic")
    play_button = Gtk.Button(icon_name="media-playback-pause-symbolic")
    skip_button = Gtk.Button(icon_name="media-skip-forward-symbolic")
    player_controls.append(previous_button)
    player_controls.append(play_button)
    player_controls.append(skip_button)
    player_box.append(player_controls)
    scale = Gtk.Scale()
    scale.set_range(0, 100)
    scale.set_hexpand(True)
    scale.set_value(80)
    player_box.append(scale)
    volume_button_box = Gtk.EventControllerMotion()
    volume_button = Gtk.Button(icon_name="audio-volume-high")
    context = volume_button.get_style_context()
    context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
    volume_button.add_controller(volume_button_box)
    volume_button.add_css_class("circular")
    # volume_button.add_css_class("background")
    volume_button.add_css_class("fadeout")
    volume_button.set_vexpand(False)
    volume_button.set_can_focus(False)
    fixed = Gtk.Fixed()
    fixed.set_valign(Gtk.Align.CENTER)
    loudness_slider = Gtk.Scale()
    loudness_slider.set_inverted(True)
    loudness_slider.set_range(0, 100)
    loudness_slider.set_hexpand(False)
    loudness_slider.set_value(100)
    # loudness_slider.set_property("opacity", 0.1)
    loudness_slider.add_css_class("fadein")
    volume_button_box.connect("enter", lambda a, b, c: fade_in(fixed, volume_button, loudness_slider))
    volume_button_box.connect("leave", lambda a: fade_out(fixed, volume_button, loudness_slider))
    # fixed.put(loudness_slider, 0, 0)
    # fixed.put(volume_button, 0, 0)
    # player_box.append(fixed)
    player_box.append(loudness_slider)
    main_box.append(headerbar)
    main_box.append(upper_box)
    main_box.append(player_box)
    # win.set_child(main_box)
    win.set_content(main_box)

    add_styling(main_box)

    win.connect("close-request", lambda x: win.destroy())
    win.set_title("SpotifyGTK")
    win.present()


def add_styling(widget):
    global css_provider
    for widget in widget:
        context = widget.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        add_styling(widget)


if __name__ == "__main__":
    window = SpotifyGTK()
