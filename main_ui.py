import os

import gi

from thread_tools.delayed_thread import DelayedThread

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw


class SpotifyGtkUI:
    play_button: Gtk.Button = None
    position_slider: Gtk.Scale = None
    loudness_slider: Gtk.Scale = None
    callbacks: [()] = None
    volume_change_delay: DelayedThread = None
    position_change_delay: DelayedThread = None
    track_duration: int = None

    def __init__(self):
        self.file_dir = os.path.dirname(os.path.abspath(__file__))
        self.app = Adw.Application(application_id='de.flxtea.spotify')
        man = Adw.StyleManager.get_default()
        man.set_color_scheme(Adw.ColorScheme.PREFER_DARK)

    def on_activate(self, appl):
        global css_provider
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(self.file_dir + "/style.css")
        win = Adw.ApplicationWindow(application=appl)
        win.css_provider = css_provider
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        headerbar = Gtk.HeaderBar()
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
        player_controls = Gtk.Box()
        player_controls.add_css_class("linked")
        previous_button = Gtk.Button(icon_name="media-skip-backward-symbolic")
        self.play_button = Gtk.Button(icon_name="media-playback-pause-symbolic")
        self.play_button.connect("clicked", self.callbacks["toggle_play"])
        self.play_button.set_sensitive(False)
        skip_button = Gtk.Button(icon_name="media-skip-forward-symbolic")
        player_controls.append(previous_button)
        player_controls.append(self.play_button)
        player_controls.append(skip_button)
        player_box.append(player_controls)
        self.position_slider = Gtk.Scale()
        self.position_slider.set_range(0, 100)
        self.position_slider.set_hexpand(True)
        self.position_slider.set_value(0)
        self.position_slider.connect("change-value", lambda a, b, c: self.position_change())
        player_box.append(self.position_slider)
        volume_button_box = Gtk.EventControllerMotion()
        volume_button = Gtk.Button(icon_name="audio-volume-high")
        context = volume_button.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        volume_button.add_controller(volume_button_box)
        volume_button.add_css_class("circular")
        volume_button.add_css_class("fadeout")
        volume_button.set_vexpand(False)
        volume_button.set_can_focus(False)
        fixed = Gtk.Fixed()
        fixed.set_valign(Gtk.Align.CENTER)
        self.loudness_slider = Gtk.Scale()
        self.loudness_slider.set_inverted(True)
        self.loudness_slider.set_range(0, 100)
        self.loudness_slider.set_hexpand(False)
        self.loudness_slider.set_value(100)
        self.loudness_slider.add_css_class("fadein")
        self.loudness_slider.connect("value-changed", lambda a: self.volume_change())
        volume_button_box.connect("enter", lambda a, b, c: fade_in(fixed, volume_button, self.loudness_slider))
        volume_button_box.connect("leave", lambda a: fade_out(fixed, volume_button, self.loudness_slider))
        # fixed.put(loudness_slider, 0, 0)
        # fixed.put(volume_button, 0, 0)
        # player_box.append(fixed)
        player_box.append(self.loudness_slider)
        main_box.append(headerbar)
        main_box.append(upper_box)
        main_box.append(player_box)
        # win.set_child(main_box)
        win.set_content(main_box)

        add_styling(main_box)

        win.connect("close-request", lambda x: win.destroy())
        win.set_title("SpotifyGTK")
        win.present()

    def backend_ready_callback(self):
        self.play_button.set_sensitive(True)

    def report_state_callback(self, position: int, duration: int):
        self.track_duration = duration
        percent = (position / duration) * 100
        if not self.position_change_delay or not self.position_change_delay.is_running():
            self.position_slider.set_value(percent)

    def position_change(self):
        if self.position_change_delay is not None and self.position_change_delay.is_running():
            # self.volume_change_delay.reset_timer()
            self.position_change_delay.args = [self.position_slider.get_value() / 100 * self.track_duration]
        else:
            self.position_change_delay = \
                DelayedThread(self.callbacks["set_position"],
                              [self.position_slider.get_value() / 100 * self.track_duration], 300)

    def volume_change(self):
        if self.volume_change_delay is not None and self.volume_change_delay.is_running():
            # self.volume_change_delay.reset_timer()
            self.volume_change_delay.args = [self.loudness_slider.get_value()]
        else:
            self.volume_change_delay = \
                DelayedThread(self.callbacks["set_volume"], [self.loudness_slider.get_value()], 200)

    def run_ui(self, callbacks):
        self.callbacks = callbacks
        self.app.connect('activate', self.on_activate)
        try:
            self.app.run(None)
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


def add_styling(widget):
    global css_provider
    for widget in widget:
        context = widget.get_style_context()
        context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        add_styling(widget)
